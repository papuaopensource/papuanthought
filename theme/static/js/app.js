/*
 * Shared front-end behaviour for Papuan Thought.
 * Loaded (deferred) before Alpine, so the components below are
 * registered on `alpine:init`.
 */
(function () {
  "use strict";

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : "";
  }

  function isAuthenticated() {
    return document.body.dataset.auth === "true";
  }

  /* Send anonymous visitors to the login page, then back here. */
  function requireAuth() {
    if (isAuthenticated()) return true;
    var next = window.location.pathname + window.location.search;
    window.location.href = (document.body.dataset.loginUrl || "/login/") + "?next=" + encodeURIComponent(next);
    return false;
  }

  async function postJSON(url, body) {
    var res = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": csrfToken(),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: body ? new URLSearchParams(body).toString() : "",
    });
    if (!res.ok || res.redirected) throw new Error("Request failed: " + res.status);
    return res.json();
  }

  function toast(message) {
    if (window.Alpine) window.Alpine.store("toast").show(message);
  }

  async function copyText(text, message) {
    try {
      await navigator.clipboard.writeText(text);
    } catch (e) {
      var area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      document.execCommand("copy");
      area.remove();
    }
    toast(message || "Link copied");
  }

  function absoluteUrl(path) {
    return new URL(path || window.location.pathname, window.location.origin).href;
  }

  /* Scroll to the paragraph of the essay a comment quotes, and flash it. */
  function scrollToQuote(text) {
    var body = document.getElementById("essay-body");
    if (!body || !text) return;
    var needle = text.trim().substring(0, 80).toLowerCase();
    var nodes = body.querySelectorAll("p, li, blockquote, h1, h2, h3, h4, h5, h6");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.textContent.toLowerCase().indexOf(needle) !== -1) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.classList.add("quote-flash");
        setTimeout(function () { el.classList.remove("quote-flash"); }, 2400);
        return;
      }
    }
    body.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* Like / share on an essay (feed cards and the detail page). */
  function essayActions(cfg) {
    return {
      hearted: !!cfg.hearted,
      hearts: cfg.hearts || 0,
      busy: false,

      async toggleHeart() {
        if (!requireAuth() || this.busy) return;
        this.busy = true;
        try {
          var data = await postJSON(cfg.reactUrl, { reaction_type: "heart" });
          if (data.reacted !== this.hearted) this.hearts += data.reacted ? 1 : -1;
          this.hearted = data.reacted;
        } catch (e) {
          toast("Something went wrong. Try again.");
        } finally {
          this.busy = false;
        }
      },

      share() {
        var url = absoluteUrl(cfg.url);
        if (navigator.share && window.matchMedia("(pointer: coarse)").matches) {
          navigator.share({ title: cfg.title || document.title, url: url }).catch(function () {});
          return;
        }
        copyText(url);
      },

      shareTo(network) {
        var url = absoluteUrl(cfg.url);
        var title = cfg.title || document.title;
        var target =
          network === "whatsapp"
            ? "https://wa.me/?text=" + encodeURIComponent(title + " " + url)
            : "https://twitter.com/intent/tweet?text=" + encodeURIComponent(title) + "&url=" + encodeURIComponent(url);
        window.open(target, "_blank", "noopener");
      },

      copyLink() {
        copyText(absoluteUrl(cfg.url));
      },
    };
  }

  /* Essay detail page: actions + quoting a selection into the reply box. */
  function essayPage(cfg) {
    return Object.assign(essayActions(cfg), {
      isPublic: !!cfg.isPublic,
      composerOpen: false,
      quoteText: "",
      popover: { show: false, x: 0, y: 0 },
      confirmEssayDelete: false,
      confirmDelete: false,
      deleteTarget: "",

      init() {
        var self = this;
        var body = document.getElementById("essay-body");
        if (!body) return;
        var onSelect = function () {
          var sel = window.getSelection();
          var text = sel ? sel.toString().trim() : "";
          if (text && sel.rangeCount && body.contains(sel.anchorNode)) {
            var rect = sel.getRangeAt(0).getBoundingClientRect();
            self.quoteText = text;
            self.popover = { show: true, x: rect.left + rect.width / 2, y: Math.max(8, rect.top - 48) };
          } else {
            self.popover.show = false;
          }
        };
        body.addEventListener("mouseup", onSelect);
        body.addEventListener("touchend", function () { setTimeout(onSelect, 0); });
        document.addEventListener("mousedown", function (e) {
          var pop = document.getElementById("quote-popover");
          if (pop && !pop.contains(e.target)) self.popover.show = false;
        });
        window.addEventListener("scroll", function () { self.popover.show = false; }, { passive: true });
      },

      openComposer() {
        this.composerOpen = true;
        this.$nextTick(function () {
          var el = document.getElementById("main-comment-textarea");
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
            el.focus({ preventScroll: true });
          }
        });
      },

      quoteSelection() {
        this.popover.show = false;
        if (!requireAuth()) return;
        this.openComposer();
      },

      openDelete(url) {
        this.deleteTarget = url;
        this.confirmDelete = true;
      },

      /* Author only: share the article with everyone, or make it members-only again. */
      async setPublic(value) {
        try {
          var res = await fetch(cfg.visibilityUrl, {
            method: "POST",
            credentials: "same-origin",
            headers: {
              "X-CSRFToken": csrfToken(),
              "X-Requested-With": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({ public: value ? "1" : "0" }).toString(),
          });
          var data = await res.json().catch(function () { return {}; });
          if (!res.ok) {
            toast(data.error || "Something went wrong. Try again.");
            return;
          }
          this.isPublic = data.is_public;
          if (data.is_public) {
            copyText(absoluteUrl(cfg.url), "Now public · link copied");
          } else {
            toast("Members-only again. The public link no longer works.");
          }
        } catch (e) {
          toast("Something went wrong. Try again.");
        }
      },
    });
  }

  document.addEventListener("alpine:init", function () {
    var Alpine = window.Alpine;

    Alpine.store("toast", {
      message: "",
      visible: false,
      timer: null,
      show(message) {
        this.message = message;
        this.visible = true;
        clearTimeout(this.timer);
        var self = this;
        this.timer = setTimeout(function () { self.visible = false; }, 2400);
      },
    });

    Alpine.store("theme", {
      value: document.documentElement.getAttribute("data-theme") || "dark",
      toggle() {
        this.set(this.value === "dark" ? "light" : "dark");
      },
      set(value) {
        this.value = value;
        document.documentElement.setAttribute("data-theme", value);
        try { localStorage.setItem("theme", value); } catch (e) {}
      },
    });

    Alpine.data("essayActions", essayActions);
    Alpine.data("essayPage", essayPage);

    Alpine.data("followButton", function (cfg) {
      return {
        following: !!cfg.following,
        busy: false,
        async toggle() {
          if (!requireAuth() || this.busy) return;
          this.busy = true;
          try {
            var data = await postJSON(cfg.url);
            this.following = data.following;
            window.dispatchEvent(
              new CustomEvent("follow-changed", { detail: { username: cfg.username, following: data.following } })
            );
            toast(data.following ? "Following " + cfg.name : "Unfollowed " + cfg.name);
          } catch (e) {
            toast("Something went wrong. Try again.");
          } finally {
            this.busy = false;
          }
        },
        sync(detail) {
          if (detail.username === cfg.username) this.following = detail.following;
        },
      };
    });

    /*
     * Report dialog. Open it with $dispatch('open-report', key) or, when one dialog
     * serves many items (comments), $dispatch('open-report', { key, url, subject }).
     */
    Alpine.data("reportDialog", function (cfg) {
      return {
        open: false,
        url: cfg.url,
        subject: cfg.subject,
        reason: "",
        details: "",
        busy: false,
        error: "",
        handle(detail) {
          var key = typeof detail === "string" ? detail : detail && detail.key;
          if (key !== cfg.key) return;
          this.url = (detail && detail.url) || cfg.url;
          this.subject = (detail && detail.subject) || cfg.subject;
          this.show();
        },
        show() {
          this.reason = "";
          this.details = "";
          this.error = "";
          this.open = true;
        },
        async submit() {
          if (this.busy) return;
          if (!this.reason) {
            this.error = "Choose a reason.";
            return;
          }
          this.busy = true;
          this.error = "";
          try {
            var res = await fetch(this.url, {
              method: "POST",
              credentials: "same-origin",
              headers: {
                "X-CSRFToken": csrfToken(),
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded",
              },
              body: new URLSearchParams({ reason: this.reason, details: this.details }).toString(),
            });
            var data = await res.json().catch(function () { return {}; });
            if (!res.ok || !data.ok) {
              this.error = data.error || "Something went wrong. Try again.";
              return;
            }
            this.open = false;
            toast("Thanks. Your report was sent to the admins.");
          } catch (e) {
            this.error = "Something went wrong. Try again.";
          } finally {
            this.busy = false;
          }
        },
      };
    });

    /* Article editor: cover image picker with local preview. */
    Alpine.data("coverPicker", function (cfg) {
      return {
        preview: cfg.url || "",
        removed: false,
        error: "",
        pick(event) {
          var file = event.target.files && event.target.files[0];
          if (!file) return;
          if (file.size > 5 * 1024 * 1024) {
            this.error = "Images can be up to 5 MB.";
            event.target.value = "";
            return;
          }
          this.error = "";
          this.removed = false;
          this.preview = URL.createObjectURL(file);
        },
        clear() {
          this.$refs.file.value = "";
          this.preview = "";
          this.removed = true;
        },
      };
    });

    Alpine.data("commentLike", function (cfg) {
      return {
        liked: !!cfg.liked,
        likes: cfg.likes || 0,
        async toggleLike() {
          if (!requireAuth()) return;
          try {
            var data = await postJSON(cfg.url);
            this.liked = data.liked;
            this.likes = data.count;
          } catch (e) {
            toast("Something went wrong. Try again.");
          }
        },
      };
    });
  });

  window.PT = { copyText: copyText, toast: toast, absoluteUrl: absoluteUrl };
  window.scrollToQuote = scrollToQuote;
})();

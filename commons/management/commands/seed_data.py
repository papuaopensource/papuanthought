"""
Seed sample data for all app contexts:
  accounts     — users + profiles (with generated avatar photos)
  essays       — articles (cover + an image in the body) with tags, and short notes
  interactions — comments, reactions (likes), follows
"""

import io
import math
import random
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify


USERS = [
    {
        "username": "yohannes",
        "email": "yohannes@example.com",
        "password": "samplepass123",
        "first_name": "Yohannes",
        "last_name": "Waromi",
        "profile": {
            "bio": "Writer from Manokwari. Interested in oral history and cultural preservation.",
            "location": "Manokwari, West Papua",
            "twitter": "yohanneswaromi",
        },
    },
    {
        "username": "magdalena",
        "email": "magdalena@example.com",
        "password": "samplepass123",
        "first_name": "Magdalena",
        "last_name": "Rumbiak",
        "profile": {
            "bio": "Educator and essayist. Writing about identity and the future of Papuan youth.",
            "location": "Jayapura, Papua",
            "instagram": "magdalena.rumbiak",
        },
    },
    {
        "username": "aleksander",
        "email": "aleksander@example.com",
        "password": "samplepass123",
        "first_name": "Aleksander",
        "last_name": "Mote",
        "profile": {
            "bio": "Open source contributor and tech enthusiast from Papua Open Source community.",
            "location": "Sorong, West Papua",
            "website": "https://papuaopensource.org",
        },
    },
    {
        "username": "natalin",
        "email": "natalin@example.com",
        "password": "samplepass123",
        "first_name": "Natalin",
        "last_name": "Ayomi",
        "profile": {
            "bio": "Poet and short story writer. Loves the forest and the sea equally.",
            "location": "Biak, Papua",
        },
    },
]

ESSAYS = [
    {
        "author": "yohannes",
        "title": "The Stories My Grandmother Never Wrote Down",
        "excerpt": "Oral tradition is not a lesser form of knowledge. It is a living archive — one that breathes, adapts, and survives.",
        "content": """My grandmother could not read or write. But she knew every name of every tree in the forest behind our village. She knew which roots healed fever, which leaves treated wounds, and which plants were never to be touched.

She carried an entire library inside her — a library that no institution had catalogued, no university had studied, and no government had considered worth preserving.

When she died, I realized: we do not have a word for what was lost.

---

Oral tradition is not a lesser form of knowledge. It is a living archive — one that breathes, adapts, and survives through human memory and community practice. The written word freezes knowledge in a single moment. The spoken word allows knowledge to travel across generations, carrying context, emotion, and nuance that paper cannot hold.

In Papua, this distinction matters enormously. Hundreds of local languages. Thousands of stories. Generations of ecological knowledge about forests, rivers, and coastlines that sustained communities long before any outsider arrived.

---

What does it mean to preserve something that was never meant to be preserved — only lived?

I do not think the answer is to simply digitize everything, to record grandmothers on video and upload them to cloud servers. That approach treats oral tradition as a static artifact, not a living practice.

The answer, I think, is to create spaces — digital and physical — where these traditions can continue to breathe. Where young Papuans can encounter the stories of their grandmothers not as museum pieces, but as living, relevant knowledge.

That is what this platform is trying to be. Not an archive. A living network.

My grandmother never wrote anything down. But I am writing this — and perhaps that is enough to begin.""",
        "tags": ["oral-history", "memory", "tradition"],
        "status": "published",
        "is_featured": True,
    },
    {
        "author": "magdalena",
        "title": "What Language Are You Thinking In?",
        "excerpt": "When we lose a language, we do not just lose words. We lose an entire way of seeing the world.",
        "content": """A linguist once told me that the Dani language of the Baliem Valley has very few basic color terms. Two, in fact — one for dark, cool colors and one for bright, warm ones. For a long time, this was used as evidence that some languages were more "developed" than others.

What the linguist did not mention: Dani speakers can distinguish dozens of shades of green in a forest. Their color vocabulary is not impoverished — it is precisely calibrated to the environment they live in.

---

Language is not just a communication tool. It is a cognitive framework. When we lose a language, we do not just lose words. We lose an entire way of seeing the world — an entire set of distinctions, metaphors, and categories that make certain things visible and others invisible.

Papua is home to roughly 300 languages. Many of them have fewer than a thousand speakers. Some have fewer than a hundred. Linguists estimate that without active effort, a significant portion of these languages will be functionally extinct within two generations.

---

I grew up speaking Indonesian at school and Biak at home. When I dream, I dream in Biak. When I am angry, I think in Biak. When I want to say something true — something that touches the real shape of what I mean — I reach for Biak.

Indonesian is my working language. Biak is my thinking language.

I wonder, sometimes, what would happen if we built platforms like this one in Biak. Not translated from Indonesian — built natively, with Biak logic, Biak metaphors, Biak humor.

I do not know if it is possible. But I think it is worth trying.""",
        "tags": ["language", "identity", "reflection"],
        "status": "published",
        "is_featured": True,
    },
    {
        "author": "aleksander",
        "title": "Why Papua Needs Open Source",
        "excerpt": "Technology is not neutral. The tools we use shape what we can build — and who gets to build it.",
        "content": """When I first started contributing to open source software, I was doing it from a rented computer in a warnet in Sorong. The connection was slow. The electricity cut out twice. I had to re-upload my pull request three times.

But I kept going. Because for the first time, I was building something that belonged to everyone — including me.

---

Technology is not neutral. The tools we use shape what we can build — and who gets to build it.

Proprietary software is built on a model of scarcity: you pay for a license, you depend on a vendor, you lose access when the subscription ends. For communities with limited resources, this model is exclusionary by design.

Open source software is built on a different model: abundance, transparency, and shared ownership. Anyone can read the code, improve it, adapt it, and redistribute it. The knowledge is held in common.

---

Papua Open Source started as a small group of developers who wanted to build things together. We did not have funding. We did not have infrastructure. We had GitHub, an internet connection, and a belief that technology could serve our community — not extract from it.

Today, we are building platforms like this one. We are running workshops in Jayapura and Manokwari. We are trying to show that you do not need to leave Papua to build things that matter.

Open source is not just a software philosophy. It is a community philosophy. And in Papua — where knowledge has always been held in common, where stories belong to everyone, where the forest is not owned but shared — it feels like something we have always known.""",
        "tags": ["open-source", "community", "technology"],
        "status": "published",
        "is_featured": False,
    },
    {
        "author": "natalin",
        "title": "The Sea Remembers Everything",
        "excerpt": "Before there were GPS coordinates, there were stars and currents and the color of the water.",
        "content": """My father navigated by the stars.

Not metaphorically. Literally. Before he became a fisherman who used GPS and a cheap Android phone, he learned to read the sky, the currents, the color of the water, and the behavior of birds to know exactly where he was and where he was going.

He learned this from his father. His father learned it from his.

---

Before there were GPS coordinates, there were stars and currents and the color of the water. Before there were satellite maps, there were navigation traditions passed down through generations — knowledge systems sophisticated enough to cross hundreds of kilometers of open ocean without instruments.

The Biaks were seafarers. This is not mythology — it is history. Archaeological evidence places Papuan voyagers across the Pacific long before European contact. Our ancestors built canoes capable of oceanic travel and carried with them language, culture, and ecological knowledge that survived the crossing.

---

I think about this when I swim at Cendrawasih Bay. The water is warm and clear and full of life — manta rays, whale sharks, sea turtles moving through water their ancestors have moved through for millions of years.

The sea remembers everything that has passed through it. It holds the memory of every voyage, every storm, every child who ever learned to swim by watching their parents.

We are trying to build a different kind of sea — a digital one. One that can hold memory the same way: not as a static record, but as something alive, tidal, always moving.

I hope we are up to the task.""",
        "tags": ["sea", "memory", "tradition", "navigation"],
        "status": "published",
        "is_featured": True,
    },
    {
        "author": "magdalena",
        "title": "Draft: Notes on Education in a Forgotten Province",
        "excerpt": "What does it mean to be educated in a place where the curriculum was designed elsewhere?",
        "content": """[Draft — not ready for publication]

A few notes I want to develop:

The textbooks we used in school were written in Jakarta. The heroes in the stories were from Java. The geography lessons described mountains and rivers I had never seen. The math problems used rice paddies as examples in a place where nobody I knew grew rice.

What does it mean to be educated in a place where the curriculum was designed elsewhere?

I want to write about this more carefully. About the gap between official knowledge and local knowledge. About what gets counted as education and what gets dismissed as superstition or tradition.

More to come.""",
        "tags": ["education", "identity"],
        "status": "draft",
        "is_featured": False,
    },
]

COMMENTS = [
    {
        "essay_title": "The Stories My Grandmother Never Wrote Down",
        "author": "magdalena",
        "content": "This moved me deeply. My own grandmother was the same — an entire world of knowledge carried in her memory. Thank you for writing this.",
    },
    {
        "essay_title": "The Stories My Grandmother Never Wrote Down",
        "author": "aleksander",
        "content": "The distinction between archive and living network is exactly right. We should discuss how this platform can embody that principle technically as well.",
    },
    {
        "essay_title": "What Language Are You Thinking In?",
        "author": "yohannes",
        "content": "Dreaming in your mother tongue — yes. That is the truest test of where a language lives in you.",
    },
    {
        "essay_title": "Why Papua Needs Open Source",
        "author": "natalin",
        "content": "I love the parallel between open source philosophy and how knowledge has always been shared in Papuan communities. That connection deserves its own essay.",
    },
    {
        "essay_title": "The Sea Remembers Everything",
        "author": "yohannes",
        "content": "The image of a digital sea that holds memory the way the ocean does — I will be thinking about this for a long time.",
    },
    {
        "essay_title": "The Sea Remembers Everything",
        "author": "magdalena",
        "content": "My grandfather was also a seafarer. This essay made me want to record his stories before it is too late.",
    },
]

FOLLOWS = [
    ("magdalena", "yohannes"),
    ("aleksander", "yohannes"),
    ("natalin", "magdalena"),
    ("yohannes", "natalin"),
    ("aleksander", "magdalena"),
]

REACTIONS = [
    ("The Stories My Grandmother Never Wrote Down", "magdalena", "heart"),
    ("The Stories My Grandmother Never Wrote Down", "aleksander", "heart"),
    ("The Stories My Grandmother Never Wrote Down", "natalin", "heart"),
    ("What Language Are You Thinking In?", "yohannes", "heart"),
    ("Why Papua Needs Open Source", "yohannes", "heart"),
    ("Why Papua Needs Open Source", "natalin", "heart"),
    ("The Sea Remembers Everything", "yohannes", "heart"),
    ("The Sea Remembers Everything", "aleksander", "heart"),
    ("The Sea Remembers Everything", "magdalena", "heart"),
]

# Days before "now" that each seeded article was published, so the feed reads naturally.
ARTICLE_DAYS_AGO = {
    "The Stories My Grandmother Never Wrote Down": 9,
    "What Language Are You Thinking In?": 6,
    "Why Papua Needs Open Source": 4,
    "The Sea Remembers Everything": 2,
}

NOTES = [
    {
        "key": "biak-tide",
        "author": "natalin",
        "hours_ago": 3,
        "content": "Walked the beach in Biak before anyone else was awake. The tide wrote something in the sand and erased it before I could read it.\n\nSome poems are like that.",
    },
    {
        "key": "come-back",
        "author": "magdalena",
        "hours_ago": 7,
        "content": "Asked my students what they want to be in ten years. Half of them answered: “someone who comes back.”\n\nI have been thinking about that answer all evening.",
    },
    {
        "key": "2g-sync",
        "author": "aleksander",
        "hours_ago": 20,
        "content": "Small win today: offline-first sync finally works on a 2G connection in Sorong. If it works here, it works anywhere.\n\nThank you to everyone who sent a patch this month.",
    },
    {
        "key": "record-elders",
        "author": "yohannes",
        "hours_ago": 30,
        "content": "Reminder to myself and to anyone reading: record your elders this week. Not next year.\n\nThe phone in your pocket is enough to start an archive. Ask about place names, songs, who planted which tree. Write down the date. Keep the file somewhere safe.",
    },
    {
        "key": "names-of-wind",
        "author": "natalin",
        "hours_ago": 52,
        "content": "My father knows eleven names for the wind. Each one tells you something different: where the rain will come from, whether the fish will rise, when it is safe to cross.\n\nI asked him to teach me all of them. He laughed and said that you do not learn the wind from a list. You learn it by being wrong about it many times, on the water, with someone patient beside you.\n\nSo this week I am going out with him every morning. I will try to be wrong in the right way. I will write down what I can, but I suspect the most important parts will not fit on paper.\n\nIf you have elders who still read the weather like this, sit with them. Ask. Listen. It is a kind of library too.",
    },
]

NOTE_COMMENTS = [
    ("come-back", "yohannes", "That answer gives me hope. Coming back is its own kind of courage."),
    ("2g-sync", "natalin", "This is the kind of engineering that actually reaches people. Well done."),
    ("record-elders", "magdalena", "Doing this with my grandfather this Sunday. Thank you for the push."),
]

NOTE_REACTIONS = [
    ("biak-tide", "magdalena"),
    ("biak-tide", "yohannes"),
    ("come-back", "natalin"),
    ("come-back", "aleksander"),
    ("2g-sync", "yohannes"),
    ("record-elders", "natalin"),
    ("record-elders", "aleksander"),
    ("names-of-wind", "magdalena"),
]

# Soft colour palettes for generated avatars (background first).
AVATAR_PALETTES = [
    ["#0f3d3e", "#1f7a6d", "#7fd1b9", "#f2c14e"],  # forest and gold
    ["#13315c", "#1d70a2", "#6ac3d8", "#f6d7a7"],  # sea and sand
    ["#4a1942", "#c96442", "#f29e4c", "#ffe3b3"],  # dusk
    ["#2d3a1f", "#6b8e23", "#c5d86d", "#f4f1de"],  # highlands
    ["#3b2c54", "#7b5ea7", "#e0a1c5", "#fde2e4"],  # orchid
    ["#2b2d42", "#8d99ae", "#ef8354", "#edf2f4"],  # slate and ember
]


def generate_avatar(seed: str, palette: list[str], size: int = 320) -> bytes:
    """A soft, abstract 'marble' avatar: blurred colour blobs, deterministic per seed."""
    from PIL import Image, ImageDraw, ImageFilter

    rnd = random.Random(seed)
    canvas = Image.new("RGB", (size, size), palette[0])
    draw = ImageDraw.Draw(canvas)
    for color in palette[1:] + palette[1:2]:
        radius = rnd.randint(size // 4, size // 2)
        x, y = rnd.randint(0, size), rnd.randint(0, size)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    canvas = canvas.filter(ImageFilter.GaussianBlur(size // 7))
    buffer = io.BytesIO()
    canvas.save(buffer, format="JPEG", quality=88)
    return buffer.getvalue()


def set_avatar(profile, seed: str, palette: list[str]) -> None:
    """Replace the profile photo with a generated avatar (overwriting a previous seed file)."""
    name = f"profiles/seed-{slugify(seed)}.jpg"
    storage = profile.photo.storage
    if storage.exists(name):
        storage.delete(name)
    profile.photo.save(name.split("/", 1)[1], ContentFile(generate_avatar(seed, palette)), save=True)


# Generated illustrations for each seeded article: a cover and one image in the body.
ARTICLE_IMAGES = {
    "The Stories My Grandmother Never Wrote Down": {
        "cover": "dusk-mountains",
        "body": "forest",
        "caption": "The forest behind the village, where every tree had a name.",
    },
    "What Language Are You Thinking In?": {
        "cover": "morning-hills",
        "body": "dusk-mountains",
        "caption": "Hundreds of languages live between these valleys.",
    },
    "Why Papua Needs Open Source": {
        "cover": "network",
        "body": "morning-hills",
        "caption": "Connectivity is uneven; the tools we build should not assume otherwise.",
    },
    "The Sea Remembers Everything": {
        "cover": "sea-sunset",
        "body": "night-sea",
        "caption": "Before GPS, there were stars and currents.",
    },
}

SCENES = {
    "dusk-mountains": {"sky": ("#2b1e4a", "#f29e4c"), "sun": "#ffd38a", "sun_at": (0.68, 0.52),
                       "ridges": ["#5b3a5e", "#3b2c54", "#241a36", "#130d1f"]},
    "morning-hills": {"sky": ("#8ec5e6", "#fde7c8"), "sun": "#fff6dc", "sun_at": (0.24, 0.32),
                      "ridges": ["#9cc08a", "#6f9d63", "#4a7a49", "#2c5531"]},
    "forest": {"sky": ("#c9e4d6", "#f4efd9"), "sun": "#fffaf0", "sun_at": (0.8, 0.28),
               "ridges": ["#7aa58a", "#4f8064", "#2f5c45", "#173a2b"], "trees": True},
    "sea-sunset": {"sky": ("#13315c", "#f6a96b"), "sun": "#ffd59e", "sun_at": (0.5, 0.6),
                   "sea": ("#1d4e7a", "#0a2240")},
    "night-sea": {"sky": ("#040a1c", "#1a2c52"), "sun": "#f4f1de", "sun_at": (0.72, 0.26),
                  "sea": ("#0d1f3c", "#030c1c"), "stars": True},
    "network": {"sky": ("#0b1022", "#1b1f3b"), "network": True},
}


def _mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


def generate_illustration(scene_name: str, seed: str, size=(1600, 900)) -> bytes:
    """A simple flat landscape illustration (sky, sun, ridges or sea) as JPEG bytes."""
    from PIL import Image, ImageDraw, ImageFilter

    scene = SCENES[scene_name]
    rnd = random.Random(f"{scene_name}:{seed}")
    width, height = size
    image = Image.new("RGB", size)
    draw = ImageDraw.Draw(image)
    top, bottom = scene["sky"]
    for y in range(height):
        draw.line([(0, y), (width, y)], fill=_mix(top, bottom, y / (height - 1)))

    if scene.get("stars"):
        for _ in range(220):
            x, y, r = rnd.randint(0, width), rnd.randint(0, int(height * 0.6)), rnd.choice([1, 1, 2])
            draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 240))

    if scene.get("network"):
        nodes = [(rnd.randint(40, width - 40), rnd.randint(40, height - 40)) for _ in range(46)]
        for i, (x1, y1) in enumerate(nodes):
            for x2, y2 in nodes[i + 1:]:
                if math.hypot(x2 - x1, y2 - y1) < 260:
                    draw.line([(x1, y1), (x2, y2)], fill=(84, 120, 190), width=2)
        for x, y in nodes:
            r = rnd.choice([5, 7, 9])
            draw.ellipse((x - r * 2, y - r * 2, x + r * 2, y + r * 2), fill=(40, 58, 110))
            draw.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice([(217, 119, 87), (246, 215, 167), (140, 190, 255)]))
        image = image.filter(ImageFilter.GaussianBlur(0.8))
    else:
        sx, sy = scene["sun_at"]
        cx, cy, r = width * sx, height * sy, height * 0.11
        glow = _mix(scene["sun"], scene["sky"][1], 0.5)
        draw.ellipse((cx - r * 1.6, cy - r * 1.6, cx + r * 1.6, cy + r * 1.6), fill=glow)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=scene["sun"])
        image = image.filter(ImageFilter.GaussianBlur(6))
        draw = ImageDraw.Draw(image)

        if "sea" in scene:
            horizon = int(height * 0.64)
            sea_top, sea_bottom = scene["sea"]
            for y in range(horizon, height):
                draw.line([(0, y), (width, y)], fill=_mix(sea_top, sea_bottom, (y - horizon) / (height - horizon)))
            for _ in range(70):  # light on the water
                y = rnd.randint(horizon + 6, height - 10)
                half = rnd.randint(20, 140) * (1 - (y - horizon) / (height - horizon) * 0.5)
                x = cx + rnd.gauss(0, 90)
                draw.line([(x - half, y), (x + half, y)], fill=_mix(scene["sun"], sea_top, 0.35), width=2)

        for depth, color in enumerate(scene.get("ridges", [])):
            base = height * (0.5 + depth * 0.12)
            amplitude = height * (0.09 - depth * 0.012)
            phase, freq = rnd.uniform(0, 6.28), rnd.uniform(1.2, 2.4)
            points = [(0, height)]
            for x in range(0, width + 41, 40):
                y = base - amplitude * math.sin(phase + freq * x / width * math.pi) - rnd.uniform(0, amplitude * 0.35)
                points.append((x, y))
            points.append((width, height))
            draw.polygon(points, fill=color)
            if scene.get("trees") and depth >= 2:
                for _ in range(60):
                    x = rnd.randint(0, width)
                    y = base + rnd.uniform(-amplitude * 0.4, height * 0.08)
                    h = rnd.randint(40, 90)
                    draw.polygon([(x, y - h), (x - h * 0.28, y), (x + h * 0.28, y)], fill=color)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


def add_article_images(article, spec) -> None:
    """Give a freshly seeded article a cover and one captioned image after its first paragraph."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    from posts import images, services

    def upload(scene, label):
        data = generate_illustration(scene, f"{article.slug}-{label}")
        return SimpleUploadedFile(f"{label}.jpg", data, content_type="image/jpeg")

    services.set_cover(article, images.process_upload(upload(spec["cover"], "cover"), images.COVER_MAX_SIZE))
    body_image = services.save_body_image(article.author, upload(spec["body"], "body"))
    first, _, rest = article.content.partition("\n\n")
    block = f"![{spec['caption']}]({body_image.image.url})\n\n*{spec['caption']}*"
    article.content = f"{first}\n\n{block}\n\n{rest}" if rest else f"{first}\n\n{block}"
    article.save(update_fields=["content"])
    services.link_body_images(article)


class Command(BaseCommand):
    help = "Seed sample data: users, essays, tags, interactions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing data before seeding.",
        )

    def handle(self, *args, **options):
        from accounts.models import User, Profile
        from posts.models import Tag, Article
        from interactions.models import Comment, Reaction, Follow

        if options["flush"]:
            self.stdout.write("Flushing existing data...")
            from posts.models import ArticleImage

            for upload in ArticleImage.objects.all():
                upload.image.delete(save=False)
            for article in Article.objects.exclude(cover_image=""):
                article.cover_image.delete(save=False)
            Reaction.objects.all().delete()
            Follow.objects.all().delete()
            Comment.objects.all().delete()
            Article.objects.all().delete()
            Tag.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING("All non-superuser data deleted."))

        # ── Users + Profiles ─────────────────────────────────────────────────
        self.stdout.write("Seeding users...")
        user_map = {}
        for index, data in enumerate(USERS):
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            for field, value in data["profile"].items():
                setattr(profile, field, value)
            profile.save()
            set_avatar(profile, data["username"], AVATAR_PALETTES[index % len(AVATAR_PALETTES)])

            user_map[data["username"]] = user

        # Superusers are kept by --flush; give them an avatar too if theirs is missing.
        for offset, admin in enumerate(User.objects.filter(is_superuser=True)):
            profile, _ = Profile.objects.get_or_create(user=admin)
            if not (profile.photo and profile.photo.storage.exists(profile.photo.name)):
                set_avatar(profile, admin.username, AVATAR_PALETTES[(len(USERS) + offset) % len(AVATAR_PALETTES)])

        # ── Essays + Tags ─────────────────────────────────────────────────────
        self.stdout.write("Seeding essays...")
        essay_map = {}
        for data in ESSAYS:
            author = user_map[data["author"]]
            slug = slugify(data["title"])
            published_at = (
                timezone.now() - timedelta(days=ARTICLE_DAYS_AGO.get(data["title"], 1))
                if data["status"] == "published"
                else None
            )

            essay, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    "author": author,
                    "title": data["title"],
                    "excerpt": data["excerpt"],
                    "content": data["content"],
                    "status": data["status"],
                    "is_featured": data["is_featured"],
                    "published_at": published_at,
                },
            )
            if created:
                tags = []
                for name in data.get("tags", []):
                    tag, _ = Tag.objects.get_or_create(
                        slug=slugify(name), defaults={"name": name}
                    )
                    tags.append(tag)
                essay.tags.set(tags)
                if data["title"] in ARTICLE_IMAGES:
                    add_article_images(essay, ARTICLE_IMAGES[data["title"]])

            essay_map[data["title"]] = essay

        # ── Comments ─────────────────────────────────────────────────────────
        self.stdout.write("Seeding comments...")
        for data in COMMENTS:
            essay = essay_map.get(data["essay_title"])
            author = user_map[data["author"]]
            if essay and essay.status == Article.PUBLISHED:
                Comment.objects.get_or_create(
                    article=essay,
                    author=author,
                    content=data["content"],
                )

        # ── Reactions ────────────────────────────────────────────────────────
        self.stdout.write("Seeding reactions...")
        for essay_title, username, reaction_type in REACTIONS:
            essay = essay_map.get(essay_title)
            user = user_map.get(username)
            if essay and user and essay.status == Article.PUBLISHED:
                Reaction.objects.get_or_create(
                    article=essay,
                    user=user,
                    reaction_type=reaction_type,
                )

        # ── Notes ────────────────────────────────────────────────────────────
        self.stdout.write("Seeding notes...")
        note_map = {}
        for data in NOTES:
            note, _ = Article.objects.get_or_create(
                author=user_map[data["author"]],
                kind=Article.NOTE,
                content=data["content"],
                defaults={
                    "status": Article.PUBLISHED,
                    "published_at": timezone.now() - timedelta(hours=data["hours_ago"]),
                },
            )
            note_map[data["key"]] = note
        for key, username, content in NOTE_COMMENTS:
            Comment.objects.get_or_create(article=note_map[key], author=user_map[username], content=content)
        for key, username in NOTE_REACTIONS:
            Reaction.objects.get_or_create(article=note_map[key], user=user_map[username], reaction_type=Reaction.HEART)

        # ── Follows ──────────────────────────────────────────────────────────
        self.stdout.write("Seeding follows...")
        for follower_name, following_name in FOLLOWS:
            follower = user_map.get(follower_name)
            following = user_map.get(following_name)
            if follower and following:
                Follow.objects.get_or_create(follower=follower, following=following)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Seeded: "
            f"{len(USERS)} users (with avatars), {len(ESSAYS)} articles "
            f"({len(ARTICLE_IMAGES)} with cover + body image), {len(NOTES)} notes, "
            f"{len(COMMENTS) + len(NOTE_COMMENTS)} comments, {len(REACTIONS) + len(NOTE_REACTIONS)} likes, "
            f"{len(FOLLOWS)} follows."
        ))

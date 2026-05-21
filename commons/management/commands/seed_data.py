"""
Seed sample data for all app contexts:
  accounts     — users + profiles
  essays       — essays with user-defined tags
  interactions — comments, reactions, follows, bookmarks
"""

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

BOOKMARKS = [
    ("aleksander", "The Stories My Grandmother Never Wrote Down"),
    ("natalin", "What Language Are You Thinking In?"),
    ("magdalena", "Why Papua Needs Open Source"),
    ("yohannes", "The Sea Remembers Everything"),
]


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
        from essays.models import Tag, Essay
        from interactions.models import Comment, Reaction, Follow, Bookmark

        if options["flush"]:
            self.stdout.write("Flushing existing data...")
            Bookmark.objects.all().delete()
            Reaction.objects.all().delete()
            Follow.objects.all().delete()
            Comment.objects.all().delete()
            Essay.objects.all().delete()
            Tag.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING("All non-superuser data deleted."))

        # ── Users + Profiles ─────────────────────────────────────────────────
        self.stdout.write("Seeding users...")
        user_map = {}
        for data in USERS:
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

            user_map[data["username"]] = user

        # ── Essays + Tags ─────────────────────────────────────────────────────
        self.stdout.write("Seeding essays...")
        essay_map = {}
        for data in ESSAYS:
            author = user_map[data["author"]]
            slug = slugify(data["title"])
            published_at = timezone.now() if data["status"] == "published" else None

            essay, created = Essay.objects.get_or_create(
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

            essay_map[data["title"]] = essay

        # ── Comments ─────────────────────────────────────────────────────────
        self.stdout.write("Seeding comments...")
        for data in COMMENTS:
            essay = essay_map.get(data["essay_title"])
            author = user_map[data["author"]]
            if essay and essay.status == Essay.PUBLISHED:
                Comment.objects.get_or_create(
                    essay=essay,
                    author=author,
                    content=data["content"],
                )

        # ── Reactions ────────────────────────────────────────────────────────
        self.stdout.write("Seeding reactions...")
        for essay_title, username, reaction_type in REACTIONS:
            essay = essay_map.get(essay_title)
            user = user_map.get(username)
            if essay and user and essay.status == Essay.PUBLISHED:
                Reaction.objects.get_or_create(
                    essay=essay,
                    user=user,
                    reaction_type=reaction_type,
                )

        # ── Follows ──────────────────────────────────────────────────────────
        self.stdout.write("Seeding follows...")
        for follower_name, following_name in FOLLOWS:
            follower = user_map.get(follower_name)
            following = user_map.get(following_name)
            if follower and following:
                Follow.objects.get_or_create(follower=follower, following=following)

        # ── Bookmarks ────────────────────────────────────────────────────────
        self.stdout.write("Seeding bookmarks...")
        for username, essay_title in BOOKMARKS:
            user = user_map.get(username)
            essay = essay_map.get(essay_title)
            if user and essay and essay.status == Essay.PUBLISHED:
                Bookmark.objects.get_or_create(user=user, essay=essay)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Seeded: "
            f"{len(USERS)} users, {len(ESSAYS)} essays, "
            f"{len(COMMENTS)} comments, {len(REACTIONS)} reactions, "
            f"{len(FOLLOWS)} follows, {len(BOOKMARKS)} bookmarks."
        ))

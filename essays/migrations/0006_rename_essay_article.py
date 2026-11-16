from django.db import migrations


class Migration(migrations.Migration):
    """Rename the Essay model to Article. The table is renamed; no data changes."""

    dependencies = [
        ("essays", "0005_essay_kind_alter_essay_title"),
        # Rename only after the interactions migrations that create foreign keys
        # to "essays.essay" (0001-0004); later ones point at "essays.article".
        ("interactions", "0004_comment_is_edited_and_commentlike"),
    ]

    operations = [
        migrations.RenameModel(old_name="Essay", new_name="Article"),
        migrations.AlterModelOptions(
            name="article",
            options={
                "ordering": ["-published_at", "-created_at"],
                "verbose_name": "article",
                "verbose_name_plural": "articles",
            },
        ),
    ]

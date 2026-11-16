from django.db import migrations


class Migration(migrations.Migration):
    """Rename the Essay model to Article. The table is renamed; no data changes."""

    dependencies = [
        ("essays", "0005_essay_kind_alter_essay_title"),
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

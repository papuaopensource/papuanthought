from django.db import migrations, models


class Migration(migrations.Migration):
    """Rename the `essay` foreign keys to `article` (columns renamed; data kept)."""

    dependencies = [
        ("interactions", "0008_alter_comment_essay_alter_notification_essay_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(model_name="report", name="report_single_target"),
        migrations.RenameField(model_name="comment", old_name="essay", new_name="article"),
        migrations.RenameField(model_name="reaction", old_name="essay", new_name="article"),
        migrations.RenameField(model_name="notification", old_name="essay", new_name="article"),
        migrations.RenameField(model_name="report", old_name="essay", new_name="article"),
        migrations.AddConstraint(
            model_name="report",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(article__isnull=False, comment__isnull=True, reported_user__isnull=True)
                    | models.Q(article__isnull=True, comment__isnull=False, reported_user__isnull=True)
                    | models.Q(article__isnull=True, comment__isnull=True, reported_user__isnull=False)
                ),
                name="report_single_target",
            ),
        ),
    ]

from django.db import migrations


class Migration(migrations.Migration):
    """The contact form became the feedback form; keep existing messages."""

    dependencies = [
        ("commons", "0001_create_contact_message"),
    ]

    operations = [
        migrations.RenameModel(old_name="ContactMessage", new_name="Feedback"),
    ]

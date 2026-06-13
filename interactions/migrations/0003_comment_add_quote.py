from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactions', '0002_add_newpost_recommend_notification_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='quote',
            field=models.TextField(blank=True, null=True),
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("service_center", "0001_initial"),
        ("chatbox", "0002_alter_chatsession_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatsession",
            name="service_center",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="chat_sessions",
                to="service_center.servicecenter",
            ),
        ),
    ]

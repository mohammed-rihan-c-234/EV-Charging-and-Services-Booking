from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sos", "0003_assignedcenter"),
    ]

    operations = [
        migrations.AddField(
            model_name="sosalert",
            name="address",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]

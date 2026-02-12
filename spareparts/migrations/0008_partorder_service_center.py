from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("service_center", "0001_initial"),
        ("spareparts", "0007_partorder_reward_points"),
    ]

    operations = [
        migrations.AddField(
            model_name="partorder",
            name="service_center",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="part_orders",
                to="service_center.servicecenter",
            ),
        ),
    ]

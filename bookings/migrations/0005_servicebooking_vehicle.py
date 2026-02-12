from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0002_vehicle_owner"),
        ("bookings", "0004_servicebooking_razorpay_order_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicebooking",
            name="vehicle",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="service_bookings",
                to="vehicles.vehicle",
            ),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_servicebooking_amount_servicebooking_approval_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicebooking',
            name='coupon_discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]

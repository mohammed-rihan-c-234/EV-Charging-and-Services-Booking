from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spareparts', '0004_partorder_partorderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='partorder',
            name='coupon_discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]

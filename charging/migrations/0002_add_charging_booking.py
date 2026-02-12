from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('charging', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='chargingstation',
            name='price_per_hour',
            field=models.DecimalField(decimal_places=2, default=50.0, max_digits=8),
        ),
        migrations.CreateModel(
            name='ChargingBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration_hours', models.PositiveIntegerField(default=2)),
                ('scheduled_at', models.DateTimeField()),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('payment_status', models.CharField(choices=[('unpaid', 'Unpaid'), ('paid', 'Paid'), ('pending', 'Pending Payment')], default='unpaid', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='charging.chargingstation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='charging_bookings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

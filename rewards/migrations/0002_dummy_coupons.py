from django.db import migrations


def add_dummy_coupons(apps, schema_editor):
    Coupon = apps.get_model('rewards', 'Coupon')
    
    dummy_coupons = [
        {
            'code': 'SAVE10',
            'title': 'Save 10% Off',
            'description': 'Get 10% discount on any order',
            'discount_percent': 10,
            'active': True,
        },
        {
            'code': 'SAVE20',
            'title': 'Save 20% Off',
            'description': 'Get 20% discount on orders over ₹500',
            'discount_percent': 20,
            'active': True,
        },
        {
            'code': 'SAVE25',
            'title': 'Save 25% Off',
            'description': 'Special 25% discount for loyal customers',
            'discount_percent': 25,
            'active': True,
        },
        {
            'code': 'WELCOME15',
            'title': 'Welcome Bonus - 15% Off',
            'description': 'Welcome offer for new customers - 15% discount',
            'discount_percent': 15,
            'active': True,
        },
        {
            'code': 'SUMMER30',
            'title': 'Summer Special - 30% Off',
            'description': 'Limited time summer offer - 30% discount',
            'discount_percent': 30,
            'active': True,
        },
        {
            'code': 'LOYALTY50',
            'title': 'Loyalty Reward - 50% Off',
            'description': 'Exclusive offer for loyal members - 50% discount',
            'discount_percent': 50,
            'active': True,
        },
    ]
    
    for coupon_data in dummy_coupons:
        Coupon.objects.get_or_create(code=coupon_data['code'], defaults=coupon_data)


def remove_dummy_coupons(apps, schema_editor):
    Coupon = apps.get_model('rewards', 'Coupon')
    coupon_codes = ['SAVE10', 'SAVE20', 'SAVE25', 'WELCOME15', 'SUMMER30', 'LOYALTY50']
    Coupon.objects.filter(code__in=coupon_codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rewards', '0002_coupon'),
    ]

    operations = [
        migrations.RunPython(add_dummy_coupons, remove_dummy_coupons),
    ]

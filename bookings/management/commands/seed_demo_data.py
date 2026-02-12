from __future__ import annotations

from django.core.management.base import BaseCommand

from charging.models import ChargingStation
from service_center.models import ServiceCenter
from services.models import ServiceType
from spareparts.models import SparePart
from rewards.models import Coupon


class Command(BaseCommand):
    help = "Seed demo Service Types, Service Centers, and Charging Stations."

    def handle(self, *args, **options):
        demo_services = [
            ("Battery Health Check", "Battery diagnostics and report.", "49.00"),
            ("Routine Maintenance", "General inspection and maintenance.", "79.00"),
            ("Tire Service", "Tire check, rotation and balancing.", "39.00"),
            ("Brake Inspection", "Brake pads/rotors inspection.", "29.00"),
        ]

        # Thrissur, Kerala (approx coordinates)
        demo_centers = [
            {
                "name": "Star EV Service Center - Thrissur Town",
                "address": "Thrissur, Kerala, India",
                "phone": "+91 487-555-0101",
                "latitude": 10.5276,
                "longitude": 76.2144,
                "operating_hours": "9am - 6pm",
            },
            {
                "name": "Star EV Service Center - Punkunnam",
                "address": "Punkunnam, Thrissur, Kerala, India",
                "phone": "+91 487-555-0112",
                "latitude": 10.5493,
                "longitude": 76.2086,
                "operating_hours": "9am - 6pm",
            },
            {
                "name": "Star EV Service Center - Ollur",
                "address": "Ollur, Thrissur, Kerala, India",
                "phone": "+91 487-555-0147",
                "latitude": 10.4818,
                "longitude": 76.2189,
                "operating_hours": "9am - 6pm",
            },
        ]

        demo_stations = [
            {
                "name": "Demo Charging Station - Thrissur Round",
                "address": "Thrissur Round, Thrissur, Kerala, India",
                "latitude": 10.5246,
                "longitude": 76.2140,
                "available_slots": 6,
                "plug_types": "CCS, Type2",
            },
            {
                "name": "Demo Charging Station - Vadakke Stand",
                "address": "Vadakke Stand, Thrissur, Kerala, India",
                "latitude": 10.5318,
                "longitude": 76.2166,
                "available_slots": 4,
                "plug_types": "CCS",
            },
            {
                "name": "Demo Charging Station - Amala Nagar",
                "address": "Amala Nagar, Thrissur, Kerala, India",
                "latitude": 10.5635,
                "longitude": 76.1837,
                "available_slots": 8,
                "plug_types": "CCS, CHAdeMO",
            },
        ]

        for name, description, base_price in demo_services:
            ServiceType.objects.update_or_create(
                name=name,
                defaults={"description": description, "base_price": base_price},
            )

        for c in demo_centers:
            ServiceCenter.objects.update_or_create(name=c["name"], defaults=c)

        for s in demo_stations:
            ChargingStation.objects.update_or_create(name=s["name"], defaults=s)

        demo_parts = [
            {
                "name": "EV Fast Charger Cable",
                "description": "Durable fast-charging cable compatible with common connectors.",
                "price": "2499.00",
                "quantity": 12,
                "image_url": "https://placehold.co/800x450?text=EV+Fast+Charger+Cable",
            },
            {
                "name": "Brake Pads (Set)",
                "description": "High-quality brake pads for smooth and safe braking.",
                "price": "1899.00",
                "quantity": 20,
                "image_url": "https://placehold.co/800x450?text=Brake+Pads",
            },
            {
                "name": "Cabin Air Filter",
                "description": "Improves air quality inside the vehicle cabin.",
                "price": "499.00",
                "quantity": 35,
                "image_url": "https://placehold.co/800x450?text=Cabin+Air+Filter",
            },
        ]
        for p in demo_parts:
            SparePart.objects.update_or_create(name=p["name"], defaults=p)

        demo_coupons = [
            {
                "code": "WELCOME10",
                "title": "Welcome discount",
                "description": "10% off on your first scheduled service.",
                "discount_percent": 10,
                "active": True,
            },
            {
                "code": "SERVICE15",
                "title": "Service savings",
                "description": "15% off on routine maintenance services.",
                "discount_percent": 15,
                "active": True,
            },
            {
                "code": "PARTS5",
                "title": "Parts deal",
                "description": "5% off on spare parts purchase.",
                "discount_percent": 5,
                "active": True,
            },
        ]
        for c in demo_coupons:
            Coupon.objects.update_or_create(code=c["code"], defaults=c)

        self.stdout.write(self.style.SUCCESS("Demo data ready (Thrissur + parts + coupons)."))

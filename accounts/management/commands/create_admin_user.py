import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a default admin user from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "").strip()
        email = os.getenv("ADMIN_EMAIL", "").strip()
        password = os.getenv("ADMIN_PASSWORD", "").strip()

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "ADMIN_USERNAME or ADMIN_PASSWORD not set; skipping admin creation."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email or ""},
        )

        if created:
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Admin user created: {username}"))
            return

        changed = False
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True
        if changed:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Admin user updated: {username}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Admin user exists: {username}"))

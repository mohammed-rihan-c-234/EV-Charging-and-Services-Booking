from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Profile


class Command(BaseCommand):
    help = "Create a Service Center role user (adds to service_center group and profile role)."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("password")
        parser.add_argument("--name", default="")
        parser.add_argument("--phone", default="")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        full_name = options["name"] or username
        phone = options["phone"] or ""

        if User.objects.filter(username=username).exists():
            raise CommandError("User already exists.")

        user = User.objects.create_user(username=username, password=password)
        group, _ = Group.objects.get_or_create(name="service_center")
        user.groups.add(group)

        Profile.objects.update_or_create(
            user=user,
            defaults={"full_name": full_name, "phone_number": phone, "role": Profile.ROLE_SERVICE_CENTER},
        )

        self.stdout.write(self.style.SUCCESS("Service center user created."))


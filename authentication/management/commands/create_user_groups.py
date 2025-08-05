from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create default user groups for the DHP platform'

    def handle(self, *args, **options):
        groups = [
            ('public', 'Public users with basic access'),
            ('creator', 'Content creators who can upload and manage content'),
            ('admin', 'Administrators with full system access'),
        ]

        for group_name, description in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created group "{group_name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Group "{group_name}" already exists')
                )

        self.stdout.write(
            self.style.SUCCESS('User groups initialization completed!')
        )

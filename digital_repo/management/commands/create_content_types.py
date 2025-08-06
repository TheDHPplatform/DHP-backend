from django.core.management.base import BaseCommand
from digital_repo.models import ArchiveType, DigitalContentType


class Command(BaseCommand):
    help = 'Create initial archive types and digital content types'

    def handle(self, *args, **options):
        # Archive types from the navigation menu
        archive_types = [
            {
                'name': 'Historical Documents',
                'description': 'Historical documents and records from various time periods'
            },
            {
                'name': 'Government Records',
                'description': 'Official government documents, policies, and administrative records'
            },
            {
                'name': 'Personal Papers',
                'description': 'Personal documents, letters, and papers from notable individuals'
            },
            {
                'name': 'Institutional Archives',
                'description': 'Archives from institutions, organizations, and companies'
            },
            {
                'name': 'Media Archives',
                'description': 'Historical media content including newspapers, magazines, and broadcasts'
            },
            {
                'name': 'Digital Preservation',
                'description': 'Digitally preserved documents and materials for long-term access'
            }
        ]

        # Digital content types from the navigation menu
        digital_content_types = [
            {
                'name': 'Datasets',
                'description': 'Statistical data, research datasets, and data collections'
            },
            {
                'name': 'Multimedia',
                'description': 'Audio, video, and interactive multimedia content'
            },
            {
                'name': 'Interactive Content',
                'description': 'Interactive educational and informational content'
            },
            {
                'name': 'Educational Resources',
                'description': 'Learning materials, courses, and educational tools'
            },
            {
                'name': '3D Models',
                'description': '3D models, virtual objects, and immersive content'
            },
            {
                'name': 'Audio Collections',
                'description': 'Audio recordings, music, speeches, and sound archives'
            }
        ]

        # Create archive types
        self.stdout.write('Creating archive types...')
        for archive_type_data in archive_types:
            archive_type, created = ArchiveType.objects.get_or_create(
                name=archive_type_data['name'],
                defaults={'description': archive_type_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created archive type: {archive_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Archive type already exists: {archive_type.name}')
                )

        # Create digital content types
        self.stdout.write('\nCreating digital content types...')
        for content_type_data in digital_content_types:
            content_type, created = DigitalContentType.objects.get_or_create(
                name=content_type_data['name'],
                defaults={'description': content_type_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created digital content type: {content_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Digital content type already exists: {content_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('\nSuccessfully created all archive and digital content types!')
        )

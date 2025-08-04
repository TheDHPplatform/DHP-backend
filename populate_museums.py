#!/usr/bin/env python
"""
Script to populate the database with museum data
"""
import os
import sys
import django
from decimal import Decimal

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dhp_backend.settings')
django.setup()

from digital_repo.models import MuseumCategory, Museum
from django.contrib.auth.models import User

def create_categories():
    """Create museum categories"""
    categories_data = [
        {
            'name': 'Historical',
            'description': 'Museums showcasing historical events, artifacts, and periods',
            'icon': 'history',
            'color': '#8B5A2B'
        },
        {
            'name': 'Cultural',
            'description': 'Museums focusing on cultural heritage and traditions',
            'icon': 'culture',
            'color': '#4A90E2'
        },
        {
            'name': 'Memorial',
            'description': 'Memorial sites and museums of remembrance',
            'icon': 'memorial',
            'color': '#E74C3C'
        },
        {
            'name': 'Art',
            'description': 'Art galleries and museums showcasing artistic works',
            'icon': 'palette',
            'color': '#9B59B6'
        },
        {
            'name': 'History',
            'description': 'Museums dedicated to historical preservation and education',
            'icon': 'book',
            'color': '#34495E'
        }
    ]
    
    for category_data in categories_data:
        category, created = MuseumCategory.objects.get_or_create(
            name=category_data['name'],
            defaults=category_data
        )
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")


def create_museums():
    """Create museums with sample data"""
    # Get or create a default user for curator
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    museums_data = [
        {
            'name': "KING'S PALACE",
            'location': "Nyanza",
            'description': "A reconstruction of the traditional royal residence, the King's Palace is a beautifully-crafted thatched dwelling shaped like a beehive.",
            'long_description': "At the back live a few long-horned Inyambo cattle, descended from the king's herd, whose keepers carefully tend and sing to them, keeping alive a unique tradition.",
            'main_image': "https://www.rwandawildlifesafari.com/wp-content/uploads/2022/10/Kings-Palace-Nyanza.jpg",
            'category_name': "Historical",
            'city': 'Nyanza',
            'address': 'Nyanza District, Southern Province',
            'established_year': 1960,
            'admission_fee': Decimal('5000.00'),
            'has_parking': True,
            'has_guided_tours': True,
            'opening_hours': {
                'monday': '8:00 AM - 5:00 PM',
                'tuesday': '8:00 AM - 5:00 PM',
                'wednesday': '8:00 AM - 5:00 PM',
                'thursday': '8:00 AM - 5:00 PM',
                'friday': '8:00 AM - 5:00 PM',
                'saturday': '8:00 AM - 5:00 PM',
                'sunday': '8:00 AM - 5:00 PM'
            },
            'tags': 'royal, traditional, heritage, Inyambo cattle'
        },
        {
            'name': "ETHNOGRAPHIC MUSEUM",
            'location': "Butare",
            'description': "A gift from Belgium's King Baudouin in the late 1980s, the Ethnographic Museum now houses one of Africa's finest ethnographic collections.",
            'long_description': "The museum showcases traditional Rwandan culture, arts, and crafts through carefully curated exhibitions.",
            'main_image': "https://www.rwandawildlifesafari.com/wp-content/uploads/2024/10/Visit-Rwanda-Ethnographic-Museum-1650x1097-1-1170x450.jpg",
            'category_name': "Cultural",
            'city': 'Butare',
            'address': 'Butare, Southern Province',
            'established_year': 1989,
            'admission_fee': Decimal('3000.00'),
            'has_parking': True,
            'has_wifi': True,
            'has_guided_tours': True,
            'opening_hours': {
                'monday': '8:00 AM - 6:00 PM',
                'tuesday': '8:00 AM - 6:00 PM',
                'wednesday': '8:00 AM - 6:00 PM',
                'thursday': '8:00 AM - 6:00 PM',
                'friday': '8:00 AM - 6:00 PM',
                'saturday': '8:00 AM - 6:00 PM',
                'sunday': 'Closed'
            },
            'tags': 'ethnographic, culture, traditional arts, Belgium'
        },
        {
            'name': "KIGALI GENOCIDE MEMORIAL",
            'location': "Gisozi",
            'description': "Commemorating the 1994 Rwandan genocide against the Tutsi, the Kigali Genocide Memorial at Gisozi is where 250,000 victims have been buried.",
            'long_description': "It serves as a place of remembrance to educate about how the Genocide against the Tutsi took shape and examines genocide in the 20th century.",
            'main_image': "https://away2uganda.com/wp-content/uploads/2024/05/rwanda-genocidal-memorial.jpg",
            'category_name': "Memorial",
            'city': 'Kigali',
            'address': 'Gisozi, Kigali',
            'established_year': 2004,
            'admission_fee': Decimal('0.00'),  # Free entry
            'has_parking': True,
            'has_wifi': True,
            'has_guided_tours': True,
            'is_wheelchair_accessible': True,
            'opening_hours': {
                'monday': '8:00 AM - 5:00 PM',
                'tuesday': '8:00 AM - 5:00 PM',
                'wednesday': '8:00 AM - 5:00 PM',
                'thursday': '8:00 AM - 5:00 PM',
                'friday': '8:00 AM - 5:00 PM',
                'saturday': '8:00 AM - 5:00 PM',
                'sunday': '8:00 AM - 5:00 PM'
            },
            'tags': 'genocide, memorial, remembrance, education, 1994'
        },
        {
            'name': "RWANDA ART MUSEUM",
            'location': "Kigali",
            'description': "Formerly the Presidential Palace Museum, this new museum displays contemporary artworks from Rwanda as well as abroad.",
            'long_description': "The museum seeks to provide an insight into the originality of Rwandan creativity and contemporary artistic expression.",
            'main_image': "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Outside_Presidential_Palace_Museum_Kigali_Rwanda_29.jpg/1200px-Outside_Presidential_Palace_Museum_Kigali_Rwanda_29.jpg",
            'category_name': "Art",
            'city': 'Kigali',
            'address': 'Kigali City',
            'established_year': 2018,
            'admission_fee': Decimal('5000.00'),
            'has_parking': True,
            'has_wifi': True,
            'has_restaurant': True,
            'has_gift_shop': True,
            'has_guided_tours': True,
            'is_wheelchair_accessible': True,
            'opening_hours': {
                'monday': 'Closed',
                'tuesday': '9:00 AM - 5:00 PM',
                'wednesday': '9:00 AM - 5:00 PM',
                'thursday': '9:00 AM - 5:00 PM',
                'friday': '9:00 AM - 5:00 PM',
                'saturday': '9:00 AM - 5:00 PM',
                'sunday': '9:00 AM - 5:00 PM'
            },
            'tags': 'art, contemporary, presidential palace, creativity'
        },
        {
            'name': "Kandt House Museum",
            'location': "Kigali",
            'description': "Richard Kandt was the first colonial governor of Rwanda, on behalf of Germany, until the early 1900s. His old house in Kigali is now a museum examining life in Rwanda before, during and after the colonial period.",
            'long_description': "Richard Kandt was the first colonial governor of Rwanda, on behalf of Germany, until the early 1900s. His old house in Kigali is now a museum examining life in Rwanda before, during and after the colonial period.",
            'main_image': "https://ugandarwandagorillatours.com/wp-content/uploads/2024/03/image.jpg",
            'category_name': "History",
            'city': 'Kigali',
            'address': 'Kigali City',
            'established_year': 2008,
            'admission_fee': Decimal('2000.00'),
            'has_parking': True,
            'has_guided_tours': True,
            'opening_hours': {
                'monday': '8:00 AM - 5:00 PM',
                'tuesday': '8:00 AM - 5:00 PM',
                'wednesday': '8:00 AM - 5:00 PM',
                'thursday': '8:00 AM - 5:00 PM',
                'friday': '8:00 AM - 5:00 PM',
                'saturday': '8:00 AM - 5:00 PM',
                'sunday': 'Closed'
            },
            'tags': 'colonial, history, Richard Kandt, Germany, governor'
        }
    ]
    
    for museum_data in museums_data:
        # Get the category
        category = MuseumCategory.objects.get(name=museum_data.pop('category_name'))
        
        museum, created = Museum.objects.get_or_create(
            name=museum_data['name'],
            defaults={
                **museum_data,
                'category': category,
                'curator': admin_user,
                'created_by': admin_user,
                'is_featured': True,  # Mark all as featured for demo
                'status': 'active'
            }
        )
        
        if created:
            print(f"Created museum: {museum.name}")
        else:
            print(f"Museum already exists: {museum.name}")


def main():
    print("Populating museum database...")
    create_categories()
    create_museums()
    print("Museum database population completed!")


if __name__ == '__main__':
    main()

import os
import django
import random
from faker import Faker
import string

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_project.settings')
django.setup()

from healthcare.models import Doctor

# Initialize Faker for generating realistic data
fake = Faker()

def generate_password(length=12):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def add_doctors():
    # List of common medical specialties
    specialties = [
        'Cardiology', 'Dermatology', 'Pediatrics', 'Orthopedics', 'Neurology',
        'Gastroenterology', 'Ophthalmology', 'Endocrinology', 'Urology', 'Oncology',
        'Psychiatry', 'General Practice', 'Rheumatology', 'Pulmonology', 'Nephrology',
        'Gynecology', 'Allergy and Immunology', 'Anesthesiology', 'Infectious Disease',
        'Family Medicine'
    ]

    # Generate 100 doctors
    doctors = []
    for i in range(100):
        # Generate unique name and email
        name = fake.name()
        email = f"doctor{i+1}@example.com"  # Ensures unique email
        # Generate random phone number
        phone = fake.phone_number()[:20] if random.choice([True, False]) else None

        doctors.append({
            'name': name,
            'speciality': random.choice(specialties),
            'email': email,
            'password': generate_password(),
            'address': fake.address().replace('\n', ', ')[:200] if random.choice([True, False]) else None,
            'phone': phone,
            'experience': random.randint(1, 30),
            'rating': round(random.uniform(2.5, 5.0), 1),
            'rating_count': random.randint(10, 200),
            'virtual_visit': random.choice([True, False]),
            'image_url': f'images/d{random.randint(1, 20)}.jpg',
            'distance': round(random.uniform(0.5, 50.0), 1) if random.choice([True, False]) else None,
            'temp_dummy': ''.join(random.choices(string.ascii_lowercase, k=8)) if random.choice([True, False]) else ''
        })

    # Add doctors to the database
    for doc in doctors:
        # Check if doctor email already exists to avoid duplicates
        if not Doctor.objects.filter(email=doc['email']).exists():
            Doctor.objects.create(
                name=doc['name'],
                speciality=doc['speciality'],
                email=doc['email'],
                password=doc['password'],
                address=doc['address'],
                phone=doc['phone'],
                experience=doc['experience'],
                rating=doc['rating'],
                rating_count=doc['rating_count'],
                virtual_visit=doc['virtual_visit'],
                image_url=doc['image_url'],
                distance=doc['distance'],
                temp_dummy=doc['temp_dummy']
            )
            print(f"Added Dr. {doc['name']} to the database.")
        else:
            print(f"Dr. {doc['name']} with email {doc['email']} already exists in the database.")

if __name__ == '__main__':
    print("Starting to add doctors...")
    add_doctors()
    print("Finished adding doctors.")
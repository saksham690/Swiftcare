import os
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_project.settings')
django.setup()

from SwiftCart.models import Medicine

def add_medicines():
    # List of 50 medicines to add
    medicines = [
        # Original medicines
        {
            'name': 'Moisturizing Cream',
            'description': 'Hydrates and soothes dry skin.',
            'price': Decimal('15.99'),
            'image_url': 'https://example.com/images/moisturizer.jpg',
            'category': 'skin'
        },
        {
            'name': 'Cough Syrup',
            'description': 'Relieves cough and sore throat.',
            'price': Decimal('9.50'),
            'image_url': 'https://example.com/images/cough_syrup.jpg',
            'category': 'cold'
        },
        {
            'name': 'Metformin',
            'description': 'Controls blood sugar levels for diabetes.',
            'price': Decimal('12.75'),
            'image_url': 'https://example.com/images/metformin.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Antihistamine',
            'description': 'Relieves allergy symptoms and cold.',
            'price': Decimal('8.25'),
            'image_url': 'https://example.com/images/antihistamine.jpg',
            'category': 'cold'
        },
        {
            'name': 'Sunscreen SPF 50',
            'description': 'Protects skin from UV rays.',
            'price': Decimal('18.00'),
            'image_url': 'https://example.com/images/sunscreen.jpg',
            'category': 'skin'
        },
        # Additional skin care medicines
        {
            'name': 'Cleansing Gel',
            'description': 'Removes impurities and excess oil.',
            'price': Decimal('10.50'),
            'image_url': 'https://example.com/images/cleansing_gel.jpg',
            'category': 'skin'
        },
        {
            'name': 'Acne Spot Treatment',
            'description': 'Targets acne and reduces redness.',
            'price': Decimal('12.99'),
            'image_url': 'https://example.com/images/acne_treatment.jpg',
            'category': 'skin'
        },
        {
            'name': 'Night Cream',
            'description': 'Nourishes skin overnight.',
            'price': Decimal('22.00'),
            'image_url': 'https://example.com/images/night_cream.jpg',
            'category': 'skin'
        },
        {
            'name': 'Eye Cream',
            'description': 'Reduces puffiness and dark circles.',
            'price': Decimal('19.75'),
            'image_url': 'https://example.com/images/eye_cream.jpg',
            'category': 'skin'
        },
        {
            'name': 'Face Mask',
            'description': 'Deeply hydrates and revitalizes skin.',
            'price': Decimal('14.25'),
            'image_url': 'https://example.com/images/face_mask.jpg',
            'category': 'skin'
        },
        {
            'name': 'Exfoliating Scrub',
            'description': 'Removes dead skin cells for a smooth finish.',
            'price': Decimal('11.99'),
            'image_url': 'https://example.com/images/exfoliator.jpg',
            'category': 'skin'
        },
        {
            'name': 'Anti-Aging Serum',
            'description': 'Reduces fine lines and wrinkles.',
            'price': Decimal('29.99'),
            'image_url': 'https://example.com/images/anti_aging_serum.jpg',
            'category': 'skin'
        },
        {
            'name': 'Lip Balm',
            'description': 'Moisturizes and protects lips.',
            'price': Decimal('4.50'),
            'image_url': 'https://example.com/images/lip_balm.jpg',
            'category': 'skin'
        },
        {
            'name': 'Body Lotion',
            'description': 'Hydrates and softens body skin.',
            'price': Decimal('13.00'),
            'image_url': 'https://example.com/images/body_lotion.jpg',
            'category': 'skin'
        },
        {
            'name': 'Hand Cream',
            'description': 'Repairs dry and cracked hands.',
            'price': Decimal('7.99'),
            'image_url': 'https://example.com/images/hand_cream.jpg',
            'category': 'skin'
        },
        {
            'name': 'Toner',
            'description': 'Balances skin pH and tightens pores.',
            'price': Decimal('12.50'),
            'image_url': 'https://example.com/images/toner.jpg',
            'category': 'skin'
        },
        {
            'name': 'Hydrating Serum',
            'description': 'Boosts skin hydration and glow.',
            'price': Decimal('25.00'),
            'image_url': 'https://example.com/images/hydrating_serum.jpg',
            'category': 'skin'
        },
        {
            'name': 'Clay Mask',
            'description': 'Detoxifies and purifies skin.',
            'price': Decimal('15.50'),
            'image_url': 'https://example.com/images/clay_mask.jpg',
            'category': 'skin'
        },
        {
            'name': 'SPF 30 Lotion',
            'description': 'Daily sun protection for sensitive skin.',
            'price': Decimal('16.75'),
            'image_url': 'https://example.com/images/spf30_lotion.jpg',
            'category': 'skin'
        },
        {
            'name': 'Vitamin C Serum',
            'description': 'Brightens and evens skin tone.',
            'price': Decimal('27.50'),
            'image_url': 'https://example.com/images/vitamin_c_serum.jpg',
            'category': 'skin'
        },
        # Additional cold & cough medicines
        {
            'name': 'Decongestant Spray',
            'description': 'Clears nasal congestion.',
            'price': Decimal('6.99'),
            'image_url': 'https://example.com/images/decongestant_spray.jpg',
            'category': 'cold'
        },
        {
            'name': 'Throat Lozenges',
            'description': 'Soothes sore throat and cough.',
            'price': Decimal('4.75'),
            'image_url': 'https://example.com/images/lozenges.jpg',
            'category': 'cold'
        },
        {
            'name': 'Cold Relief Tablets',
            'description': 'Relieves cold symptoms like fever and aches.',
            'price': Decimal('7.50'),
            'image_url': 'https://example.com/images/cold_tablets.jpg',
            'category': 'cold'
        },
        {
            'name': 'Nasal Drops',
            'description': 'Relieves stuffy nose and sinus pressure.',
            'price': Decimal('5.25'),
            'image_url': 'https://example.com/images/nasal_drops.jpg',
            'category': 'cold'
        },
        {
            'name': 'Vapor Rub',
            'description': 'Eases breathing during colds.',
            'price': Decimal('6.50'),
            'image_url': 'https://example.com/images/vapor_rub.jpg',
            'category': 'cold'
        },
        {
            'name': 'Flu Relief Powder',
            'description': 'Reduces flu symptoms and boosts recovery.',
            'price': Decimal('8.99'),
            'image_url': 'https://example.com/images/flu_powder.jpg',
            'category': 'cold'
        },
        {
            'name': 'Cough Drops',
            'description': 'Soothes persistent cough.',
            'price': Decimal('3.99'),
            'image_url': 'https://example.com/images/cough_drops.jpg',
            'category': 'cold'
        },
        {
            'name': 'Allergy Relief',
            'description': 'Reduces sneezing and itchy eyes.',
            'price': Decimal('9.25'),
            'image_url': 'https://example.com/images/allergy_relief.jpg',
            'category': 'cold'
        },
        {
            'name': 'Chest Congestion Syrup',
            'description': 'Loosens mucus and relieves chest tightness.',
            'price': Decimal('10.75'),
            'image_url': 'https://example.com/images/chest_syrup.jpg',
            'category': 'cold'
        },
        {
            'name': 'Sinus Relief Capsules',
            'description': 'Eases sinus pain and pressure.',
            'price': Decimal('11.50'),
            'image_url': 'https://example.com/images/sinus_capsules.jpg',
            'category': 'cold'
        },
        {
            'name': 'Daytime Cold Medicine',
            'description': 'Non-drowsy relief for cold symptoms.',
            'price': Decimal('9.99'),
            'image_url': 'https://example.com/images/daytime_cold.jpg',
            'category': 'cold'
        },
        {
            'name': 'Nighttime Cold Medicine',
            'description': 'Helps sleep with cold symptom relief.',
            'price': Decimal('10.25'),
            'image_url': 'https://example.com/images/nighttime_cold.jpg',
            'category': 'cold'
        },
        {
            'name': 'Mucus Relief Tablets',
            'description': 'Clears mucus and congestion.',
            'price': Decimal('8.50'),
            'image_url': 'https://example.com/images/mucus_tablets.jpg',
            'category': 'cold'
        },
        {
            'name': 'Sore Throat Spray',
            'description': 'Numbs and soothes throat pain.',
            'price': Decimal('7.75'),
            'image_url': 'https://example.com/images/throat_spray.jpg',
            'category': 'cold'
        },
        # Additional diabetes medicines
        {
            'name': 'Insulin Glargine',
            'description': 'Long-acting insulin for blood sugar control.',
            'price': Decimal('45.00'),
            'image_url': 'https://example.com/images/insulin_glargine.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Gliclazide',
            'description': 'Stimulates insulin release for type 2 diabetes.',
            'price': Decimal('14.50'),
            'image_url': 'https://example.com/images/gliclazide.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Pioglitazone',
            'description': 'Improves insulin sensitivity.',
            'price': Decimal('16.25'),
            'image_url': 'https://example.com/images/pioglitazone.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Sitagliptin',
            'description': 'Enhances insulin production after meals.',
            'price': Decimal('22.50'),
            'image_url': 'https://example.com/images/sitagliptin.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Dapagliflozin',
            'description': 'Reduces blood sugar by kidney filtration.',
            'price': Decimal('28.75'),
            'image_url': 'https://example.com/images/dapagliflozin.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Glimepiride',
            'description': 'Lowers blood sugar in type 2 diabetes.',
            'price': Decimal('13.99'),
            'image_url': 'https://example.com/images/glimepiride.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Acarbose',
            'description': 'Slows carbohydrate absorption.',
            'price': Decimal('15.50'),
            'image_url': 'https://example.com/images/acarbose.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Empagliflozin',
            'description': 'Lowers glucose via urine excretion.',
            'price': Decimal('29.99'),
            'image_url': 'https://example.com/images/empagliflozin.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Vildagliptin',
            'description': 'Increases insulin secretion.',
            'price': Decimal('21.25'),
            'image_url': 'https://example.com/images/vildagliptin.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Linagliptin',
            'description': 'Controls blood sugar with low hypoglycemia risk.',
            'price': Decimal('23.50'),
            'image_url': 'https://example.com/images/linagliptin.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Insulin Aspart',
            'description': 'Fast-acting insulin for mealtime control.',
            'price': Decimal('42.00'),
            'image_url': 'https://example.com/images/insulin_aspart.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Repaglinide',
            'description': 'Stimulates rapid insulin release.',
            'price': Decimal('17.75'),
            'image_url': 'https://example.com/images/repaglinide.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Nateglinide',
            'description': 'Controls post-meal glucose spikes.',
            'price': Decimal('16.99'),
            'image_url': 'https://example.com/images/nateglinide.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Canagliflozin',
            'description': 'Reduces blood sugar through urine.',
            'price': Decimal('30.25'),
            'image_url': 'https://example.com/images/canagliflozin.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Tolbutamide',
            'description': 'Lowers blood sugar in type 2 diabetes.',
            'price': Decimal('12.99'),
            'image_url': 'https://example.com/images/tolbutamide.jpg',
            'category': 'diabetes'
        },
        {
            'name': 'Glipizide',
            'description': 'Stimulates insulin production.',
            'price': Decimal('13.50'),
            'image_url': 'https://example.com/images/glipizide.jpg',
            'category': 'diabetes'
        },
    ]

    # Add medicines to the database
    for med in medicines:
        # Check if medicine already exists to avoid duplicates
        if not Medicine.objects.filter(name=med['name']).exists():
            Medicine.objects.create(
                name=med['name'],
                description=med['description'],
                price=med['price'],
                image_url=med['image_url'],
                category=med['category']
            )
            print(f"Added {med['name']} to the database.")
        else:
            print(f"{med['name']} already exists in the database.")

if __name__ == '__main__':
    print("Starting to add medicines...")
    add_medicines()
    print("Finished adding medicines.")
from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_db():
    try:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS products
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL UNIQUE,
                      description TEXT,
                      price REAL,
                      image_url TEXT,
                      category TEXT,
                      stock_quantity INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS comments
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      product_name TEXT NOT NULL,
                      reviewer_name TEXT NOT NULL,
                      reviewer_email TEXT,
                      rating INTEGER NOT NULL,
                      comment_text TEXT NOT NULL,
                      created_at TEXT NOT NULL)''')
        conn.commit()
        logger.debug("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
    finally:
        conn.close()

def seed_data():
    try:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        products = [
            # Medicines from add_medicines.py (50)
            ('Moisturizing Cream', 'Hydrates and soothes dry skin.', 15.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTN64-Feo2lV7CI1G8EcUWUpB4AEJSDWuDxSg&s', 'skin', 50),
            ('Cough Syrup', 'Relieves cough and sore throat.', 9.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSMn263P_IPeXgwHaxlnfT4R1GUJ64S4BFJgA&s', 'cold', 75),
            ('Metformin', 'Controls blood sugar levels for diabetes.', 12.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGHkQ6ISytrJEwoQgTKKEzdnN7B4ZZU2FiTQ&s', 'diabetes', 80),
            ('Antihistamine', 'Relieves allergy symptoms and cold.', 8.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYWpb2NRQgO-RNQSMzKWWhLDMIEyYH2JOeIA&s', 'cold', 100),
            ('Sunscreen SPF 50', 'Protects skin from UV rays.', 18.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAkp0sD14ZrtFcfdgRhUM_RngbwpbWNLIY-g&s', 'skin', 50),
            ('Cleansing Gel', 'Removes impurities and excess oil.', 10.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTN2uq-gc92bXx48xriBcjLpMFQb0cF2MpX9w&s', 'skin', 50),
            
            ('Acne Spot Treatment', 'Targets acne and reduces redness.', 12.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQXUjKJqUrGj7BypYegK8K103-3jeNf28q_kg&s', 'skin', 50),
            
            ('Night Cream', 'Nourishes skin overnight.', 22.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR5haxr1J5aZzyLKxhBY2Fyacpt5BfgLOJfuQ&s', 'skin', 50),
            
            ('Eye Cream', 'Reduces puffiness and dark circles.', 19.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTUi5A0SRe--C6Ag1chJRHnY2gXI2Q20r7Awg&s', 'skin', 50),
            
            ('Face Mask', 'Deeply hydrates and revitalizes skin.', 14.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTa6a4AZX4SJ6rHeIWPYllwfJOrrkWKg9efYA&s', 'skin', 50),
            ('Exfoliating Scrub', 'Removes dead skin cells for a smooth finish.', 11.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWY9Hl6OItixLh4a7JugXAZFBcu4gi0W_YKA&s', 'skin', 50),
            ('Anti-Aging Serum', 'Reduces fine lines and wrinkles.', 29.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcReI3tqm0wMGlUZDQQjUOOKozU6p1yHNW9uZQ&s', 'skin', 50),
            ('Lip Balm', 'Moisturizes and protects lips.', 4.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTDMSGhuJaSowvaxd6EUo1VpZ0zKx3Mp58okA&s', 'skin', 50),
            ('Body Lotion', 'Hydrates and softens body skin.', 13.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTgVwpQPPo12ilH4y7iUO05GDYURhiLKQLTXg&s', 'skin', 50),
            ('Hand Cream', 'Repairs dry and cracked hands.', 7.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsU9HB-yNynmVwYgE1BR8HwUeC5OEVM1y2Gw&s', 'skin', 50),
            ('Toner', 'Balances skin pH and tightens pores.', 12.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQsyEQ1XcJsk0HxuaW5o62fOKETiJjgJYapPg&s', 'skin', 50),
            ('Hydrating Serum', 'Boosts skin hydration and glow.', 25.00, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT0jDe_6e2AdhPfXFNSiergmlLc3WUUPj6_9A&s', 'skin', 50),
            ('Clay Mask', 'Detoxifies and purifies skin.', 15.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQdDd3vUVk8Pagu-xC1AnT0LB20DrBTO137Kw&s', 'skin', 50),
            ('SPF 30 Lotion', 'Daily sun protection for sensitive skin.', 16.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSyWzCWLKwNl3fcP8EGnaU7THivB1Ju6kjUsg&s', 'skin', 50),
            ('Vitamin C Serum', 'Brightens and evens skin tone.', 27.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNXNk02RSfECrsIKfJh7PVWLA2eCln3MW8CA&s', 'skin', 30),
            ('Decongestant Spray', 'Clears nasal congestion.', 6.99, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRg1aigBc8AJDF5EyutEKlzopqvM5sqhI9JoQ&s', 'cold', 100),
            ('Throat Lozenges', 'Soothes sore throat and cough.', 4.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSOf1ItwuZeB2x_gEtVk15gC1_lkar29H2xtA&s', 'cold', 100),
            ('Cold Relief Tablets', 'Relieves cold symptoms like fever and aches.', 7.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaNX3dnfWCpqklB8iueG4t4PmZT-86REKc8Q&s', 'cold', 100),
            ('Nasal Drops', 'Relieves stuffy nose and sinus pressure.', 5.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWkpNtb6hGULVZ07JdXjyYa9Mhfprcii0FeQ&s', 'cold', 100),
            ('Vapor Rub', 'Eases breathing during colds.', 6.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR39hp-BLQ62R9TxepM8LddpO90rB6J55lGAw&s', 'cold', 100),
            ('Flu Relief Powder', 'Reduces flu symptoms and boosts recovery.', 8.99, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBCXRF87tJFUi4nfa-e20TPaZEyZDGuFuU_Q&s', 'cold', 100),
            ('Cough Drops', 'Soothes persistent cough.', 3.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR9qDelfKf9ENbmUYvE17nRMhZy72ufK-qlAA&s', 'cold', 100),
            ('Allergy Relief', 'Reduces sneezing and itchy eyes.', 9.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT7aNSmFMSvrGOv34qWq-2p57JwJjTe2XtB3A&s', 'cold', 100),
            ('Chest Congestion Syrup', 'Loosens mucus and relieves chest tightness.', 10.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTf8Tkhy3oEslhk3-Vdd-E64afvxBdlGRbAzg&s', 'cold', 100),
            ('Sinus Relief Capsules', 'Eases sinus pain and pressure.', 11.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmpIAMko0Mtaxrt1J3QAqMKPkxhyJ-m_FogA&s', 'cold', 100),
            ('Daytime Cold Medicine', 'Non-drowsy relief for cold symptoms.', 9.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRPK3Rm8xUdl1rOjaO5LC7v9qzZxtNjjC2e6g&s', 'cold', 100),
            ('Nighttime Cold Medicine', 'Helps sleep with cold symptom relief.', 10.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnnVxfGoGo2So7A7U8fb9cHgLRO_op6SGZ4Q&s', 'cold', 100),
            ('Mucus Relief Tablets', 'Clears mucus and congestion.', 8.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQGWmdKfV25TZH9Hmj3wcr_uR9VoaHtipCCgw&s', 'cold', 100),
            ('Sore Throat Spray', 'Numbs and soothes throat pain.', 7.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKHdUNPVD2-bbPjYLHD79jj9DpcqEFNitF2w&s', 'cold', 100),
            ('Insulin Glargine', 'Long-acting insulin for blood sugar control.', 45.00, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdMoBSx5aNjm3Ipj59wbk0fGF9-IkKp5Rnbw&s', 'diabetes', 30),
            ('Gliclazide', 'Stimulates insulin release for type 2 diabetes.', 14.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTDuWbeIkWwyEObIlrejv5OfUivu0b8aWeA7g&s', 'diabetes', 30),
            ('Pioglitazone', 'Improves insulin sensitivity.', 16.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSD2KLoClYII4DwkbLTSXar2prHr8rbXleKAg&s', 'diabetes', 30),
            ('Sitagliptin', 'Enhances insulin production after meals.', 22.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4wwkrohi52OefVzKyEcD2AQfsl9hBL3UKIg&s', 'diabetes', 30),
            ('Dapagliflozin', 'Reduces blood sugar by kidney filtration.', 28.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtrRtCU9gCppAK2O8CsFIsYGxNKvxkr91H-A&s', 'diabetes', 30),
            ('Glimepiride', 'Lowers blood sugar in type 2 diabetes.', 13.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrFaUoCVH2jM9Y603jQYouSFTvqRNZgKdtdA&s', 'diabetes', 30),
            ('Acarbose', 'Slows carbohydrate absorption.', 15.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTmfkGeSdwGyEQqkwgnxo4G_w7K-iRgXbCGAA&s', 'diabetes', 30),
            ('Empagliflozin', 'Lowers glucose via urine excretion.', 29.99, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRd4-3XXpujT6dTrIF0gAlmurqgicDbxMbElw&s', 'diabetes', 30),
            ('Vildagliptin', 'Increases insulin secretion.', 21.25, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2iViCT5kvdzobqToaVq5-__Xffqp-S-fMSQ&s', 'diabetes', 30),
            ('Linagliptin', 'Controls blood sugar with low hypoglycemia risk.', 23.50, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR10w99SWpcZxIhVYKx7yQZ9xE-5UM5voCuFw&s', 'diabetes', 30),
            ('Insulin Aspart', 'Fast-acting insulin for mealtime control.', 42.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTLEw-kqNy8JoOxKQRytFUef6ATsVr3hCEyw&s', 'diabetes', 20),
            ('Repaglinide', 'Stimulates rapid insulin release.', 17.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRmdNeiTLv_6-IzIjybuv715HCtRfEtAMoNbg&s', 'diabetes', 30),
            ('Nateglinide', 'Controls post-meal glucose spikes.', 16.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQe7fJ-Vs3yuA3WW8ptPeBUTQ9ke3ihXEWrmQ&s', 'diabetes', 30),
            ('Canagliflozin', 'Reduces blood sugar through urine.', 30.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT8eJfjpJu7hXHAlB8tWI5vxSpaOiktE-GMSw&s', 'diabetes', 30),
            ('Tolbutamide', 'Lowers blood sugar in type 2 diabetes.', 12.99, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-4fxz6e5TYglUJ7lPV_bchw5KLfxEATxerw&s', 'diabetes', 30),
            ('Glipizide', 'Stimulates insulin production.', 13.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-dQNaPt3SqnylendbrRP5D2iiUfolgcLz4A&s', 'diabetes', 30),
            # Additional medicines from original app.py (14 unique)
            ('Paracetamol', 'Reduces fever and pain.', 5.99, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLpJ3xVC0nGhklfwtZwH97Hbcyn5MSnrk7WQ&s', 'pain', 200),
            ('Ibuprofen', 'Anti-inflammatory drug.', 7.49, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQc_bwpKlBmqfGkRJVVDKoCqvFKeMXRaYCtjQ&s', 'pain', 150),
            ('Aspirin', 'Pain relief and anti-inflammatory.', 6.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7LBSYhHvT1xPqanRfDa8H6B8t8hZlCq4kIw&s', 'pain', 180),
            ('Amoxicillin', 'Antibiotic for infections.', 12.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTlaXSgFzQMO6BtFdZXSNO0YB_hPiKy1K39zw&s', 'antibiotic', 60),
            ('Azithromycin', 'Treats bacterial infections.', 14.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfsQF3VtkWuo6hT-vJv-Nhf6BWp3clGYDTmg&s', 'antibiotic', 40),
            ('Lisinopril', 'Manages high blood pressure.', 9.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQOGTKD47XurpkP5iCkZBplT308isXvIMJpfQ&s', 'heart', 90),
            ('Amlodipine', 'Treats high blood pressure.', 8.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCCK6rUznz1qT6HgIUBtTZiyI8hxb-BGbqvQ&s', 'heart', 100),
            ('Atorvastatin', 'Lowers cholesterol.', 11.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRDcMYKkeTG-0TD0e_6xCVjg6YB89U5SWdeUw&s', 'heart', 70),
            ('Levothyroxine', 'Treats hypothyroidism.', 7.99, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTe0OOxdTUwsAN209mW9lWXTkmTuPEWESfPfA&s', 'thyroid', 110),
            ('Omeprazole', 'Reduces stomach acid.', 13.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSrz8Cs0KGE7UKI-BAnT9tBeYQQZ2Nk0TOBiQ&s', 'stomach', 65),
            ('Pantoprazole', 'Proton pump inhibitor.', 14.25, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTWRcrY4v9Lraz1yxWmE3WJWZMhqxul6nneYw&s', 'stomach', 55),
            ('Sertraline', 'Antidepressant.', 16.99, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCjOijNUaoKXTq5GR7tYXNM45BlEVtzw6aCg&s', 'mental_health', 45),
            ('Fluoxetine', 'SSRI for depression.', 15.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwkCU-xoSYfmUiSXVP3zbkSDQlIxdXpbjwdw&s', 'mental_health', 50),
        
            ('Clotrimazole Cream', 'Antifungal cream for athletes foot and ringworm..', 8.75, '	https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSs19OpcwC8kHA6lR3_MhHBeCO__GJ_IR78Kw&s', 'skin', 120),
            ('Doxycycline', 'Antibiotic for acne and respiratory infections.', 13.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwkCU-xoSYfmUiSXVP3zbkSDQlIxdXpbjwdw&s', 'mental_health', 50),
            ('Prednisolone', 'Steroid for inflammation and autoimmune conditions.', 11.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS-KjJz62xVl3X-g50WPdPNbusNOYZ166MElg&s', 'steroid', 50),
            ('Methotrexate', 'Treats rheumatoid arthritis and certain cancers.', 15.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2Q2jqWIFX9NtZcS0ghnT_zXPV4RrQfIUraA&s', 'steroid', 50),
            ('Folic Acid', 'Supports cell division and prevents anemia.', 15.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQyzOUbiDalMw4X5UkXdkhhf4EvKcvy2LiBQQ&s', 'supplement', 200),
            ('Calcium Carbonate', 'Calcium supplement for strong bones and teeth.', 7.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOvJ0SF-LBNSVLIypKhEGW1rHUqoNtkQM61w&s', 'supplement', 170),
            ('Iron Supplement', 'Treats iron deficiency anemia.', 8.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRh6ejTgcA4k_lknnwD91qscZGTt5BtfAcOJA&s', 'supplement', 160),
            ('Zinc Tablets', 'Boosts immune system and supports wound healing.', 9.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTli1zmLNYWYCvQTIgqrtfmm735tZq6t0sdug&s', 'sleep', 100),
            ('Melatonin', 'Improves sleep quality for insomnia relief.', 15.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwkCU-xoSYfmUiSXVP3zbkSDQlIxdXpbjwdw&s', 'mental_health', 50),
            ('Diphenhydramine', 'Antihistamine for sleep aid and allergy relief.', 7.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRQAZ0Rf0NgKhTCF0cBIUpg8FRqHJFGhK0iEQ&s', 'sleep', 110),
            ('Loperamide', 'Treats diarrhea by slowing gut movement.', 6.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQnIal4TeHQlw5ID_uL9708H_oY7u5mqLUVOg&s', 'stomach', 120),
            ('Bisacodyl', 'Laxative for constipation relief.', 5.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGn-kCRGiW_YALlpLX7ae-sdBq7SS3xT3X2Q&s', 'stomach', 130),
            ('Simethicone', 'Relieves bloating and gas discomfort.', 6.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSWKd9xbnNgfewAEc3id6_NpdYNgXV6nYMxYA&s', 'stomach', 140),
            ('Acyclovir', 'Antiviral for herpes and shingles treatment.', 19.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRIlxCA39c4EhREXi89Gj9CgXpoRh_tcEX5fg&s', 'antiviral', 35),
            ('Oseltamivir', 'Treats influenza (flu) by reducing symptoms.', 24.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbSQAiykyfUlCdITD_luq0ROaTkKTdkf_Drg&s', 'antiviral', 30),
            ('Mupirocin Ointment', 'Antibacterial ointment for skin infections.', 10.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbpZ4jMckLc0wJpvaZmysIQv_BGIrOj5WgRw&s', 'skin', 70),
            ('Ketoconazole Shampoo', 'Treats dandruff and fungal scalp infections.', 12.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTObKymeUHRoYbfClV_D6WlRWZ4i83V1up-pA&s', 'skin', 60),
            ('Diclofenac Gel', 'Topical gel for joint and muscle pain relief.', 11.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnBSS47RsNQ6tktiwct7lW0OpONfVdESeNmg&s', 'pain', 130),
            ('Montelukast', 'Prevents asthma and treats seasonal allergies.', 15.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRuDkUvs9uwTMWhXww2-xQg4RCNdbGSuDd7xw&s', 'respiratory', 50),
            ('Furosemide', 'Diuretic for treating edema and hypertension.', 8.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQA1hpsvyWB5aV4sSVS5Vy0XSTFxfHYuxQp6g&s', 'heart', 90),
            ('Warfarin', 'Blood thinner to prevent blood clots.', 10.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR4UxPpUkrN60GQAwqneS7MyYZroRth-70p6Q&s', 'heart', 80),
            ('Clopidogrel', 'Prevents heart attack and stroke in at-risk patients.', 12.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnDCP4Ale_KEylSJgQ9StEEVogX3Sda1j-GA&s', 'mental_health', 70),
            ('Escitalopram', 'Treats depression and generalized anxiety disorder.', 17.75, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ54RZmDCQlvIz3e_brom4ZfhOPe5s6-NEj2A&s', 'mental_health', 60),
            ('Alprazolam', 'Manages anxiety and panic disorders.', 14.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxt-uGAi-km1X2H4oUTunahriCfY-CGWN_fw&s', 'mental_health', 55),
            ('Hydrocortisone Cream', 'Reduces inflammation and itching from skin conditions.', 9.50, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSk9Upl1oY5ewE3ySLAXOw0UhwO2cLC3t2cAw&s', 'mental_health', 85),
            ('Cetirizine', 'Antihistamine for allergy symptoms with long-lasting relief.', 7.25, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGk7ZxFO5sH_PsBmK9pGh0Ll0_pB2UbHb-MQ&s', 'mental_health', 130),
            ('Sunscreen SPF 50', 'Protects skin from UV rays.', 18.00, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAkp0sD14ZrtFcfdgRhUM_RngbwpbWNLIY-g&s', 'mental_health', 50),
            ('Budesonide Inhaler', 'Prevents asthma attacks with anti-inflammatory action.', 28.99, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2L6Q_FJc1-bfdrR7Y9GcFzwVSQvo9x904-A&s', 'mental_health', 20),
            
        
        ]
        

        for product in products:
            name, description, price, image_url, category, stock_quantity = product
            # Check if product exists
            c.execute('SELECT id FROM products WHERE name = ?', (name,))
            existing = c.fetchone()
            if existing:
                # Update existing product
                c.execute('''UPDATE products SET description = ?, price = ?, image_url = ?, category = ?, stock_quantity = ?
                             WHERE name = ?''',
                          (description, price, image_url, category, stock_quantity, name))
                logger.debug(f"Updated {name} in database")
            else:
                # Insert new product
                c.execute('''INSERT INTO products (name, description, price, image_url, category, stock_quantity)
                             VALUES (?, ?, ?, ?, ?, ?)''',
                          (name, description, price, image_url, category, stock_quantity))
                logger.debug(f"Inserted {name} into database")
        conn.commit()
        logger.debug("Database seeded successfully")
    except sqlite3.Error as e:
        logger.error(f"Database seeding failed: {e}")
    finally:
        conn.close()

init_db()
seed_data()

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('SELECT id, name, description, price, image_url, category, stock_quantity FROM products')
        products = [
            {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'image_url': row[4],
                'category': row[5],
                'stock_quantity': row[6]
            } for row in c.fetchall()
        ]
        conn.close()
        return jsonify(products)
    except sqlite3.Error as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_name>/', methods=['GET'])
def get_product(product_name):
    try:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('SELECT id, name, description, price, image_url, category, stock_quantity FROM products WHERE name = ?', (product_name,))
        row = c.fetchone()
        conn.close()
        if row:
            product = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'image_url': row[4],
                'category': row[5],
                'stock_quantity': row[6]
            }
            return jsonify(product)
        return jsonify({'error': 'Product not found'}), 404
    except sqlite3.Error as e:
        logger.error(f"Error fetching product {product_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_name>/', methods=['PATCH'])
def update_product_stock(product_name):
    try:
        data = request.get_json()
        stock_quantity = data.get('stock_quantity')
        if stock_quantity is None or not isinstance(stock_quantity, int) or stock_quantity < 0:
            return jsonify({'error': 'Invalid stock_quantity'}), 400
        
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('UPDATE products SET stock_quantity = ? WHERE name = ?', (stock_quantity, product_name))
        if c.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
        conn.commit()
        conn.close()
        logger.info(f"Updated stock for {product_name}: {stock_quantity}")
        return jsonify({'message': 'Stock updated successfully'})
    except sqlite3.Error as e:
        logger.error(f"Error updating stock for {product_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_name>/comments', methods=['GET'])
def get_comments(product_name):
    try:
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('SELECT id, product_name, reviewer_name, reviewer_email, rating, comment_text, created_at FROM comments WHERE product_name = ?', (product_name,))
        comments = [
            {
                'id': row[0],
                'product_name': row[1],
                'reviewer_name': row[2],
                'reviewer_email': row[3],
                'rating': row[4],
                'comment_text': row[5],
                'created_at': row[6]
            } for row in c.fetchall()
        ]
        conn.close()
        return jsonify(comments)
    except sqlite3.Error as e:
        logger.error(f"Error fetching comments for {product_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_name>/comments', methods=['POST'])
def add_comment(product_name):
    try:
        data = request.get_json()
        reviewer_name = data.get('reviewer_name')
        reviewer_email = data.get('reviewer_email')
        rating = data.get('rating')
        comment_text = data.get('comment_text')
        
        if not all([reviewer_name, rating, comment_text]) or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Invalid comment data'}), 400
        
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        created_at = datetime.now().isoformat()
        c.execute('INSERT INTO comments (product_name, reviewer_name, reviewer_email, rating, comment_text, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                  (product_name, reviewer_name, reviewer_email, rating, comment_text, created_at))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Comment added successfully'})
    except sqlite3.Error as e:
        logger.error(f"Error adding comment for {product_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products/<product_name>/comments/<int:id>', methods=['DELETE'])
def delete_comment(product_name, id):
    try:
        logger.info(f"Received DELETE request for comment ID {id} for product {product_name}")
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('DELETE FROM comments WHERE id = ? AND product_name = ?', (id, product_name))
        if c.rowcount == 0:
            conn.close()
            logger.warning(f"Comment not found: ID {id} for product {product_name}")
            return jsonify({'error': 'Comment not found'}), 404
        conn.commit()
        conn.close()
        logger.info(f"Deleted comment: ID {id} for product {product_name}")
        return jsonify({
            'message': 'Comment deleted successfully',
            'id': id
        }), 200
    except sqlite3.Error as e:
        conn.close()
        logger.error(f"Error deleting comment ID {id} for product {product_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask app on port 5000")
    app.run(debug=True)
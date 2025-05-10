from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure SQLite database
db_path = os.path.join(os.path.dirname(__file__), 'contact_flask.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=True)
    agree_terms = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    logger.info("Creating database tables...")
    db.create_all()
    logger.info("Database tables created successfully")

# API endpoint to handle form or JSON submission (POST)
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        logger.info("Received POST request to /submit_contact")
        # Determine content type
        content_type = request.content_type
        if content_type and 'application/json' in content_type:
            data = request.get_json()
            logger.debug(f"JSON data: {data}")
        else:
            data = request.form
            logger.debug(f"Form data: {dict(data)}")

        # Extract fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = str(data.get('phone', '')).strip()  # Convert to string
        address = data.get('address', '').strip()
        message = data.get('message', '').strip()
        
        # Handle agreeTerms based on content type
        if content_type and 'application/json' in content_type:
            agree_terms = data.get('agreeTerms', False)
            if isinstance(agree_terms, str):
                agree_terms = agree_terms.lower() == 'on' or agree_terms.lower() == 'true'
        else:
            agree_terms = data.get('agreeTerms') == 'on'

        # Validate required fields
        if not all([name, email, phone, address]):
            logger.warning("Validation failed: Missing required fields")
            return jsonify({'error': 'Name, email, phone, and address are required'}), 400
        
        if not agree_terms:
            logger.warning("Validation failed: Terms not agreed")
            return jsonify({'error': 'You resonmust agree to the terms'}), 400

        # Basic email format check
        if '@' not in email or '.' not in email:
            logger.warning(f"Invalid email format: {email}")
            return jsonify({'error': 'Invalid email format'}), 400

        # Create new contact entry
        contact = Contact(
            name=name,
            email=email,
            phone=phone,
            address=address,
            message=message or None,  # Store None if empty
            agree_terms=agree_terms
        )

        # Add to database and commit
        db.session.add(contact)
        db.session.commit()
        logger.info(f"Contact saved: {name}, {email}")

        return jsonify({
            'message': 'Contact information saved successfully',
            'data': {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'message': message,
                'agree_terms': agree_terms
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving contact: {str(e)}")
        return jsonify({'error': 'Server error: Failed to save contact'}), 500

# API endpoint to retrieve all contact submissions or filter by email (GET)
@app.route('/submit_contact', methods=['GET'])
def get_contacts():
    try:
        logger.info("Received GET request to /submit_contact")
        # Get query parameters for filtering (optional)
        email = request.args.get('email')
        
        # Query contacts
        query = Contact.query
        if email:
            query = query.filter_by(email=email)
        
        contacts = query.all()
        
        # Format response
        contacts_data = [
            {
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'address': contact.address,
                'message': contact.message,
                'agree_terms': contact.agree_terms,
                'created_at': contact.created_at.isoformat()
            } for contact in contacts
        ]
        
        logger.info(f"Retrieved {len(contacts_data)} contact entries")
        return jsonify({
            'message': 'Contacts retrieved successfully',
            'data': contacts_data
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving contacts: {str(e)}")
        return jsonify({'error': 'Server error: Failed to retrieve contacts'}), 500

# API endpoint to retrieve a single contact by ID (GET)
@app.route('/submit_contact/<int:id>', methods=['GET'])
def get_contact_by_id(id):
    try:
        logger.info(f"Received GET request for contact ID {id}")
        # Find contact by ID
        contact = Contact.query.get(id)
        
        if not contact:
            logger.warning(f"Contact not found: ID {id}")
            return jsonify({'error': 'Contact not found'}), 404

        # Format response
        contact_data = {
            'id': contact.id,
            'name': contact.name,
            'email': contact.email,
            'phone': contact.phone,
            'address': contact.address,
            'message': contact.message,
            'agree_terms': contact.agree_terms,
            'created_at': contact.created_at.isoformat()
        }
        
        logger.info(f"Retrieved contact: ID {id}, {contact.email}")
        return jsonify({
            'message': 'Contact retrieved successfully',
            'data': contact_data
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving contact ID {id}: {str(e)}")
        return jsonify({'error': 'Server error: Failed to retrieve contact'}), 500

# API endpoint to delete a contact submission (DELETE)
@app.route('/submit_contact/<int:id>', methods=['DELETE'])
def delete_contact(id):
    try:
        logger.info(f"Received DELETE request for contact ID {id}")
        # Find contact by ID
        contact = Contact.query.get(id)
        
        if not contact:
            logger.warning(f"Contact not found: ID {id}")
            return jsonify({'error': 'Contact not found'}), 404

        # Delete contact
        db.session.delete(contact)
        db.session.commit()
        logger.info(f"Contact deleted: ID {id}")

        return jsonify({
            'message': 'Contact deleted successfully',
            'id': id
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting contact ID {id}: {str(e)}")
        return jsonify({'error': 'Server error: Failed to delete contact'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask app on port 5001")
    app.run(debug=True, port=5001)
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

app = Flask(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)

class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.String)
    email = db.Column(db.String)
    linkedId = db.Column(db.Integer)
    linkPrecedence = db.Column(db.String)
    createdAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updatedAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deletedAt = db.Column(db.DateTime)

@app.route('/identify', methods=['POST'])
def identify_contact():
    data = request.get_json()
    email = data.get('email')
    phoneNumber = data.get('phoneNumber')

    with app.app_context():
        try:
            def get_primary_contact(email=None, phone_number=None):
                if email:
                    primary_contact = Contact.query.filter_by(email=email).first()
                else:
                    primary_contact = Contact.query.filter_by(phoneNumber=phone_number).first()

                while primary_contact and primary_contact.linkedId:
                    primary_contact = Contact.query.filter_by(id=primary_contact.linkedId).first()
                return primary_contact

            def find_last_contact(primary_contact):
                current_contact = primary_contact
                while primary_contact:
                    current_contact = primary_contact
                    primary_contact = Contact.query.filter_by(linkedId=primary_contact.id).first()
                return current_contact

            def gather_contacts(primary_contact):
                contacts = []
                current_contact = primary_contact
                while current_contact:
                    contacts.append(current_contact)
                    current_contact = Contact.query.filter_by(linkedId=current_contact.id).first()
                return contacts

            def prepare_response_data(contacts):
                primary_contact = None
                secondary_contacts = []
                emails = []
                phone_numbers = []
                secondary_contact_ids = []

                for contact in contacts:
                    if contact.linkPrecedence == "primary":
                        primary_contact = contact
                        if contact.email and contact.email not in emails:
                            emails.insert(0, contact.email)
                        if contact.phoneNumber and contact.phoneNumber not in phone_numbers:
                            phone_numbers.insert(0, contact.phoneNumber)
                    else:
                        secondary_contacts.append(contact)
                        if contact.email and contact.email not in emails:
                            emails.append(contact.email)
                        if contact.phoneNumber and contact.phoneNumber not in phone_numbers:
                            phone_numbers.append(contact.phoneNumber)
                        secondary_contact_ids.append(contact.id)

                return {
                    "primaryContactId": primary_contact.id if primary_contact else None,
                    "emails": emails,
                    "phoneNumbers": phone_numbers,
                    "secondaryContactIds": secondary_contact_ids
                }

            primary_contact = None
            contacts = []

            if email and not phoneNumber:
                primary_contact = get_primary_contact(email=email)
                if not primary_contact:
                    new_contact = Contact(email=email, linkPrecedence="primary")
                    db.session.add(new_contact)
                    db.session.commit()
                    primary_contact = new_contact

            elif phoneNumber and not email:
                primary_contact = get_primary_contact(phone_number=phoneNumber)
                if not primary_contact:
                    new_contact = Contact(phoneNumber=phoneNumber, linkPrecedence="primary")
                    db.session.add(new_contact)
                    db.session.commit()
                    primary_contact = new_contact

            elif email and phoneNumber:
                primary_contact_by_email = get_primary_contact(email=email)
                primary_contact_by_phone = get_primary_contact(phone_number=phoneNumber)

                if not primary_contact_by_email and primary_contact_by_phone:
                    latest_contact = find_last_contact(primary_contact_by_phone)
                    new_contact = Contact(email=email, linkPrecedence="secondary", linkedId=latest_contact.id, phoneNumber=phoneNumber)
                    db.session.add(new_contact)
                    db.session.commit()
                    primary_contact = primary_contact_by_phone

                elif primary_contact_by_email and not primary_contact_by_phone:
                    latest_contact = find_last_contact(primary_contact_by_email)
                    new_contact = Contact(phoneNumber=phoneNumber, linkPrecedence="secondary", linkedId=latest_contact.id, email=email)
                    db.session.add(new_contact)
                    db.session.commit()
                    primary_contact = primary_contact_by_email

                elif primary_contact_by_email == primary_contact_by_phone:
                    primary_contact = primary_contact_by_phone

                else:
                    current_top = primary_contact_by_email
                    latest_contact = find_last_contact(primary_contact_by_email)
                    primary_contact_by_phone.linkedId = latest_contact.id
                    primary_contact_by_phone.linkPrecedence = "secondary"
                    db.session.commit()
                    primary_contact = current_top

            if primary_contact:
                contacts = gather_contacts(primary_contact)

            if contacts:
                response_data = {
                    "contact": prepare_response_data(contacts)
                }
                return jsonify(response_data), 200
            else:
                return jsonify({"message": "No contact found"}), 404

        except IntegrityError:
            db.session.rollback()
            return jsonify({"message": "Database integrity error"}), 500

        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()

import os
from dotenv import load_dotenv

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

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
    createdAt = db.Column(db.DateTime)
    updatedAt = db.Column(db.DateTime)
    deletedAt = db.Column(db.DateTime)

@app.route('/identify', methods=['POST'])
def identify_contact():
    data = request.get_json()
    email = data.get('email')
    phoneNumber = data.get('phoneNumber')

    with app.app_context():

        def get_primary_contact_by_email(email):
            primary_contact = Contact.query.filter_by(email=email, linkPrecedence='primary').first()
            if not primary_contact:
                secondary_contact = Contact.query.filter_by(email=email).first()
                if secondary_contact:
                    primary_contact = Contact.query.filter_by(id=secondary_contact.linkedId).first()
            return primary_contact

        def get_primary_contact_by_phone(phone_number):
            primary_contact = Contact.query.filter_by(phoneNumber=phone_number, linkPrecedence='primary').first()
            if not primary_contact:
                secondary_contact = Contact.query.filter_by(phoneNumber=phone_number).first()
                if secondary_contact:
                    primary_contact = Contact.query.filter_by(id=secondary_contact.linkedId).first()
            return primary_contact

        def gather_contacts(primary_contact):
            contacts = Contact.query.filter_by(linkedId=primary_contact.id).all()
            contacts.append(primary_contact)
            return contacts

        def prepare_response_data(contacts):
            primary_contact = None
            secondary_contacts = []
            emails = []
            phoneNumbers = []
            secondaryContactIds = []

            for contact in contacts:
                if contact.linkPrecedence == "primary":
                    primary_contact = contact
                    if contact.email and contact.email not in emails:
                        emails.insert(0, contact.email)
                    if contact.phoneNumber and contact.phoneNumber not in phoneNumbers:
                        phoneNumbers.insert(0, contact.phoneNumber)
                else:
                    secondary_contacts.append(contact)
                    if contact.email and contact.email not in emails:
                        emails.append(contact.email)
                    if contact.phoneNumber and contact.phoneNumber not in phoneNumbers:
                        phoneNumbers.append(contact.phoneNumber)
                    secondaryContactIds.append(contact.id)

            response_data = {
                "primaryContactId": primary_contact.id if primary_contact else None,
                "emails": emails,
                "phoneNumbers": phoneNumbers,
                "secondaryContactIds": secondaryContactIds
            }

            return response_data

        primaryContract = None
        contacts = []

        if email and not phoneNumber:
            primaryContract = get_primary_contact_by_email(email)
            if not primaryContract:
                try:
                    newContact = Contact(email=email,linkPrecedence="primary")
                    db.session.add(newContact)
                    db.session.commit()
                    primaryContract = newContact
                except IntegrityError as e:
                    db.session.rollback()
                    raise e
                
        elif phoneNumber and not email:
            primaryContract = get_primary_contact_by_phone(phoneNumber)
            if not primaryContract:
                try:
                    newContact = Contact(phoneNumber=phoneNumber,linkPrecedence="primary")
                    db.session.add(newContact)
                    db.session.commit()
                    primaryContract = newContact
                except IntegrityError as e:
                    db.session.rollback()
                    raise e

        elif email and phoneNumber:
            pass
        
        if primaryContract:
            contacts = gather_contacts(primaryContract)

        if contacts:
            response_data = {
                "contact": prepare_response_data(contacts)
            }
            return jsonify(response_data), 200
        else:
            return jsonify({"message": "No contact found"}), 404

if __name__ == '__main__':
    app.run()


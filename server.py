import os
from dotenv import load_dotenv

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

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

    response_data = {
        "email": email,
        "phoneNumber": phoneNumber,
    }

    return response_data


if __name__ == '__main__':
    app.run()


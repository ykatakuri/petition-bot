from os import environ

import psycopg2
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)


class Petitions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.Text, nullable=False)
    option_2 = db.Column(db.Text, nullable=False)
    countdown = db.Column(db.Integer, nullable=False)
    is_closed = db.Column(db.Text, default=False)

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "option_1": self.option_1,
            "option_2": self.option_2,
            "countdown": self.countdown,
            "is_closed": self.is_closed
        }
    
db.create_all()

# create a new petition
@app.route('/api/petitions', methods=['POST'])
def create_petition():
    try:
        data = request.get_json()
        petition = Petitions(
            title=data['title'],
            content=data['content'],
            option_1=data['option_1'],
            option_2=data['option_2'],
            countdown=data['countdown']
        )
        db.session.add(petition)
        db.session.commit()
        return make_response(jsonify({"message": "Petition created successfully"}), 201)
    except Exception as e:
        return make_response(jsonify({"message": f"Something went wrong - {e}"}), 500)
    
# get all petitions 
@app.route('/api/petitions', methods=['GET'])
def get_petitions():
    try:
        petitions = Petitions.query.all()
        if not petitions:
            return make_response(jsonify({"message": "No petitions found"}), 404)
        
        return make_response(jsonify({"petitions": [petition.json() for petition in petitions]}), 200)
    except Exception as e:
        return make_response(jsonify({"message": f"Something went wrong - {e}"}), 500)
    
# get a single petition
@app.route('/api/petitions/<int:id>', methods=['GET'])
def get_petition(id):
    try:
        petition = Petitions.query.filter_by(id=id).first()
        if not petition:
            return make_response(jsonify({"message": "Petition not found"}), 404)
        
        return make_response(jsonify({"petition": petition.json()}), 200)
    except Exception as e:
        return make_response(jsonify({"message": f"Something went wrong - {e}"}), 500)
    
# update a petition
@app.route('/api/petitions/<int:id>', methods=['PUT'])
def update_petition(id):
    try:
        data = request.get_json()
        petition = Petitions.query.filter_by(id=id).first()
        if not petition:
            return make_response(jsonify({"message": "Petition not found"}), 404)
        
        petition.title = data['title']
        petition.content = data['content']
        petition.option_1 = data['option_1']
        petition.option_2 = data['option_2']
        petition.countdown = data['countdown']
        petition.is_closed = data['is_closed']

        db.session.commit()
        return make_response(jsonify({"message": "Petition updated successfully"}), 200)
    except Exception as e:
        return make_response(jsonify({"message": f"Something went wrong - {e}"}), 500)


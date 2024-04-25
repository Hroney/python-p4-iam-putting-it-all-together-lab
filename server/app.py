#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        try:
            data = request.get_json()
            user = User(username=data['username'])
            user.password_hash = data['password']
            user.bio = data['bio']
            user.image_url = data['image_url']
            session['user_id'] = user.id
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), 201
        except KeyError as e:
            return {'error': str(e)}, 422
    pass

class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict()
        else:
            return {'message': '401: Not Authorized'}, 401
    pass

class Login(Resource):

    def post(self):
        try:
            user = User.query.filter(User.username == request.get_json()['username']).first()
            session['user_id'] = user.id
            return user.to_dict()
        except Exception as e:
            return {'error': str(e)}, 401
    pass

class Logout(Resource):
    
    def delete(self):
        try:
            session['user_id'] = None
            return {}, 401
        except Exception as e:
            return {"error": str(e)}, 401

class RecipeIndex(Resource):

    def get(self):
        if session['user_id']:
            recipes = Recipe.query.all()
            return [recipe.to_dict() for recipe in recipes], 200
        else:
            return {"error": "Not logged in"}, 401
        
    def post(self):
        try:
            if session['user_id']:
                new_recipe = Recipe(
                    title = request.get_json()['title'],
                    instructions = request.get_json()['instructions'],
                    minutes_to_complete = request.get_json()['minutes_to_complete'],
                    user_id = session['user_id']
                )
                db.session.add(new_recipe)
                db.session.commit()
                
                return new_recipe.to_dict(), 201
            else:
                return {'error': 'Not Logged In'}, 401
        except Exception as e:
            return {'error': str(e)}, 422
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
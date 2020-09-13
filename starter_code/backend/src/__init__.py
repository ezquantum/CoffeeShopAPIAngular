import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

class Error(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

#Recreate the database
# db_drop_and_create_all()

## ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():

    try:
        drinks = Drink.query.all()
        menu = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': menu,
        }), 200

    except:
        abort(500)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_detail(token):

    try:
        drinks = Drink.query.all()
        menu = [drink.long() for drink in drinks]

        return jsonify({
            'success': True, 
            'drinks': menu
        }), 200
    except:
        abort(500)

    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
#Make a new drink
    try:
        #get response
        data = request.get_json()
        title = data.get('title', None)
        recipe = data.get('recipe', None)
        
        #insert
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        #return success
        return jsonify({
            'success': True,
            'drinks': drink.long(),
        }), 200
        
    except Exception:
        abort(422)


    '''
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, drink_id):


    data = request.get_json()
    title = data.get('title', None)

    drink = Drink.query.filter_by(id=drink_id).one_or_none()


    if drink is None:
        abort(404)

    if title is None:
        abort(400)

    try:
        drink.title = title
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()],
        })
    except:
        abort(422)


    '''
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):

    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'deleted': drink_id,
        })
    except:
        abort(422)


    ## Error Handling
    '''
    Example error handling for unprocessable entity
    '''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

    '''
    @TODO implement error handlers using the @app.errorhandler(error) decorator
        each error handler should return (with approprate messages):
                jsonify({
                        "success": False, 
                        "error": 404,
                        "message": "resource not found"
                        }), 404

    '''

@app.errorhandler(404)
def resource_not_found(error):

    return jsonify({
        "success": False,
        "error": 404,
        "message": "Page not found"
    }), 404

    '''
    @TODO implement error handler for 404
        error handler should conform to general task above 
    '''

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

    '''
    @TODO implement error handler for AuthError
        error handler should conform to general task above 
    '''

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Server error"
    }), 500

@app.errorhandler(AuthError)
def handle_auth_error(exception):
    response = jsonify(exception.error)
    response.status_code = exception.status_code
    return response
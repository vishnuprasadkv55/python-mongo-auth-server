from app.auth import email
from app.auth.email import send_mail
from flask.json import jsonify
from . import auth
from app.config import db
from .services import forgot_password, login_user, refresh_current_token, register_user, resend_verification_code, save_new_password, verify_user, token_required
from flask import request, abort

VERIFICATION_CODE_LENGTH = 5


@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    response = register_user(data)
    if response["status"] == 'failed':
        abort(406, {'message': 'userExistException'})
    else:
        return response


@auth.route('/verify', methods=['POST'])
def verify():
    data = request.json
    response = verify_user(data)
    if response['status'] == 'failed':
        abort(406, {'message:' + response['exception']})
    else:
        return {"message": "success"}


@auth.route('/forgot', methods=['POST'])
def forgot():
    data = request.json
    response = forgot_password(data)
    if response['status'] == "success":
        return {"message": response['status']}
    elif response['status'] == 'failed':
        abort(403, {'message:' + response['exception']})
    else:
        abort(403, {'message:forbdden'})


@auth.route('/confirm', methods=['post'])
def confirm():
    data = request.json
    response = save_new_password(data)
    if response['status'] == 'success':
        return {"message": response['status']}
    elif response['status'] == 'failed':
        abort(403, {'message:' + response['exception']})
    else:
        abort(403, {'message:forbdden'})


@auth.route('/resend', methods=['POST'])
def resend():
    data = request.json
    response = resend_verification_code(data)
    if response['status'] == 'success':
        return {"message": response["status"]}
    else:
        abort(403, {'message': response['status']})

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    response = login_user(data)
    if response['status'] == 'success':
        return response
    else:
        abort(403, response)

@auth.route('/refreshToken', methods=['POST'])
def refresh():
    data = request.json
    response = refresh_current_token(data)
    if response['status'] == 'success':
        return response
    else:
        abort(403, response)

@auth.route('/api', methods=['POST'])
@token_required
def get_api():
    return {
        'status': 'success',
        'message': 'hello'
    }

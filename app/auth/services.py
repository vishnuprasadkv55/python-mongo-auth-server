from app.utils.dict import dotdict
from .email import send_mail
from app.auth.email import send_mail
from . import auth
from app.config import db
import datetime
import bcrypt
import string
import secrets
import os
import jwt
from datetime import datetime, timedelta
users = db.users
temp_users = db.temp_users
access_tokens = db.access_tokens
refresh_tokens= db.refresh_tokens
APP_SECRET_KEY = 'APP_SECRET_KEY'
VERIFICATION_CODE_LENGTH = 'VERIFICATION_CODE_LENGTH'

def send_verification_mail(mail_data):
    send_mail(mail_data)


def register_user(data):
    verification_code = ''.join(secrets.choice(
        string.ascii_lowercase) for i in range(int(os.environ.get(VERIFICATION_CODE_LENGTH))))
    hashed_password = bcrypt.hashpw(
        data["password"].encode('utf8'), bcrypt.gensalt())
    verification_data = {
        "username": data["username"],
        "verification_code": verification_code
    }

    userExist = users.find_one({"username": data['username']})
    if userExist:
        return {"status": 'failed', "exception": "userExistException"}
    else:
        user_id = users.insert_one({**data,
                                    "password": hashed_password,
                                    "active": False}).inserted_id
        temp_user_id = temp_users.insert_one(verification_data).inserted_id
        send_verification_mail({**verification_data, "email": data["email"],
                                "username": data["username"]})
        return {"status": "success", "data": data}


def verify_user(data):
    verification = {
        "username": data["username"],
        "code": data["code"]
    }

    user = temp_users.find_one({"username": verification['username']})
    if user:
        if user["verification_code"] == verification['code']:
            users.find_one_and_update({"username": verification['username']}, {
                                      "$set": {"active": True}})
            temp_users.find_one_and_delete(
                {"username": verification['username']})
            return {"status": "success"}
        else:
            return {"status": 'failed', "exception": "wrongVerificationCode"}
    else:
        return {"status": 'failed', "exception": "forbiddenError"}


def forgot_password(data):
    userExist = temp_users.find_one({"username": data["username"]})
    if userExist:
        return {"status": 'failed', "exception": "verificationAlreadyInProgress"}
    else:
        user = users.find_one({"username": data["username"]})
        if user and user['active']:
            verification_code = ''.join(secrets.choice(
                string.ascii_lowercase) for i in range(int(os.environ.get(VERIFICATION_CODE_LENGTH))))
            send_verification_mail({**user, "verification_code": verification_code})
            temp_user_id = temp_users.insert_one({**data, "verification_code": verification_code})
            return {"status": "success"}
        else:
            return {"status": 'failed', "exception": "userDoesNotExist"}

def save_new_password(data):
    user = temp_users.find_one({"username": data['username']})
    if user:
        if user['verification_code'] == data['code']:
            hashed_password = bcrypt.hashpw(data['password'].encode('utf8'), bcrypt.gensalt())
            users.find_one_and_update({'username': data['username']}, {"$set": {'password': hashed_password}})
            temp_users.find_one_and_delete({'username': data['username']})
            return {"status": "success"}
        else:
            return {"status": 'failed', "exception": "wrongVerificationCode"}
    else:
        return {"status": 'failed', "exception": "forbiddenError"}

def resend_verification_code(data):
    user = users.find_one({"username": data['username']})
    temp_user = temp_users.find_one({"username": data['username']})
    if user and temp_user:
        send_verification_mail({**user, "verification_code": temp_user['verification_code'] })
        return {"status": "success"}
    else:
        return {"status": 'failed', "exception": "forbiddenError"}
        
def jwt_encode(payload, time_delta):
    payload['iat'] = datetime.utcnow()
    payload['exp'] = datetime.utcnow() + time_delta
    return jwt.encode(
        payload,
        os.environ.get(APP_SECRET_KEY),
        algorithm='HS256'
    )
def jwt_decode(token): 
    try: 
        payload = jwt.decode(token, os.environ.get(APP_SECRET_KEY), algorithms="HS256")
        return {"status": "success", "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"status": "failed", "exception": 'signatureExpired'}
    except jwt.InvalidTokenError:
        return {"status": "failed", "exception": 'invalidToken'}


def login_user(data):
    user = users.find_one({"username": data["username"]})
    if user is None:
        return {"status": 'failed', 'exception': 'userDoesNotExist'}
    else:
        checkpw = bcrypt.checkpw(data['password'].encode('utf8'), user['password'])
        print('hey')
        if checkpw:
            key = os.environ.get(APP_SECRET_KEY)
            payload = {
                "sub": str(user['_id']),
                "username": user["username"],
            }
            access_token = jwt_encode(payload, timedelta(days=0, minutes=10))
            refresh_token = jwt_encode(payload, timedelta(days=0, minutes=30))
            try: 
                family_id = access_tokens.insert({"access_token": access_token, "valid": True})
                refresh_tokens.insert_one({"family_id": family_id, "refresh_token": refresh_token, "valid": True})
            except Exception as exception:
                print(exception)
            return {'status': 'success', 'access_token': access_token, 'refresh_token': refresh_token }
        else:
            return {"status": 'failed', 'exception': 'authenticationFailed'}
    
def refresh_current_token(data):
    refresh_token = refresh_tokens.find_one({'refresh_token': data['refresh_token']})
    if refresh_token is None:
        return {"status": 'failed', "exception": "refreshTokenForbiddenError"}
    else:        
        access_token = access_tokens.find_one({'_id': refresh_token['family_id'], 'valid': True})
        if access_token is None:
            return {"status": 'failed', "exception": "accessTokenForbiddenError"}
        elif refresh_token['valid'] is not True:
            access_tokens.delete_many({'_id': refresh_token['family_id']})
            refresh_tokens.delete_many({'family_id': refresh_token['family_id']})
            return {'status': 'failed', 'exception': 'malpractice'}
        elif access_token and refresh_token['valid']:
            refresh_tokens.update_one({'_id': refresh_token["_id"]}, {'$set': {'valid': False}})
            # old_refresh_token_payload = jwt_decode(data['refresh_token'])
            payload_response = jwt_decode(access_token['access_token'])
            if payload_response['status'] == 'failed':
                access_tokens.delete_many({'_id': refresh_token['family_id']})
                refresh_tokens.delete_many({'family_id': refresh_token['family_id']})
                return payload_response

            payload = {
                "sub": payload_response['payload']['sub'],
                "username": payload_response['payload']['username'],
            }
            
            new_refresh_token = jwt_encode(payload, timedelta(days=0, minutes=30))
            new_access_token = jwt_encode(payload, timedelta(days=0, minutes=10))
            # family_id = access_tokens.insert({"access_token": new_access_token, "valid": True})
            access_tokens.update_one({'_id': refresh_token['family_id']}, {'$set': {"access_token": new_access_token}})
            refresh_tokens.insert_one({"family_id": refresh_token['family_id'], 'refresh_token': new_refresh_token,'access_token': new_access_token, 'valid': True})
            return {'status': 'success', 'access_token': new_access_token, 'refresh_token': new_refresh_token }
        
    
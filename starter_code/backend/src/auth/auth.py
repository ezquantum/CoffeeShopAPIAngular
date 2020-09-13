import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'coffestack.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee'


## AuthError Exception

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


### = Done


#Defined global method
def get_token_auth_header():
    #Attempt to retrieve header from request
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'Unauthorized Request', 
            'description': 'Please log-in with the correct credentials.'
            }, 401)
    
    #Splits the header into two parts
    auth_header = request.headers['Authorization']
    header_parts= auth_header.split(' ')
    if len(header_parts) !=2:
        raise AuthError({
            'code': 'Unauthorized Request', 
            'description': 'Please log-in with the correct credentials.'
            }, 401)

    elif header_parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'Unauthorized Request', 
            'description': 'Please log-in with the correct credentials.'
            }, 401)
    #Returns the token portion of header
    return header_parts [1]



def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
            }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code':'unauthorized',
            'description': 'Permission not found.'
    }, 403)

    return True

def verify_decode_jwt(token):
    '''
    Verifies and decodes the jwt from the given token
    '''

    # process key and header data
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)

    #fake
    rsa_key = {'kty': 'RSA', 
            'use': 'sig', 
            'n': '1Mu2yp5nToZjwO8JGoeV_ccBEDkbJ_aBRe1WJ-juJtcYOzyMgnGVujqv22WbjDj0blmJuP-EZ1ym0PzG2TIrnYk6mHsyVfjz-aQB7FBcTxl4CCnREN3gXQS2-6udmVGl0awZublowsFYP5vEfF_Go4_ir43RHMr_kxMQO4l-ipk28e1-ymOqsjyXv_ovtyNC0eS7_f1x2dMIRZ6_5ck5V4BxW57hm-u59WjM2O0rCYbgO_gOqTyXlYN0lQ35sECutCKgRmfWjI-Q8huSNec6srUDQ3V3YlKhW5Wu23dOYyLtav8V6YvgsgM3R9LTHcKTvHfYDyVvkiyZa0Eg794Mfw', 
            'e': 'AQAB', 
            'kid': '9E2wuF5V9hhj1uMiQq0Dj' 
           }

    # Ensure that token header has the kid field

    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)
    
    for key in jwks['keys']:
       
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }




    if rsa_key:
        payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
        )
        print('payload is')
        print(payload)
        try:
            # decode token with the constants    
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            print(payload)
            return payload

        # raise errors
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, ' +
                'check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)

# def verify_decode_jwt(token):
#     #retrieve public key from Auth0
#     jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
#     jwks = json.loads(jsonurl.read())

#     # Retrieve data from header
#     unverified_header = jwt.get_unverified_header(token)

#     #Choose the KEY
#     rsa_key = {}
#     if 'kid' not in unverified_header:
#         raise AuthError({
#             'code':'invalid_header',
#             'description': 'Authorization malformed.'
#     }, 401)

#     for key in jwks['keys']:
#         if key['kid'] == unverified_header['kid']:
#             rsa_key = {
#                 'kty': key['kty'],
#                 'kid': key['kid'],
#                 'use': key['use'],
#                 'n': key['n'],
#                 'e': key['e']
#                 }

#     if rsa_key:
#         try:   
#             # USE THE KEY TO VALIDATE THE JWT
#             payload = jwt.decode(
#                 token,
#                 rsa_key,
#                 algorithms=ALGORITHMS,
#                 audience=API_AUDIENCE,
#                 issuer='https://' + AUTH0_DOMAIN + '/'
#             )
#             return payload
        
#         # raise errors for common exceptions
#         except jwt.ExpiredSignatureError:
#             raise AuthError({
#                 'code': 'token_expired',
#                 'description': 'Token expired.'
#                 }, 401)

#             except jwt.JWTClaimsError:
#                 raise AuthError({
#                     'code': 'invalid_claims',
#                     'description': 'Incorrect claims. Please, ' +
#                     'check the audience and issuer.'
#                     }, 401)
#             except Exception:
#                 raise AuthError({
#                     'code': 'invalid_header',
#                     'description': 'Unable to parse authentication token.'
#                     }, 400)
#                 raise AuthError({
#                     'code': 'invalid_header',
#                     'description': 'Unable to find the appropriate key.'
#                     }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


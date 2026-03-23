import jwt
import datetime

SECRET_KEY = "ini_adalah_secret_key_yang_sangat_panjang_dan_aman_sekali_123"

def generate_token():
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "user": "admin"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True, "OK"
    except jwt.ExpiredSignatureError:
        return False, "Token Expired"
    except Exception:
        return False, "Invalid Token"
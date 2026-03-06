from itsdangerous import URLSafeSerializer
from flask import current_app

def get_serializer():
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="url-id")

def encrypt_id(value):
    s = get_serializer()
    return s.dumps(value)

def decrypt_id(value):
    s = get_serializer()
    return s.loads(value)
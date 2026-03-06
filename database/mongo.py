from datetime import datetime
from pymongo import MongoClient

class ConexionMongo:

    cliente = MongoClient("mongodb://localhost:27017")
    db = cliente["threadline_logs"]
    coleccion_logs = db["bitacora_autenticacion"]

    @staticmethod
    def guardar_log(usuario=None, endpoint=None, ip=None, estado=None, metodo=None, url=None, datos=None):

        log = {
            "usuario": usuario,
            "endpoint": endpoint,
            "ip": ip,
            "estado": estado,
            "metodo": metodo,
            "url": url,
            "datos": datos,
            "fecha": datetime.utcnow()
        }

        ConexionMongo.coleccion_logs.insert_one(log)
# routes/merma.py
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from database.mysql import db
from securrity.middlerware import login_requerido, permiso_requerido, decrypt_url_id

merma = Blueprint("merma", __name__, url_prefix="/merma")

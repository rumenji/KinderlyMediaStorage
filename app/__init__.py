from flask import Flask
import os
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
app.config['ALLOWED_EXTENSIONS'] = {'xlsx'}

from app import routes
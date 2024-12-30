from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TimeField
from wtforms.validators import InputRequired

# Allowed extensions for uploaded files
ALLOWED_EXTENSIONS = ['xls', 'xlsx']

class FileUploadForm(FlaskForm):
    '''Validates a file is uploaded and it matches the allowed types''' 
    file = FileField('Choose a file below and click Schedule', validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, "Only .xls and .xlsx files are allowed!")])
    

class EditTimeForm(FlaskForm):
    '''Form to edit run time for an existing job'''
    new_time = TimeField('Enter a new departure time for the trip:', validators=[InputRequired("Time is required!")])
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import TimeField
from wtforms.validators import InputRequired

# Allowed extensions for spreadhseets
ALLOWED_EXTENSIONS = ['xls', 'xlsx']

class FileUploadForm(FlaskForm):       
    file = FileField('Choose a file below and click Schedule', validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, "Only .xls and .xlsx files are allowed!")])
    

class EditTimeForm(FlaskForm):
    new_time = TimeField('Enter a new departure time for the trip:', validators=[InputRequired("Time is required!")])
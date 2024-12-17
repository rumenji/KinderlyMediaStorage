from app import app
from flask import request, redirect, render_template
from werkzeug.utils import secure_filename
import os
from scheduler import allowed_file, read_excel, schedule_trips

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Process the file
            trips = read_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            schedule_trips(trips)
            return 'File uploaded and trips scheduled!'
    return render_template('upload.html')
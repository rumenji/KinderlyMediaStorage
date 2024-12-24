from flask import render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import os
from app import app
import datetime
from scheduler_set import schedule_trips, read_excel, scheduler, allowed_file

# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return redirect(request.url)
#         file = request.files['file']
#         if file.filename == '':
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             trips = read_excel(file_path)
#             schedule_trips(trips)
#             return render_template('upload.html', jobs=scheduler.get_jobs())
#     return render_template('upload.html', jobs=scheduler.get_jobs())
@app.route('/', methods=['GET'])
def list_jobs():
    return render_template('upload.html', jobs=scheduler.get_jobs())

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('list_jobs'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('list_jobs'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        trips = read_excel(file_path)
        schedule_trips(trips)
        os.remove(file_path)
    return redirect(url_for('list_jobs'))

@app.route('/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        return jsonify(success=True)
    except:
        return jsonify(success=False)

@app.route('/edit_job/<job_id>', methods=['POST'])
def edit_job(job_id):
    new_time = request.form.get('new_time')
    new_time = datetime.datetime.strptime(new_time, '%H:%M').time()
    now = datetime.datetime.now()
    new_run_date = datetime.datetime.combine(now.date(), new_time) - datetime.timedelta(hours=1)
    
    try:
        job = scheduler.get_job(job_id)
        if job:
            job.reschedule('date', run_date=new_run_date)
        return jsonify(success=True)
    except:
        return jsonify(success=False)
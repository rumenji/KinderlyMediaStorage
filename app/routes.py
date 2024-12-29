from flask import render_template, request, redirect, url_for, jsonify, flash, get_flashed_messages
from werkzeug.utils import secure_filename
import os
from app import app
import datetime
from scheduler_set import schedule_trips, read_excel, scheduler, allowed_file
from .forms import FileUploadForm, EditTimeForm
##############################################################################
# 404 route

@app.errorhandler(404) 
def not_found(e): 
  return render_template("404.html")

##############################################################################
# Homepage route

@app.route('/', methods=['GET'])
def list_jobs():
    get_flashed_messages()
    form = FileUploadForm()
    update_form = EditTimeForm()
    return render_template('upload.html', form=form, update_form=update_form, jobs=scheduler.get_jobs())

##############################################################################
# Post file upload route

@app.route('/upload', methods=['POST'])
def upload_file():
    form = FileUploadForm()
    
    if form.validate_on_submit():
        file = form.file.data
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)  
        try:
            trips = read_excel(file_path)
            response = schedule_trips(trips)
            os.remove(file_path)
            
            flash('Successfully scheduled all upcoming trips', 'success')

            if len(response) > 0:
                flash(f'The following trips departure times have already passed: {", ".join(response)}', 'warning')
            return redirect(url_for('list_jobs'))
        except Exception as e:
            os.remove(file_path)
            flash(str(e), 'danger')
        
    return render_template('upload.html', form=form)

##############################################################################
# Post delete scheduled job route

@app.route('/delete_job/<job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        flash(f'Trip {job_id} deleted!', 'warning')
        return redirect(url_for('list_jobs'))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('list_jobs'))

##############################################################################
# Post edit trip departure time for a scheduled job

@app.route('/edit_job/<job_id>', methods=['POST'])
def edit_job(job_id):
    update_form = EditTimeForm()
    if update_form.validate_on_submit():
        new_time = update_form.new_time.data
        # new_time = datetime.datetime.strptime(new_time, '%H:%M').time()
        now = datetime.datetime.now()
        new_run_date = datetime.datetime.combine(now.date(), new_time) - datetime.timedelta(hours=1)
        
        try:
            job = scheduler.get_job(job_id)
            if job:
                job.reschedule('date', run_date=new_run_date)
            flash(f'Trip {job_id} successfully edited!', 'success')
            return redirect(url_for('list_jobs'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('list_jobs'))
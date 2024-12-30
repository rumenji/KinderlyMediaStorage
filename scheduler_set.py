from openpyxl import load_workbook
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import requests
import datetime
import os
from dotenv import load_dotenv
from app import app

load_dotenv()

SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
X_VESTABOARD_API_KEY = os.getenv("X-VESTABOARD-API-KEY")
X_VESTABOARD_API_SECRET = os.getenv("X-VESTABOARD-API-SECRET")
DEFAULT_MESSAGE = os.getenv('DEFAULT_MESSAGE')
TITLE = os.getenv('TITLE')
SEARCH_VALUE = os.getenv('SEARCH_VALUE')

job_store = MemoryJobStore()
executors = {'default': ThreadPoolExecutor(20),
             'processpool': ProcessPoolExecutor(5)}
job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 90
}
scheduler = BackgroundScheduler(jobstores={'default': job_store}, executors=executors, job_defaults=job_defaults)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_excel(file_path):
    try:
        workbook = load_workbook(filename=file_path)
        sheet = workbook.active
        headers = [cell.value for cell in sheet[1]]
        required_columns = ['Start time LT', 'End time LT', 'Customer', 'Orig', 'Dest']
        if not all(col in headers for col in required_columns):
            raise Exception('The file does not have columns Start time LT, End time LT, Customer, Orig, or Dest')
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data.append(dict(zip(headers, row)))
        data = [trip for trip in data if trip['Customer type'] == 'Retail' and any([trip['Orig'] == SEARCH_VALUE, trip['Dest'] == SEARCH_VALUE])]
        if len(data) == 0:
            raise Exception('No matching trips in the uploaded file!')
        return data
    except Exception as e:
        raise e

# Limit name to 9 characters to fit on one line. If less than 9 - add spaces
def get_last_name(full_name):
    last_name = full_name.split()[-1]  # Get the last word (last name)
    last_name = last_name[:9]  # Limit to 9 characters
    last_name = last_name.ljust(9)  # Add spaces if less than 9 characters
    return last_name

CURRENTLY_DISPLAYED_TRIPS = [{
                    "msg": {
                    "style": {
                    "height": 1,
                    "width": 22
                    },
                    "template": TITLE
                },
                "time": datetime.datetime.strptime('11:59 pm', '%I:%M %p').time()
                }]

def format_vestaboard_message(message, time, last):
    try:
        global CURRENTLY_DISPLAYED_TRIPS
        if last:
            CURRENTLY_DISPLAYED_TRIPS = []  
        if len(CURRENTLY_DISPLAYED_TRIPS) > 1:
            now = datetime.datetime.now()
            upcoming_trips = [trip for trip in CURRENTLY_DISPLAYED_TRIPS if trip['time'] > now.time()]
            CURRENTLY_DISPLAYED_TRIPS = upcoming_trips
        
        CURRENTLY_DISPLAYED_TRIPS.append(
                {
                    "msg": {
                    "style": {
                    "height": 1,
                    "width": 22,
                    "align": "center"
                    },
                    "template": message
                },
                "time": time
                }
            )
        formatted_msg = requests.post(
            "https://vbml.vestaboard.com/compose",
            headers={"Content-Type": "application/json"},
            json={"components": [trip['msg'] for trip in CURRENTLY_DISPLAYED_TRIPS]}
        )
        
        if formatted_msg.status_code == 200:
            return formatted_msg.json()
        else:
            raise Exception(f"Failed to format message: {formatted_msg.status_code}")
    except Exception as e:
        raise e
    
    
def post_to_vestaboard(message, time, last):
    try:
        characters = format_vestaboard_message(message, time, last)
        if characters:
            response = requests.post(
                f"https://subscriptions.vestaboard.com/subscriptions/{SUBSCRIPTION_ID}/message",
                headers={"Content-Type": "application/json",
                        "x-vestaboard-api-key": X_VESTABOARD_API_KEY,
                        "x-vestaboard-api-secret": X_VESTABOARD_API_SECRET},
                json={"characters": characters}
            )
            if response.status_code != 200:
                raise Exception(f"Failed to update Vestaboard: {response.status_code}")
    except Exception as e:
        raise e

def schedule_trips(trips):
    if len(trips) == 0:
        raise Exception('No trips in the uploaded file!')
    
    last_departure = datetime.datetime.now().time()
    
    skipped_trips = []
    
    for trip in trips:
        file_departure = trip.get('Start time LT')
        file_arrival = trip.get('End time LT')
        file_customer = trip.get('Customer')
        file_pax = trip.get('Pax allocated')
        file_origin = trip.get('Orig')
        file_destination = trip.get('Dest')
        
        if not all([file_departure, file_arrival, file_customer, file_destination, file_origin]):
            raise Exception('The file does not have columns Start time LT, End time LT, Customer, Orig, or Dest')
        # If departure - show departure time, if arrival - show arrival time
        time_to_show = file_departure if file_origin == SEARCH_VALUE else file_arrival
        if file_pax != 0:
            try:
                customer_name = get_last_name(file_customer)
                departure_time = datetime.datetime.strptime(str(time_to_show), '%I:%M %p').time()
                now = datetime.datetime.now()
                departure = datetime.datetime.combine(now.date(), departure_time)
                
                delay = (departure - now).total_seconds()
                if delay > 0:
                    job_runtime = departure - datetime.timedelta(hours=1) if delay>3600 else now
                    job = scheduler.add_job(
                        post_to_vestaboard, 
                        'date', 
                        run_date=job_runtime,
                        args=[f"{customer_name} {file_origin[-3:]}-{file_destination[-3:]} {departure_time.strftime('%H%M')}", departure_time, False],
                        id=f"{file_customer}_{file_origin}_{file_destination}"
                    )
                    if last_departure < departure_time:
                        last_departure = departure_time

                else:
                    skipped_trips.append(f"{file_customer} at {departure_time}")
            except Exception as e:
                raise e
    try:  
        scheduler.add_job(
                    post_to_vestaboard, 
                    'date', 
                    run_date=datetime.datetime.combine(now.date(), last_departure) + datetime.timedelta(minutes=15),
                    args=[DEFAULT_MESSAGE, last_departure, True],
                    id="End"
                )
    except Exception as e:
        raise e
    
    return skipped_trips

scheduler.start()  # Start the scheduler
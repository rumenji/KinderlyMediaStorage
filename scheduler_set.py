from openpyxl import load_workbook
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import requests
import datetime
import os
from dotenv import load_dotenv
from app import app

load_dotenv()

SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
X_VESTABOARD_API_KEY = os.getenv("X-VESTABOARD-API-KEY")
X_VESTABOARD_API_SECRET = os.getenv("X-VESTABOARD-API-SECRET")

job_store = MemoryJobStore()
executors = {'default': ThreadPoolExecutor(20)}
scheduler = BackgroundScheduler(jobstores={'default': job_store}, executors=executors)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_excel(file_path):
    workbook = load_workbook(filename=file_path)
    sheet = workbook.active
    headers = [cell.value for cell in sheet[1]]
    data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        data.append(dict(zip(headers, row)))
    return data

CURRENTLY_DISPLAYED_TRIPS = []

def format_vestaboard_message(message, time):
    global CURRENTLY_DISPLAYED_TRIPS
    if len(CURRENTLY_DISPLAYED_TRIPS) > 0:
        now = datetime.datetime.now()
        upcoming_trips = [trip for trip in CURRENTLY_DISPLAYED_TRIPS if trip['time'] > now.time()]
        CURRENTLY_DISPLAYED_TRIPS = upcoming_trips
    
    CURRENTLY_DISPLAYED_TRIPS.append(
            {
                "msg": {
                "style": {
                "height": 2,
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
        print(f"Successfully formatted message!")
        return formatted_msg.json()
    else:
        print(f"Failed to format message: {formatted_msg.status_code}")
        return(False)
    
    
def post_to_vestaboard(message, time):
    characters = format_vestaboard_message(message, time)
    if characters:
        print(characters)
 
        response = requests.post(
            f"https://subscriptions.vestaboard.com/subscriptions/{SUBSCRIPTION_ID}/message",
            headers={"Content-Type": "application/json",
                    "x-vestaboard-api-key": X_VESTABOARD_API_KEY,
                    "x-vestaboard-api-secret": X_VESTABOARD_API_SECRET},
            json={"characters": characters}
        )
        if response.status_code == 200:
            print(f"Successfully updated Vestaboard with:\n{message}")
        else:
            print(f"Failed to update Vestaboard: {response.status_code}")

def schedule_trips(trips):
    last_departure = datetime.datetime.now().time()
    for trip in trips:
        departure_time = datetime.datetime.strptime(str(trip['Start time Z']), '%I:%M %p').time()
        now = datetime.datetime.now()
        departure = datetime.datetime.combine(now.date(), departure_time)
        
        delay = (departure - datetime.datetime.now()).total_seconds()
        
        if delay > 0:
            job = scheduler.add_job(
                post_to_vestaboard, 
                'date', 
                run_date=departure - datetime.timedelta(hours=1),
                args=[f"{trip['Customer']} {trip['Orig']} to {trip['Dest']}", departure_time],
                id=f"{trip['Customer']}_{trip['Orig']}_{trip['Dest']}"
            )
            if last_departure < departure_time:
                last_departure = departure_time
            
            print(f"Scheduled trip for {trip['Customer']} from {trip['Orig']} to {trip['Dest']} at {departure_time}")
        else:
            print(f"Trip for {trip['Customer']} at {departure_time} already passed today.")
            
    scheduler.add_job(
                post_to_vestaboard, 
                'date', 
                run_date=datetime.datetime.combine(now.date(), last_departure) + datetime.timedelta(minutes=15),
                args=["Welcome to Elite Jets", last_departure],
                id="End"
            )
    

scheduler.start()  # Start the scheduler
# Vestaboard Scheduler

This app is about scheduling of upcoming trip details to be displayed on a Vestaboard. The users upload an Excel spreadsheet exported from a CRM app, and the app schedules each trip to be displayed on the board one hour before the departure time. If there are multiple trips within an hour, multiple trips are dispalyed for a maximum of 3 trips at the same time - the Vestaboard has 6 rows, where each trip can take 2 rows.
The UI allows the user to see a list of scheduled tasks. The users have the option to update the departure time, or delete the scheduled trips altogether.


[App Screenshot Scheduled Jobs List](/screenshots/screenshot.png)


## Get Started

### Tech Stack

[Requirements](/requirements.txt)

  - Python 3.12
  - Pip
  - Virtualenv
  - Flask 3.1.0
  - Openpyxl 3.1.5
  - APScheduler 3.11.0

### Installation

  1. Clone the repository: `git clone`
  2. Create a virtual environment : `python3 -m venv venv`
  3. Activate the virtual environment: `source venv/bin/activate`
  4. Install dependencies: `pip3 install -r requirements.txt`
  5. Run app: `flask run`
    
### Main Features

- A web application that allows users to schedule trips to be displayed on a Vestaboard
- The app allows a user to upload an XLSX spreadhseet exported from a CRM.
- The app will schedule the trips to be displayed on the Vestaboard one hour before departure.
- The app allows to show 3 trips simultanously - scheduled within one hour.
- The app will remove trips after their departure time has passed.
- The app will show custom text after the last trip has left.

### Upload File Template

[Excel Template](/screenshots/Template.xlsx)

The app expects an XSLX file.
The file must include the following columns:
- Customer
- Start time Z
- Orig
- Dest

### Project Management

[Project Board][https://github.com/rumenji/Vestaboard-Scheduler/projects?query=is%3Aopen] <br />
[List of Issues][https://github.com/rumenji/Vestaboard-Scheduler/issues]

### Author

Rumen Ivanov
[LinkedIn](https://www.linkedin.com/in/rumen-ivanov-it/)

### Vestaboard

Vestaboard 
[Official website](https://www.vestaboard.com/)
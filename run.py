from app import app
from multiprocessing import cpu_count
# Run flask settings if not using gunicorn
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', processes=cpu_count())

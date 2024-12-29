from app import app
from multiprocessing import cpu_count

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0')
    app.run(debug=False, host='0.0.0.0', processes=cpu_count())




# gunicorn -w $(nproc) --threads 2 --max-requests 10 myproject:app
from app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# from multiprocessing import cpu_count
# app.run(debug=False, processes=cpu_count())

# gunicorn -w $(nproc) --threads 2 --max-requests 10 myproject:app
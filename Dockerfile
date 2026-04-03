FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python backend/wait_for_db.py && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
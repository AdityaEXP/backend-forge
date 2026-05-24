FROM python:3.12-slim

WORKDIR /

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "auth_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.12-alpine

WORKDIR /app 
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN mkdir log

COPY src /app/scripts
ENTRYPOINT [ "python", "/app/scripts/main.py" ]
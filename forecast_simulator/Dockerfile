FROM python:3.11-bullseye
RUN mkdir -p /opt/app
WORKDIR /opt/app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python", "producer.py"]
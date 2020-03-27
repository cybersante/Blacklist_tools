FROM python:3.7.3-slim

RUN pip3 install gunicorn flask ipaddress python-geoip-python3
COPY . /app
WORKDIR /app

ENTRYPOINT ["bash", "/gunicorn_starter.sh"]

FROM python:3.7-slim-stretch

RUN mkdir -p /opt/app
WORKDIR /opt/app

ADD requirements.txt /opt/app
ADD main.py /opt/app
ADD .env /opt/app

RUN pip install -r requirements.txt

EXPOSE 2015

CMD [ "gunicorn", "-b", "0.0.0.0:2015", "main:app" ]
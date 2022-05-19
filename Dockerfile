FROM python:3.10
ADD . /app
# TODO: this should be more specific and add just the needed files
# TODO: it also needs to setup the static and media directories
WORKDIR /app


RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install psycopg2-binary

EXPOSE 8011
CMD ["gunicorn", "--bind", "0.0.0.0:8011", "djangoTest.wsgi", "--workers=4"]
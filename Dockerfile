FROM tiangolo/uwsgi-nginx-flask:flask

COPY requirements.txt main.py __init__.py uwsgi.ini /app/
COPY conf /etc/nginx/conf.d/


COPY documents /app/documents/
COPY front-end/index.html front-end/styles.css /var/www/app/
COPY front-end/dist /var/www/app/dist
COPY front-end/fonts /var/www/app/fonts
COPY front-end/imgs /var/www/app/imgs
COPY front-end/js /var/www/app/js
COPY front-end/css /var/www/app/css

RUN pip install --upgrade -r requirements.txt

EXPOSE 8080
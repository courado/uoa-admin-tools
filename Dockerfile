FROM tiangolo/uwsgi-nginx-flask:python2.7

COPY requirements.txt main.py __init__.py uwsgi.ini /app/
RUN pip install --upgrade -r requirements.txt
COPY conf /etc/nginx/conf.d/

COPY documents /app/documents/
COPY front-end/index.html front-end/styles.css /app/static/
COPY front-end/dist /app/static/dist
COPY front-end/fonts /app/static/fonts
COPY front-end/imgs /app/static/imgs
COPY front-end/js /app/static/js
COPY front-end/css /app/static/css

ENTRYPOINT ["/start.sh"]

EXPOSE 80

FROM python:3.6.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV prometheus_multiproc_dir /tmp

CMD gunicorn -c config.py -w 4 -b 0.0.0.0:8080 server:app

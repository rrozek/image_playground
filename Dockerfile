FROM python:3.8-slim

COPY ./ /app
WORKDIR /app

RUN apt-get -y update
RUN apt-get install -y gcc libpq-dev netcat
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 80

CMD ["gunicorn", "-w", "3", "--bind", "0.0.0.0:80", "--access-logfile", "-", "backend.wsgi:application"]

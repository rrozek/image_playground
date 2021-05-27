# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
# install imagemagick
RUN apk update \
    && apk add gimp postgresql-dev gcc python3-dev musl-dev bash inotify-tools imagemagick ghostscript

#install gimp
RUN mkdir -p /gimp && chmod 777 /gimp && mv /etc/gimp/2.0/gimprc /etc/gimp/2.0/gimprc.dist

# install api dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
COPY gimp_rootfs /
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

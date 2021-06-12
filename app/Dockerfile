# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
  RUN apk update \
    && apk add wget alpine-sdk zlib zlib-dev imagemagick-dev potrace libxml2 xmlto libpng-dev libjpeg-turbo-dev freetype-dev fontconfig-dev	perl-dev ghostscript-dev libwebp-dev libtool tiff-dev lcms2-dev gimp pkgconfig postgresql-dev gcc python3-dev musl-dev bash inotify-tools ghostscript

# install imagemagick
RUN wget https://download.imagemagick.org/ImageMagick/download/ImageMagick.tar.gz && \
    tar -xzf ImageMagick.tar.gz && \
    cd ImageMagick-7.0.11-14 && \
    ./configure --prefix /usr/local && \
    make -j3 && \
    make install && \
    cd .. && \
    rm -rf  ImageMagick*

#install gimp
RUN mkdir -p /gimp && chmod 777 /gimp && mv /etc/gimp/2.0/gimprc /etc/gimp/2.0/gimprc.dist

# install api dependencies
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app
COPY gimp_rootfs /
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
EXPOSE 8000
# copy project
COPY . /usr/src/app

# run entrypoint.sh
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

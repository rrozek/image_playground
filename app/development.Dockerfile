# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

  RUN apk update \
    && apk add wget bash zlib pkgconfig gcc python3-dev musl-dev gimp \
    alpine-sdk potrace libxml2-dev libpng-dev libjpeg-turbo-dev freetype-dev fontconfig-dev	ghostscript-dev libtool tiff-dev ghostscript \
    libwebp-dev perl-dev lcms2-dev inotify-tools

# install imagemagick
RUN wget https://download.imagemagick.org/ImageMagick/download/ImageMagick-6.9.12-14.tar.gz && \
    tar -xzf ImageMagick-6.9.12-14.tar.gz && \
    cd ImageMagick-6.9.12-14 && \
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

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
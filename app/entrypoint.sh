#!/bin/bash

set -e

cd /usr/src/app
mkdir /gimp/scripts
cp snippets/svg-clip-path.scm /gimp/scripts/

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"


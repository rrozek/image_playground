#!/bin/sh

set -e

USER=${DB_USER:-admin}
PASS=${DB_PASSWORD:-MySuperAwesomePassword}
DB=${DB_NAME:-wbtcv_api}

echo "Creating user"
psql -q -c "DROP ROLE IF EXISTS \"$USER\";"
psql -q <<-EOF
    CREATE ROLE "$USER" WITH ENCRYPTED PASSWORD '$PASS';
    ALTER ROLE "$USER" WITH ENCRYPTED PASSWORD '$PASS';
    ALTER ROLE "$USER" WITH SUPERUSER;
    ALTER ROLE "$USER" WITH LOGIN;
EOF

echo "Creating database"
psql -q <<-EOF
    CREATE DATABASE "$DB" WITH OWNER="$USER" ENCODING='UTF8';
    GRANT ALL ON DATABASE "$DB" TO "$USER"
EOF
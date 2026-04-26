#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Auto-seed default users and diseases on every deploy.
# Uses get_or_create so it NEVER duplicates — safe to run repeatedly.
python manage.py seed_data

# Auto-seed all PlantVillage AI detection classes
python seed_plantvillage.py

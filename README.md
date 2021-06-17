# Server for "IntelliJ IDEA team statistics plugin"
## Description
This repository contains Django application for "IntelliJ IDEA team statistics plugin" project. 

The goal is to create plugin and web-service which allow tracking of different metrics (with possibility to create some custom).

Plugin source code can be found in [plugin repository](https://github.com/DT6A/TeamStatisticsPlugin).

## Requirements
1. Python3
2. All other requierments can be found in `requirements.txt`

## Setting up
1. Install [MySQL](https://dev.mysql.com/downloads/installer/)
2. Install requirements with `pip install -r requirements.txt` 
3. Change `DATABASES` setting in `django_server/django_server/settings.py` to be compatible with your MySQL setup
4. Go to `django_server` directory
5. Run `python manage.py makemigrations` and `python manage.py migrate`
6. (Optional) Create superuser with `python manage.py createsuperuser`
8. Start server with `python manage.py runserver`

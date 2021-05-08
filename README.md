# Setting up
1. Install [MySQL](https://dev.mysql.com/downloads/installer/)
2. Install requirements with `pip install -r requirements.txt` 
3. Change `DATABASES` setting in `django_server/django_server/settings.py` to be compatible with your MySQL setup
4. Go to `django_server` directory
5. (Optional) Create superuser with `python manage.py createsuperuser`
6. Run `python manage.py makemigrations` and `python manage.py migrate`
7. Start server with `python manage.py runserver`
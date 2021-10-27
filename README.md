# DragonLinguistics
My personal website

## Development
### Environment
Before doing anything, make sure you've copied `.env.example` to `.env` and configured the fields.

* `SECRET_KEY` should be a randomly generated and complex key. See https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key for more information.
* `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST` and `DATABASE_PORT` should be the credentials pointing to a MySQL/MariaDB server instance. This is the database that Dragon Linguistics uses.
* `DEBUG` should be set to `TRUE` if you are running it for development, and to `FALSE` (or anything else in theory) for running otherwise. When debugging, errors are printed in the browser which is a security concern for any set up other than development so be careful when moving to production!
* `ALLOWED_HOSTS` is a comma-separated list of hosts that Django will listen to. In development, this is usually fine to stick as `localhost` but when the time comes it may need to change to e.g `my-django-website.example.com,www.my-django-website.example.com`
* `STATIC_URL` and `MEDIA_URL` are the paths to be used in the URL for static content and for user-uploaded content. If these begin with a `/`, this will be a relative path (e.g `my-django-website.example.com/media/`) but otherwise they can be a full URL in themselves (e.g `https://assets.example.com/`). Both of these should end in a trailing slash.
* `MEDIA_ROOT` is the file system location of the directory where user-uploaded content should be put. In development this can just be set as e.g a `media` folder within the development environment (e.g `/home/user/repos/dragonlinguistics/media`), but in production you may want to customise this to a more secure location.

### Django
To set up the Django environment for the first time, you need to set up the Python virtual environment in your dev folder:
```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

After this point you can access all Django tools through this environment. Migrate and start the server with the following commands:
```
venv/bin/python manage.py migrate
venv/bin/python manage.py runserver
```

When you set up your environment, it's worth creating a superuser so you can access the admin interface.
```
venv/bin/python manage.py createsuperuser
```

If you've added/changed some models and need to generate migrations, run the following:
```
venv/bin/python manage.py makemigrations
```

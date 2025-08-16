"""This file is used by Passenger to serve the Django app."""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append(os.getcwd())
os.environ["DJANGO_SETTINGS_MODULE"] = "root.settings"


application = get_wsgi_application()

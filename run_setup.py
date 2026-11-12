import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comfortzone.settings")

import django
django.setup()

from django.core.management import call_command

call_command("migrate", interactive=False)
call_command("collectstatic", interactive=False)
print("Setup done")
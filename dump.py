import json
from django.core.management import call_command
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'squadra.settings')

import django
django.setup()

with open('fixtures/datadump.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', indent=2, stdout=f)

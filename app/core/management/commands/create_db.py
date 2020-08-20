import sys
import logging
import MySQLdb
import traceback

from django.core.management.base import BaseCommand
from django.conf import settings


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = 'Creates the initial database'

    def handle(self, *args, **options):
        dbname = settings.DATABASES['default']['NAME']
        user_name = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        rds_host = settings.DATABASES['default']['HOST']
        port = int(settings.DATABASES['default']['PORT'])

        print('Starting db creation')
        try:
            db = MySQLdb.connect(
                host=rds_host,
                user=user_name,
                password=password,
                db="mysql",
                connect_timeout=5,
                port=port
                )
            c = db.cursor()
            print("connected to db server")
            c.execute(f"CREATE DATABASE {dbname};")
            c.execute(
                f"""GRANT ALL PRIVILEGES ON db_name.*
                TO '{user_name}' IDENTIFIED BY '{password}';""")
            c.close()
            print("closed db connection")
        except Exception:
            track = traceback.format_exc()
            print(track)
            logger.error(
                "ERROR: Could not connect to MySql instance.")
            sys.exit()

import time

# import the conntctions module which is
# what we can use ti test if the database connection is available
from django.db import connections

# import the operational errorr that Django
# will throw if the database isn't available
from django.db.utils import OperationalError

# import base command the class that we need to build on
# in order to create our custom command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        # passing *args, **options to management commends
        # output a message to the screen
        self.stdout.write("Waiting for database...")
        db_conn = None

        # while db_conn is false value it could be a blank string or None
        while not db_conn:
            try:
                # try set db.conn to the database connection
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)

        # final message that says the database is available
        self.stdout.write(self.style.SUCCESS("Database available!!"))

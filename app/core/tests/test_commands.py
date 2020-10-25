# Allow us to mock the behavior of the Django get database function
# can simulate the database being available and not being
# available for wen we test our command
from unittest.mock import patch

# allow us to call the command in our source code
from django.core.management import call_command

# import the operational error that Django throws when the
# database is unavailable
# to simulate the database being avaliable or not when we run our command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    """Test waiting for db when db is available"""

    def test_wait_for_db_ready(self):
        # create management command the way that
        # we tested the database is available
        # in Django just try and retrieve the default
        # database via the ConnectionHandler
        # __getitem__ function call when retrieve the database is getitem
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            # whenever this is called during our test execution instead of
            # actually before performing whatever
            # behavior __getitem__ in Django
            # it will override it and just replace it with
            # a mock object which does two things
            # 1) return gi.return_value = True value that we specify
            # 2) allow us monitor how many times it was called
            # and the differrnt calls that were made to it
            gi.return_value = True
            # wait_for_db the name of the management command that we create
            call_command("wait_for_db")
            # create assertions of our test
            # __getitem__ set to call once
            self.assertEqual(gi.call_count, 1)

    # it is replaces the behavior of time.sleep and just replace it
    # with a mock function thet return True
    # mean test it won't actually wait the second or however long
    # you have it to wait in your code
    @patch("time.sleep", return_value=True)
    # do same thig with patch
    # ('django.db.utils.ConnectionHandler.__getitem__') as gi:
    # then pass gi as an argument to test_wait_for_db
    def test_wait_for_db(self, ts):
        # argument ts even not using it still need to pass it
        # if don't do that then when run test it will error
        # because it'll have an unexpected argument
        """Test waiting for db"""
        with patch("django.db.utils.ConnectionHandler.__getitem__") as gi:
            # that the five times call this __getitem__
            # it's going to raise the OperationalError
            # on the sixth time it won't raise the error it will just return
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command("wait_for_db")
            self.assertEqual(gi.call_count, 6)

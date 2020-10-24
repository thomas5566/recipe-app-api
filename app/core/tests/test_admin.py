from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    # setUp function is ran before every test that we run
    # so sometimes there are setup tasks need to be done
    # before every test in our test case class
    def setUp(self):
        # basically sets to self so that's accessible
        # in the other test a Client variable
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@gmail.com", password="password123"
        )
        # uses Client help function that allows you to log
        # a user in with the Django authentication
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="password123",
            name="Test use full name"
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        # admin:core_user_changelist URLs are actually defined in Django admin
        # what this will do is it will generate the URL for our list user page
        # use reverse function instead of just typing the URL manually
        url = reverse("admin:core_user_changelist")
        # res = response
        # This will use test client to perform a HTTP GET on the URL
        res = self.client.get(url)
        # assertContains is a Django custom assertion
        # that will check that response contains a sertain item
        # and check HTTP request was HTTP 200 and
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works"""
        # reverse function will create a URL like
        # /admin/core/user/1 args=[self.user.id] is assigned to the
        # arguments of the URL at the end
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        # Test status code for the response that our client
        # gives is HTTP 200 check status code okay the page worked
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

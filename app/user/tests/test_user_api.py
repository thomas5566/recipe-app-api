from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# test client that we can use to make requests to
# our API and then check what the response is
from rest_framework.test import APIClient

# a module that contains some status codes
# that we can see in basically human readable form
from rest_framework import status

# all caps is we don't expect this value to change during our tests at all
CREATE_USER_URL = reverse("user:create")
# This URL is use to make the HTTP POST request to generate our token
TOKEN_URL = reverse('user:token')
# update user endpoint 'me' URL
ME_URL = reverse('user:me')


# **param dynamic list of arguments
# we can pass them directly into the create user model
# have a lot of flexibility about the fields can assign to the user
# that we create for our samples
def create_user(**params):
    # a function when we're creating users
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        # call client in test can reuse for all of the tests
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with vaild payload is successful"""
        # payload is the object that you pass to the API when
        # you make the request so just test that
        # if pass in all the correct fields
        # then the user is created successfully
        payload = {
            "email": "test@gmail.com",
            "password": "testpass",
            "name": "Test name",
        }
        # make request
        # do a HTTP POST request to client to URL for creating users
        res = self.client.post(CREATE_USER_URL, payload)

        # make sure that the API return 201 create
        # when we create a new object
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # test that object is actually created
        # unwind the response for 'res' because when do
        # a HTTP POST and create a user we expect to see
        # the created user object returned in the API
        # along with status.HTTP_201_CREATED
        # **res.data it will take the dictionary response
        # pass **res.data as the parameters for the 'get'
        # then if this gets the user successfully then
        # know that user is actually being create properly
        user = get_user_model().objects.get(**res.data)
        # test passwordis correct by doing user.check_password
        self.assertTrue(user.check_password(payload["password"]))
        # check the password is not return .get(**res.data) of this object
        # we don't want the password being returned in the request
        # because it is a potential security vulnerability
        # ensure password are kept as secret as possible
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
                    "email": "test@gmail.com",
                    "password": "testpass",
                    'name': 'Test',
                }
        # ** will pass in basically 'email' equals 'test@gmail.com'
        # 'password': 'testpass'
        # ** make it a little less wordy so there's a few less characters
        # there just make it a cleaner
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        # make HTTP_400_BAD_REQUEST because the user is already exists
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more then 5 characters"""
        payload = {
                    "email": "test@gmail.com",
                    "password": "pw",
                    'name': 'Test',
                }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # check user was never created
        # if the user exists it will return true otherwise will return False
        user_exists = get_user_model().objects.filter(
            email=payload["email"]).exists()
        # we hope user_exists would be false
        # because we don't want the user to exist
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        # checks that there is a key called token
        # in the response.data that we get back
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='test@gmail.com', password='testpass')
        payload = {
            'email': 'test@gmail.com',
            'password': 'wrong'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not creates if user doesn't exist"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpass'
        }
        # make our request without creating the user
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        # a HTTP get to the ME_URL
        res = self.client.get(ME_URL)

        # make sure that if you call the URL without any authentication
        # it returns HTTP_401_UNAUTHORIZED
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='testpass',
            name='test'
        )
        # create a reusable client
        self.client = APIClient()
        # help function for simulate or making authenticated request
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # test that the user object returned is what we expect
        # no need to sending password because it's hash and
        # no need for that password to bo on the client-side
        # if provide that password it will make it accessible
        # then it just opens up for different vulnerabilities
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""
        # test that cannot do a HTTP POST request on the profile
        res = self.client.post(ME_URL, {})

        # standard response when you try and do a HTTP
        # method that is not allowed on the API
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        # user profile update test
        payload = {'name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)
        # refresh_from_db help function
        # to update the user with
        # the latest values from the database
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

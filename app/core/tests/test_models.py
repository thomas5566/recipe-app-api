from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@gmail.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = "test@gmail.com"
        password = "Test123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(
            # check_password return True or False
            user.check_password(password)
        )

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@GMAIL.COM"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            # anything that we run in here should raise ValueError
            # if it doesn't raise a value error then this test will fail
            get_user_model().objects.create_user(None, "test123")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            "test@gmail.com",
            "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        # it is creates a tag and then just assert that
        # when convert our tag model to a string it name='Vegan'
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string respresentation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Testthe recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

    # UUID module function generate a unique UUID version 4
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct locations"""
        uuid = 'test-uuid'
        # means anytime we call this UUID4 function that is
        # triggered from with in our test it will change the
        # value override the default behavior and just return
        # 'test-uuid' this instead this allows us to reliably
        # test how our function works
        mock_uuid.return_value = uuid
        # it will remove myimage part and replace it with the UUID
        # and keep the 'jpg' extension
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        # F string can define any variables that you want and
        # surround them in these {} and it will render the string
        exp_path = f'upload/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)

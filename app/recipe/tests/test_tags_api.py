from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        # query on the model that we expect to get
        # to compare to the result
        # order base on the name
        tags = Tag.objects.all().order_by('-name')
        # there's going to be more then one item in serializer
        # if without many=True that it will assume that you are
        # trying to serializer a single object
        # but we want serializer list of object
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # res.data is the data that was returned in the response
        # and then we expect that to equal the serializer.data
        # that we passed in so result should be same
        # and revers order list of all tags orders by name
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        # create a new user in addition to the user
        # that is created at the setUp function
        # so we can assign a tag to that user
        # and then we can compare that tag was not
        # included in the response because it was
        # not the authenticated user
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        # create a new tag that is assigned to the
        # authenticated user
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)
        # expect the one tag to be reutrn in the list
        # because that's the only tag assigned to the
        # authenticated user
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check the length of the results return
        # because if there's two return then that's is a problem
        # if there's one return then that's what we expect
        # because we only created one tag assigned to the
        # authenticated user
        # len(res.data) the length of the array that was return
        # in the request
        self.assertEqual(len(res.data), 1)
        # test the name of the tag returned in the one response
        # is the tag that we create and assign to the user
        # res.data[0] take the first element of the data response
        # and get the name and compare that to tag.name
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        # this test will false if this doesn't exists
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.tags.add(tag1)
        # pass dictionary with the get parameters we want to apply it
        # to our get request and call filter assigned_only and pass 1
        # then this will be evaluated to true and it will filter by
        # the tags are assigned_only
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=3.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=2.00,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)

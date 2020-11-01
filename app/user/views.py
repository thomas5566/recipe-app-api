# from django.shortcuts import render

# Create API view that comes with the Django rest framework
# this is a view that's pre-made for us that allows us to
# easily make a API that contain an object in a database
# using the serializer that were going to provide
from rest_framework import generics, authentication, permissions
# if authenticated using a username and password
# as standard is easy pass in the ObtainAuthToken view
# directly into our URLs
# Beacuse we are customizing it slightly we need to
# import it into our views and then extend is with a class
# and make a few modifications to tje class variables
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer

    # set render class so we can view this endpoint in
    # the browser with the browsable api
    # if don't do this then have use some other tool
    # make the HTTP POST request
    # DEFAULT_RENDERER_CLASSES if we ever change the
    # render class and we want to use a diffrent class to render
    # browseable API the we can do that in the setting and it will
    # update in our view automatically so we don't have to go
    # through the view and change it
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    # authentication is the mechanism by which the authentication
    # happens so this could be cokie authentication
    # or token authentication
    authentication_classes = (authentication.TokenAuthentication,)
    # permissions are the level of access that the user has
    # only permission to add is that the user must be
    # authenticated to use the API they don't have any
    # special permissions just have to be logged in
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authentication user"""
        # add a GET object function to our API view
        # when get_object is called the request will have the
        # user attached to it because of the authentication_classes
        # because we have the authentication_classes that takes care
        # of take getting the authentication user and assigning it
        # to request
        return self.request.user

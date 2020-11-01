from django.contrib.auth import get_user_model, authenticate
# whenever you're outputting any messages in python code
# that are going to be output to the screen
# this is pass them through this translation system
# just so if you ever do add any extra languages
# to projects can easily add the language file
# and automatically convert all of the text to
# the correct language
from django.utils.translation import ugettext_lazy as _
# from django.contrib.auth import models

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name")

        # extra key word arg
        # allow us to configure a few extra setting in model serializer
        # use this to ensure that the password is write only
        # and the minimum required length is 5 characters
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        # override the create function
        # when ready to create the user it will call create function
        # and it will pass in the validated_data
        # the validated_data will contain all of the data that was
        # passed in to serializers would be the JSON data
        # that was made in the HTTP POST
        return get_user_model().objects.create_user(**validated_data)

# this function is called when we validate our serializer
# validation is checking the input are all correct
# is a CharField or a character field and password is CharField
# And as part of the validation function we are also going to validate
# that the authentication credentials are correct


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        # it's passible to have witespace in password
        # so may have an extra space before or after
        # Django rest framwork serializer it will trim
        # off this white space
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        # attrs basically just every field that makes up
        # our serializer so any field that makes up a serializer
        # it will get passed into the validate function as dictionary
        # and then retrieve the fields via this attributes
        # and we can validate whether we want to pass this
        # validation or want to fail the validation
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            # basically access the context of the request
            # that was made so it's going to pass AuthTokenSerializer
            # into our view set and what the Django rest framework viewset
            # does when a request is made it passes the context into the
            # serializer in this context class variable and from that
            # we can get ahold of the request that was made
            request=self.context.get('request'),
            username=email,
            password=password
        )
        # when the authentication fail
        if not user:
            msg = _('Unable to authenticate with provided credentials')
            # raise the validation error and then the Django rest framework
            # knows how to handle this error and it by passing error 400
            # response and sending a response to user
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        # whenever overriding the validate function must return the value
        # at the end once the validation is successful
        return attrs

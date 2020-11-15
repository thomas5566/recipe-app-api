from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from . import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owend reipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenicated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer

    # Add a function which will override the get queryset function
    # def get_queryset(self):
    #     """Return objects for the current authenticated user only"""
    #     # when the list function is invoked
    #     # when TagViewSet is invoked from a URL
    #     # it will call get_queryset to retrieve
    #     # queryset = Tag.objects.all() object
    #     # this is we can apply any custom filtering
    #     # like limiting it to the authenticated user
    #     # so get_queryset will return will displayed in the API
    #     # you could reference Tag.objects.all() directly
    #     # but if change the queryset = Tag.objects.all() object
    #     # the retrieving then it wouldn't work
    #     # so you want to be change it in one place and this
    #     # should be the objects that are being rendered by viewset
    #     return self.queryset.filter(user=self.request.user).order_by('-name')

    # def perform_create(self, serializer):
    #     """Create a new tag"""
    #     # perform_create function allows to hook into the
    #     # create process when creating an object
    #     # when doing perform_create object in viewset
    #     # this function will be in invoked and the serializer
    #     # validated serializer will be passed in as a serializer argumrnt
    #     serializer.save(user=self.request.user)


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    # def get_queryset(self):
    #     """Return objects for the current authenticated user"""
    #     return self.queryset.filter(user=self.request.user).order_by('-name')

    # def perform_create(self, serializer):
    #     """Create a new ingredient"""
    #     serializer.save(user=self.request.user)


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    # ModelViewSet allow update create view details
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

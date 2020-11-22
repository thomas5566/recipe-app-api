from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
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
        # use bool because assigned_only value only 0 or 1
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

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

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        # we do this is because we don't want to be reassigning
        # our query set with the filtered option we want to
        # actually reference queryset apply the filter and then
        # return that instead of our main query
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # __ Django syntax for filtering on foreign key objects
            # tags field in our queryset in a recipe query set
            # and that has a foreign key to the tags table wihich
            # has an ID, __in return all of the tags where the ID
            # is in this list that we provide
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    # Custom actions
    # allow user to POST an image to recipe
    # detail is a specific recipe so only be able to upload images
    # for recipe that already exist and will use detail URL that
    # has the ID of the recipe in the URL so it knows which one
    # to upload the image to
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

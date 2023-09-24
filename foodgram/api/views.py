from rest_framework import viewsets, status
from rest_framework.response import Response

from recipes.models import Recipe, Tag, Shop, Follow, Ingredient, Favorite
from api.serializers import (RecipeCrUpSerializer,  RecipeReadSerializer,
                             TagSerializer, ShopSerializer,
                             FollowSerializer, IngredientSerializer,
                             FavoriteSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        elif self.action in ['create', 'partial_update', 'delete']:
            return RecipeCrUpSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def create(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        user = request.user
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        id_recipe = self.kwargs['id']
        recipe = Recipe.objects.get(id=id_recipe)
        Favorite.objects.get(recipe=recipe).delete()

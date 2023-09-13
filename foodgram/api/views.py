from rest_framework import viewsets

from recipes.models import Recipe, Tag, Shop, Follow, Ingredient, Favorite
from .serializers import (RecipeCrUpSerializer, RecipeReadSerializer,
                          TagSerializer, ShopSerializer,
                          FollowSerializer, IngredientSerializer,
                          FavoriteSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve':
            return RecipeReadSerializer
        if self.action == 'create' or 'update':
            return RecipeCrUpSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from recipes.models import (Recipe, Tag, Shop, Follow, Ingredient, Favorite,
                            CustomUser)
from api.serializers import (RecipeCrUpSerializer,  RecipeReadSerializer,
                             TagSerializer, FollowSerializer,
                             IngredientSerializer, FavoriteShopSerializer)
from api.permissions import OnlyAuthorized


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


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        follows_user = Follow.objects.filter(
            user=user_id).values_list('author_id', flat=True)
        users = CustomUser.objects.filter(id__in=follows_user)
        return users

    def create(self, request, *args, **kwargs):
        user = request.user
        author_id = kwargs.get('id')
        author = CustomUser.objects.get(id=author_id)
        Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        id_author = kwargs.get('id')
        Follow.objects.get(author=id_author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteShopSerializer
    permission_classes = (OnlyAuthorized,)

    def create(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        user = request.user
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = FavoriteShopSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        Favorite.objects.get(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = FavoriteShopSerializer

    def create(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        user = request.user
        Shop.objects.create(user=user, item=recipe)
        serializer = FavoriteShopSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        Shop.objects.get(item=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

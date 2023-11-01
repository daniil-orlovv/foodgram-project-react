from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FollowPagination
from api.permissions import AuthUserDelete
from api.serializers import (CustomUserSerializer, FavoriteCartSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeCrUpSerializer, RecipeReadSerializer,
                             TagSerializer)
from recipes.models import (Cart, CustomUser, Favorite, Follow, Ingredient,
                            Recipe, RecipeIngredient, Tag)

SIZE_FONTS = 12
X_POINT = 50
Y_POINT = 750
DECREASE_Y_POINT = 20


class CustomDjoserUserViewSet(DjoserUserViewSet):
    queryset = CustomUser.objects.all()

    @action(detail=False)
    def subscriptions(self, request, *args, **kwargs):
        paginator = FollowPagination()
        user = self.request.user
        limit = self.request.query_params.get('recipes_limit', None)
        queryset = CustomUser.objects.filter(author_followers__user=user)
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FollowSerializer(
            result_page,
            many=True,
            context={
                'limit': limit,
            })
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=[AuthUserDelete])
    def follow(self, request, *args, **kwargs):
        user = request.user
        author_id = kwargs.get('id')
        author = get_object_or_404(CustomUser, id=author_id)
        Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            author,
            context={
                'request': request,
                'author': author,
                'author_id': author_id
            })
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @follow.mapping.delete
    def unfollow(self, request, *args, **kwargs):
        user = request.user
        author_id = kwargs.get('id')
        author = get_object_or_404(CustomUser, id=author_id)
        objects = user.user_followings.filter(author=author)
        if not objects.exists():
            return Response({
                'error': 'Вы не подписаны на этого автора!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeCrUpSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        permission_classes=[AuthUserDelete]
    )
    def add_to_shop_cart(self, request, *args, **kwargs):
        id_recipe = kwargs.get('pk')
        recipe = Recipe.objects.get(id=id_recipe)
        user = request.user
        if user.user_cart.filter(item=recipe).exists():
            return Response({
                'error': 'Рецепт уже добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Cart.objects.create(user=user, item=recipe)
        serializer = FavoriteCartSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @add_to_shop_cart.mapping.delete
    def del_from_shop_cart(self, request, *args, **kwargs):
        id_recipe = kwargs.get('pk')
        user = request.user
        recipe = Recipe.objects.get(id=id_recipe)
        objects = user.user_cart.filter(item=recipe)
        if not objects.exists():
            return Response({
                'error': 'Рецепт не добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=True, url_path='download_shopping_cart')
    def download(self, request, *args, **kwargs):
        all_ingredients = []
        ingredients = RecipeIngredient.objects.filter(
            recipe__author=request.user.username
        ).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                amount=Sum('amount'))
        for ingredient in ingredients:
            ingredient_info = {
                'name': ingredient['ingredient__name'],
                'unit': ingredient['ingredient__measurement_unit'],
                'amount': int(ingredient['amount'])
            }
            all_ingredients.append(ingredient_info)

        font = '/app/api/fonts/Arial.ttf'
        pdfmetrics.registerFont(TTFont('Arial', font))
        file_pdf = Canvas('shop_list.pdf')
        file_pdf.setFont('Arial', SIZE_FONTS)
        y_coordinate = Y_POINT
        for ingredient in all_ingredients:
            ingredient_text = (f'{ingredient["name"]}'
                               f'({ingredient["unit"]}) — '
                               f'{ingredient["amount"]}')
            file_pdf.drawString(X_POINT, y_coordinate, ingredient_text)
            y_coordinate -= DECREASE_Y_POINT
        file_pdf.showPage()
        file_pdf.save()
        pdf_file_path = 'shop_list.pdf'
        response = FileResponse(
            open(pdf_file_path, 'rb'), content_type='application/pdf')
        response[
            'Content-Disposition'] = 'attachment; filename="shop_list.pdf"'
        return response

    @action(detail=True, methods=['post'])
    def favorite(self, request, *args, **kwargs):
        id_recipe = kwargs.get('pk')
        recipe = Recipe.objects.get(id=id_recipe)
        user = request.user
        if user.user_favorites.filter(recipe=recipe).exists():
            return Response({
                'error': 'Рецепт уже добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = FavoriteCartSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, *args, **kwargs):
        id_recipe = kwargs.get('pk')
        user = request.user
        recipe = Recipe.objects.get(id=id_recipe)
        objects = user.user_favorites.filter(recipe=recipe)
        if not objects.exists():
            return Response({
                'error': 'Рецепт не добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        objects.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import FollowPagination
from api.permissions import CreateIfAuth, UpdateIfAuthor
from api.serializers import (CustomUserSerializer, FavoriteShopSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeCrUpSerializer, RecipeReadSerializer,
                             TagSerializer)
from recipes.models import (CustomUser, Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, Shop, Tag)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = None

    @action(detail=True)
    def me(self, request, *args, **kwargs):
        user_id = request.user.id
        user = get_object_or_404(CustomUser, id=user_id)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [CreateIfAuth, UpdateIfAuthor]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return Recipe.objects.all().order_by('-created')

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
    permission_classes = [permissions.AllowAny, ]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    pagination_class = FollowPagination

    @action(detail=False)
    def subscriptions(self, request, *args, **kwargs):
        paginator = FollowPagination()
        user = self.request.user
        queryset = CustomUser.objects.filter(following__user=user)
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = FollowSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        author_id = kwargs.get('id')
        author = get_object_or_404(CustomUser, id=author_id)
        if user == author:
            return Response({
                'error': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=user.id, author=author_id).exists():
            return Response({
                'error': 'Вы уже подписаны на этого автора!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        author_id = kwargs.get('id')
        if not Follow.objects.filter(author=author_id).exists():
            return Response({
                'error': 'Вы не подписаны на этого автора!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.get(author=author_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteShopSerializer

    def create(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        user = request.user
        if Favorite.objects.filter(user=user.id, recipe=recipe).exists():
            return Response({
                'error': 'Рецепт уже добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=user, recipe=recipe)
        serializer = FavoriteShopSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        if not Favorite.objects.filter(recipe=recipe).exists():
            return Response({
                'error': 'Рецепт не добавлен в избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.get(recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShopViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteShopSerializer

    def get_queryset(self):
        user = self.request.user.id
        queryset = Recipe.objects.filter(shop_item__user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        user = request.user
        if Shop.objects.filter(user=user.id, item=recipe).exists():
            return Response({
                'error': 'Рецепт уже добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Shop.objects.create(user=user, item=recipe)
        serializer = FavoriteShopSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete(self, request, *args, **kwargs):
        id_recipe = kwargs.get('id')
        recipe = Recipe.objects.get(id=id_recipe)
        if not Shop.objects.filter(item=recipe).exists():
            return Response({
                'error': 'Рецепт не добавлен в список покупок!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Shop.objects.get(item=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True)
    def download(self, request, *args, **kwargs):
        all_ingredients = []
        ingredients = RecipeIngredient.objects.filter(
            recipe__author__username=request.user.username
        ).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                amount=Sum('amount'))
        for i in ingredients:
            ingredient_info = {
                "name": i['ingredient__name'],
                "unit": i['ingredient__measurement_unit'],
                "amount": int(i['amount'])
            }
            all_ingredients.append(ingredient_info)

        font = "/app/api/fonts/Arial.ttf"
        pdfmetrics.registerFont(TTFont('Arial', font))
        file_pdf = Canvas("shop_list.pdf")
        file_pdf.setFont("Arial", 12)
        y = 750
        for i in all_ingredients:
            ingredient_text = f"{i['name']} ({i['unit']}) — {i['amount']}"
            file_pdf.drawString(50, y, ingredient_text)
            y -= 20
        file_pdf.showPage()
        file_pdf.save()
        pdf_file_path = "shop_list.pdf"
        response = FileResponse(
            open(pdf_file_path, 'rb'), content_type='application/pdf')
        response[
            'Content-Disposition'] = 'attachment; filename="shop_list.pdf"'
        return response

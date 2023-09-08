from rest_framework import serializers
from recipes.models import Recipe, Tag, Shop, Ingredient, Follow, Favorite


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'text', 'tags', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', 'color_code', 'slug')


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('user', 'item')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('title')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'favorite')


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('useer', 'author')

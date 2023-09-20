from rest_framework import serializers
from recipes.models import (Recipe, Tag, Shop, Ingredient, Follow, Favorite,
                            RecipeIngredient, CustomUser)
from djoser.serializers import UserCreateSerializer


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientM2MSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeCrUpSerializer(serializers.ModelSerializer):
    ingredients = IngredientM2MSerializer(
        many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time'
        )

    def create(self, validated_data):

        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            cur_ingr = ingredient.get('id')
            cur_amount = ingredient.get('amount')

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=cur_ingr,
                amount=cur_amount
            )
        return recipe

    def to_representation(self, instance):
        recipe_serializer = RecipeReadSerializer(instance)
        return recipe_serializer.data


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id',
    )
    ingredient = serializers.CharField(
        source='ingredient.name',
        required=False
    )
    amount = serializers.ReadOnlyField()
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        required=False
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'ingredient',
            'amount',
            'measurement_unit'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipes',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time'
        )


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('user', 'item')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'favorite')


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('useer', 'author')

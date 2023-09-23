from rest_framework import serializers
from recipes.models import (Recipe, Tag, Shop, Ingredient, Follow, Favorite,
                            RecipeIngredient, CustomUser, RecipeTag)
from djoser.serializers import UserCreateSerializer, UserSerializer


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


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class TagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


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
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
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
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient in ingredients:
            cur_ingr = ingredient.get('id')
            cur_amount = ingredient.get('amount')

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=cur_ingr,
                amount=cur_amount
            )
        for tag_id in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag_id)

        return recipe

    def update(self, instance, validated_data):
        object_id = instance.pk
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        for ingredient in ingredients:
            cur_ingr = ingredient.get('id')
            cur_amount = ingredient.get('amount')
            RecipeIngredient.objects.filter(recipe=object_id).update(
                ingredient=cur_ingr,
                amount=cur_amount
            )
        for tag_id in tags:
            RecipeTag.objects.filter(recipe=object_id).update(
                tag=tag_id)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()
        return instance

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
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    author = CustomUserSerializer(
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

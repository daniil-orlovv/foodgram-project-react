import base64
import re

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.utils import bulk_create_recipe_ingredients, bulk_create_recipe_tags
from recipes.models import (Cart, CustomUser, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Tag)

MAX_VALUE = 32000
MIN_VALUE = 1
MAX_LEN_NAME = 200


class CustomUserCreateSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )

    def validate(self, data):
        data = super().validate(data)
        email = data.get('email')
        username = data.get('username')
        user_full = CustomUser.objects.filter(
            email=email, username=username).exists()
        user_email = CustomUser.objects.filter(email=email).exists()
        user_username = CustomUser.objects.filter(username=username).exists()
        if not user_full and user_email:
            raise serializers.ValidationError('Эта почта занята!')
        if not user_full and user_username:
            raise serializers.ValidationError('Этот username занят!')
        return data

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Используйте буквы, цифры и символы @/./+/-/_')
        return value

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return user.user_followings.filter(author=obj).exists()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return user.user_followings.filter(author=obj).exists()


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
    amount = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeCrUpSerializer(serializers.ModelSerializer):
    ingredients = IngredientM2MSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')
    cooking_time = serializers.IntegerField(
        max_value=MAX_VALUE,
        min_value=MIN_VALUE
    )
    name = serializers.CharField(max_length=MAX_LEN_NAME)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'image',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        return user.user_favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        return user.user_cart.filter(item=obj).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        bulk_create_recipe_ingredients(recipe, ingredients)
        bulk_create_recipe_tags(recipe, tags)

        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        bulk_create_recipe_ingredients(recipe, ingredients)
        RecipeTag.objects.filter(recipe=recipe).delete()
        bulk_create_recipe_tags(recipe, tags)

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
    name = serializers.CharField(
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
            'name',
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
    image = serializers.ReadOnlyField(
        source='image.url')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'image',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return user.user_favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return user.user_cart.filter(item=obj).exists()


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('user', 'item')


class FavoriteCartSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            limit = request.GET.get('recipes_limit')
            recipes = user.author_recipes.filter(author=obj)[:int(limit)]
            return FavoriteCartSerializer(
                recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            return user.author_recipes.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            return user.user_followings.filter(author=obj).exists()

    # def validate(self, data):
    #     request = self.context.get('request')
    #     user = request.user
    #     if user == author:
    #         return Response({
    #             'error': 'Нельзя подписаться на самого себя!'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

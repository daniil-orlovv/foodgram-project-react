
import re
import base64

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from recipes.models import (Recipe, Tag, Shop, Ingredient, RecipeIngredient,
                            CustomUser, RecipeTag, Follow, Favorite)


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
        if Follow.objects.filter(
            user=request.user,
            author=obj
        ).exists():
            return True
        return False


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
            return Follow.objects.filter(
                user=request.user.id,
                author=obj.id
            ).exists()
        return False


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
        if Favorite.objects.filter(
            user=request.user.id,
            recipe=obj.id
        ).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if Shop.objects.filter(
            user=request.user.id,
            item=obj.id
        ).exists():
            return True
        return False

    def validate_name(self, value):
        if len(value) > 200:
            raise serializers.ValidationError(
                'Название не может быть больше 200 символов')
        return value

    def valiate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1 минуты!')
        return value

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
        RecipeTag.objects.filter(recipe=object_id).delete()
        recipe = get_object_or_404(Recipe, id=object_id)
        for tag_id in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag_id)
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
            return Favorite.objects.filter(
                user=request.user.id,
                recipe=obj.id
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Shop.objects.filter(
                user=request.user.id,
                item=obj.id
            ).exists()
        return False


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('user', 'item')


class FavoriteShopSerializer(serializers.ModelSerializer):
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
            limit = request.GET.get('recipes_limit')
            recipes = Recipe.objects.filter(author=obj).order_by(
                '-created')[:int(limit)]
        else:
            recipes = Recipe.objects.filter(author=obj)
        return FavoriteShopSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user.id,
                author=obj.id
            ).exists()
        return False

from rest_framework import serializers
from recipes.models import Recipe, Tag, Shop, Ingredient, Follow, Favorite, RecipeIngredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'name',
            'unit'
        )


class IngredientM2MSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'ingredient',
            'amount'
        )


class RecipeCrUpSerializer(serializers.ModelSerializer):
    ingredients = IngredientM2MSerializer(
        many=True,
        source='ingredients_recipe'
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
            recipes = Recipe.objects.create(**validated_data)

            for ingredient in ingredients:
                cur_ingr = ingredient.get('ingredient')
                amount = ingredient.get('amount')
                recipes.ingredients.add(
                    cur_ingr,
                    through_defaults={
                        'amount': amount,
                    }
                )

            return recipes


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredient.id',
    )
    ingredient = serializers.CharField(
        source='ingredient.name',
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'ingredient',
            'amount'
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipeingredient_set',
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
        fields = ('id', 'title', 'color_code', 'slug')


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

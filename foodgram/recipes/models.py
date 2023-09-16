from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Tag(models.Model):
    title = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        blank=False,
        null=True,
        unique=True,
        default='#FFFFFF'
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        unique=True)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    name = models.CharField(max_length=150, blank=True)
    unit = models.CharField(max_length=20, blank=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='recipes_author'
    )
    name = models.CharField(max_length=200, blank=False, null=False)
    picture = models.ImageField(blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    tags = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='recipes_tags',  # Вроде можно получить все рецепты, которые
        # связаны с тэгом
    )
    cooking_time = models.DurationField(blank=False, null=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='ingredients_recipe',
        blank=True,
        null=True
    )
    is_favorited = models.IntegerField(default=0)
    is_in_shopping_cart = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='ingredient_recipeingredient'
    )
    amount = models.FloatField(blank=False, null=False)


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )


class Shop(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    item = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')


class Meta:
    constraints = [
        models.UniqueConstraint(fields=['user', 'author'],
                                name='user_author_unique')
    ]

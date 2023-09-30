from django.db import models

from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_subscribed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')


class Tag(models.Model):
    name = models.CharField(
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
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=150, blank=True)
    measurement_unit = models.CharField(max_length=20, blank=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    name = models.CharField(max_length=200, blank=False, null=False)
    image = models.ImageField(blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag'
    )
    cooking_time = models.DurationField(blank=False, null=False)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipetag_recipe'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    amount = models.FloatField(blank=True, null=True)


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )


class Shop(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    item = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )


class Follow(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='following')


class Meta:
    constraints = [
        models.UniqueConstraint(fields=['user', 'author'],
                                name='user_author_unique')
    ]

from django.contrib.auth.models import AbstractUser
from django.db import models

MIN_VALUE = 1
MAX_VALUE = 32000


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Почта'
    )
    username = models.CharField(max_length=150, verbose_name='Юзернэйм')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')

    class Meta:
        ordering = ['-email']

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        unique=True,
        default='#00BFFF',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=True,
        related_name='author_recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

    @property
    def added_to_fav(self):
        result = Favorite.objects.filter(recipe=self.id)
        return result.count()


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipetag_recipe',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )

    class Meta:
        ordering = ['-tag']
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'tag'],
                                    name='recipe_tag_unique')
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Количество'
    )

    class Meta:
        ordering = ['-ingredient']


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-user']


class Cart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_cart',
        verbose_name='Пользователь'
    )
    item = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='item_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-user']


class Follow(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='user_followings',
                             verbose_name='Пользователь')
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='author_followers',
                               verbose_name='Автор')

    class Meta:
        ordering = ['-user']
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='user_author_unique')
        ]

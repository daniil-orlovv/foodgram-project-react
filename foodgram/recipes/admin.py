from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (Recipe, RecipeIngredient, Tag, Ingredient, Favorite,
                     Follow, Shop, CustomUser)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username',)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ('recipe', 'ingredient', 'amount',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = (
        'name',
        'author',
        'added_to_fav',
    )
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)
    readonly_fields = ('author',)


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'tag',
    )


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Ingredient)
class ImportExportIngredient(ImportExportModelAdmin):
    pass


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
    search_fields = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class ShopAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'item',
    )
    search_fields = ('user',)
    list_filter = ('user',)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(CustomUser, CustomUserAdmin)

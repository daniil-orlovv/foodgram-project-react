from django.contrib import admin
from .models import (Recipe, RecipeIngredient, Tag, Ingredient, Favorite,
                     Follow, Shop)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ('recipe', 'ingredient', 'amount',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = (
        'author',
        'name',
    )
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)
    readonly_fields = ('author',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
    )
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
    search_fields = ('title',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'favorite',
    )
    search_fields = ('user', 'favorite')
    list_filter = ('user', 'favorite')


class ShopAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'item',
    )
    search_fields = ('user',)
    list_filter = ('user',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Ingredient, IngredientAdmin)

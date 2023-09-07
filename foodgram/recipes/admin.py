from django.contrib import admin
from .models import (Recipe, RecipeIngredient, Tag, Ingredient, Unit, Favorite,
                     Follow, Shop)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ('recipe', 'ingredient', 'amount', 'unit',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = (
        'author',
        'title',
    )
    search_fields = ('title',)
    list_filter = ('author', 'title', 'tag',)
    readonly_fields = ('author',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'unit',
    )
    search_fields = ('recipe', 'ingredient',)
    list_filter = ('ingredient',)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title',
    )
    search_fields = ('title',)


class UnitAdmin(admin.ModelAdmin):
    list_display = (
        'title',
    )
    search_fields = ('title',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'color_code',
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
admin.site.register(RecipeIngredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, ProductAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow)
admin.site.register(Shop, ShopAdmin)

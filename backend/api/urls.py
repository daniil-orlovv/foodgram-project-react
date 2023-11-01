from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CustomDjoserUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = SimpleRouter()

router.register('users', CustomDjoserUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

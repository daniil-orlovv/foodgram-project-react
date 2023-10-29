from django.urls import include, path
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.routers import SimpleRouter

from .views import (FavoriteViewSet, FollowViewSet, IngredientViewSet,
                    RecipeViewSet, ShopViewSet, TagViewSet)

router = SimpleRouter()

router.register('users', DjoserUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('cart', ShopViewSet, basename='get_shop_list')
router.register(r'recipes/(?P<id>\d+)/shopping_cart', ShopViewSet,
                basename='shop')
router.register(r'recipes/(?P<id>\d+)/favorite', FavoriteViewSet,
                basename='favorite')
router.register(r'users/(?P<id>\d+)/subscribe', FollowViewSet,
                basename='follow')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('recipes/download_shopping_cart/',
         ShopViewSet.as_view({'get': 'download'})),
    path('users/subscriptions/', FollowViewSet.as_view(
        {'get': 'subscriptions'})),

    path('auth/', include('djoser.urls.authtoken')),
]

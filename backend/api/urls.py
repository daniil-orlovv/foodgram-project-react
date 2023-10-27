from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CustomUserViewSet, FavoriteViewSet, FollowViewSet,
                    IngredientViewSet, RecipeViewSet, ShopViewSet, TagViewSet,
                    me)

router = SimpleRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('cart', ShopViewSet, basename='get_shop_list')
router.register(r'recipes/(?P<id>\d+)/shopping_cart', ShopViewSet,
                basename='shop')
router.register(r'recipes/(?P<id>\d+)/favorite', FavoriteViewSet,
                basename='favorite')
router.register(r'users/(?P<id>\d+)/subscribe', FollowViewSet,
                basename='follow')
router.register(r'users/(?P<id>\d+)', CustomUserViewSet,
                basename='get_user')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         ShopViewSet.as_view({'get': 'download'})),
    path('users/me/', CustomUserViewSet.as_view({'get': 'me'})),
    path('users/subscriptions/', FollowViewSet.as_view(
        {'get': 'subscriptions'})),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('api/users/me/', me())

]

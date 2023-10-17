from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (RecipeViewSet, ShopViewSet, FavoriteViewSet,
                    FollowViewSet, IngredientViewSet, TagViewSet,
                    CustomUserViewSet)

router = SimpleRouter()


router.register(r'users', CustomUserViewSet, basename='get_user')
router.register(
    'users/subscriptions', FollowViewSet, basename='getfollows')
router.register(
    r'users/(?P<id>\d+)/subscribe', FollowViewSet, basename='follow')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'recipes/(?P<id>\d+)/shopping_cart', ShopViewSet,
                basename='shop')
router.register(r'recipes/(?P<id>\d+)/favorite', FavoriteViewSet,
                basename='favorite')
router.register('tags', TagViewSet, basename='tags')
router.register('cart', ShopViewSet, basename='get_shop_list')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         ShopViewSet.as_view({'get': 'download'})),
    path('users/me/', CustomUserViewSet.as_view({'get': 'me'})),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

]

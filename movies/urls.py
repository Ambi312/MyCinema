from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (MovieViewSet, ReviewCreateViewSet,
                    AddStarRatingViewSet, ActorsViewSet, FavouriteViewSet, GenreViewSet)

router = SimpleRouter()
router.register('genre', GenreViewSet)
router.register('favourites', FavouriteViewSet)
router.register('actor', ActorsViewSet)

urlpatterns = format_suffix_patterns([
    path("movie/", MovieViewSet.as_view({'get': 'list'})),
    path("movie/<int:pk>/", MovieViewSet.as_view({'get': 'retrieve'})),
    path("review/", ReviewCreateViewSet.as_view({'post': 'create'})),
    path("rating/", AddStarRatingViewSet.as_view({'post': 'create'})),
    path('', include(router.urls))
])

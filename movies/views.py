from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .permissions import IsAdmin
from .serializers import *
from .service import MovieFilter


class MovieViewSet(ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter

    def get_queryset(self):
        movies = Movie.objects.all()
        return movies

    def get_serializer_class(self):
        if self.action == 'list':
            return MovieListSerializer
        elif self.action == "retrieve":
            return MovieDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q')
        queryset = self.get_queryset().filter(Q(title__icontains=query) |
                                              Q(description__icontains=query))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdmin]


class ReviewCreateViewSet(ModelViewSet):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['action'] = self.action
        return context

    @action(detail=True, methods=['get'])
    def like(self, request, pk):
        user = request.user
        review = get_object_or_404(Review, pk=pk)
        if user.is_authenticated:
            if user in review.likes.all():
                review.likes.remove(user)
                message = 'Unliked!'
            else:
                review.likes.add(user)
                message = 'Liked!'
        context = {'Status': message}
        return Response(context, status=200)


class AddStarRatingViewSet(ModelViewSet):
    serializer_class = CreateRatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ActorsViewSet(ModelViewSet):
    queryset = Actor.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ActorSerializer
        elif self.action == "retrieve":
            return ActorDetailSerializer


class FavouriteViewSet(ModelViewSet):
    queryset = Movie.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'add_to_favorites', 'remove_from_favorites']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return []

    @action(['POST'], detail=True)
    def add_to_favorites(self, request, pk=None):
        movie = self.get_object()
        if request.user.added_to_favorites.filter(movie=movie).exists():
            return Response('Уже добавлено в избранное')
        Favourites.objects.create(movie=movie, user=request.user)
        return Response('Добавлено в избранное')

    @action(['POST'], detail=True)
    def remove_from_favorites(self, request, pk=None):
        movie = self.get_object()
        if not request.user.added_to_favorites.filter(movie=movie).exists():
            return Response('Фильм не находится в списке избранных')
        request.user.added_to_favorites.filter(movie=movie).delete()
        return Response('Фильм удален из избранных')

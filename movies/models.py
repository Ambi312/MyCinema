from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import date
from django.urls import reverse

from account.models import MyUser


class Category(models.Model):
    name = models.CharField(max_length=150)
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Actor(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveSmallIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to="actors")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('actor_detail', kwargs={"slug": self.name})

    class Meta:
        verbose_name = "Actor and Director"
        verbose_name_plural = "Actors and Directors"


class Genre(models.Model):
    name = models.CharField(max_length=100)
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"


class Movie(models.Model):
    title = models.CharField(max_length=100)
    tagline = models.CharField(max_length=100, default='')
    description = models.TextField()
    poster = models.ImageField(upload_to="movies")
    year = models.PositiveSmallIntegerField()
    country = models.CharField(max_length=30)
    directors = models.ManyToManyField(Actor, verbose_name="directors", related_name="film_director")
    actors = models.ManyToManyField(Actor, verbose_name="actors", related_name="film_actor")
    genres = models.ManyToManyField(Genre, verbose_name="genres")
    world_premiere = models.DateField(default=date.today)
    category = models.ForeignKey(Category, verbose_name="Category", on_delete=models.SET_NULL, null=True)
    url = models.URLField(max_length=200, default='')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("movie_detail", kwargs={"slug": self.url})

    def get_review(self):
        return self.reviews_set.filter(parent__isnull=True)

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"


class Favorites(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.CASCADE,
                             related_name='added_to_favorites')

    class Meta:
        unique_together = ['movie', 'user']


class Rating(models.Model):
    star = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="movie", related_name="ratings")

    def __str__(self):
        return f"{self.star} - {self.movie}"

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"


class Review(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=100)
    text = models.TextField(max_length=5000)
    parent = models.ForeignKey('self', verbose_name="Parent", on_delete=models.SET_NULL, blank=True, null=True,
                               related_name="children")
    movie = models.ForeignKey(Movie, verbose_name="movie", on_delete=models.CASCADE, related_name="reviews")
    likes = models.ManyToManyField(MyUser, related_name='likers', blank=True)

    def __str__(self):
        return f"{self.name} - {self.movie}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

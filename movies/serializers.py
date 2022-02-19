from rest_framework import serializers

from .models import *


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'


class ActorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = "__all__"


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ("title", "tagline", "poster", 'url')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "name", "text", "children")

    def to_representation(self, instance):
        representation = super(ReviewSerializer, self).to_representation(instance)
        representation['likes'] = instance.likes.count()
        action = self.context.get('action')
        if action == 'list':
            representation['comments'] = instance.commenty.count()
        else:
            representation['comments'] = ReviewCreateSerializer(instance.commenty.all(), many=True).data
        return representation


class MovieDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    directors = ActorSerializer(read_only=True, many=True)
    actors = ActorSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        fields = '__all__'


class CreateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("star", "movie")

    @staticmethod
    def validate_star(star):
        if star not in range(1, 6):
            raise serializers.ValidationError('Рейтинг должен быть от 1 до 5')
        return star

    def create(self, validated_data):
        rating, _ = Rating.objects.update_or_create(
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get("star")}
        )
        return rating

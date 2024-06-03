from django.contrib.auth.models import User
from geopy import Nominatim
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Post, Comment, Like, PostImage


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = '__all__'


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer для изображений в посте."""

    class Meta:
        model = PostImage
        fields = ('id', 'image',)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer для комментариев под постом."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'text', 'created_at', 'updated_at',)

    def to_representation(self, instance):
        """Вывод данных пользователю."""

        rep = super().to_representation(instance)
        rep['user'] = User.objects.get(id=instance.user.id).username
        return rep


class PostSerializer(serializers.ModelSerializer):
    """Serializer для постов."""

    images = PostImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=None, use_url=True),
        write_only=True,
        min_length=1
    )

    comments = CommentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'user', 'text', 'images',
                  'uploaded_images', 'location',
                  'comments', 'created_at',
                  'updated_at',)

    def create(self, validated_data):
        """Создание поста."""

        uploaded_images = validated_data.pop('uploaded_images')
        validated_data['user'] = self.context['request'].user

        if validated_data.get('location'):
            geolocator = Nominatim(user_agent='posts')
            my_location = geolocator.geocode(validated_data['location'])
            if not my_location:
                raise ValidationError('Указано несуществующее место')
            validated_data['location'] = (f'{str(my_location.latitude)}, '
                                          f'{str(my_location.longitude)}')

        post = Post.objects.create(**validated_data)
        for image in uploaded_images:
            PostImage.objects.create(post=post, image=image)
        return post

    def to_representation(self, instance):
        """Вывод данных пользователю."""

        rep = super().to_representation(instance)
        rep['likes_count'] = len(Like.objects.filter(post_id=instance.id))
        rep['user'] = User.objects.get(id=instance.user.id).username

        if rep.get('location'):
            geolocator = Nominatim(user_agent='posts')
            coordinates = rep['location']
            location = geolocator.reverse(coordinates)
            rep['location'] = location.address
        else:
            rep.pop('location')

        return rep


class AddCommentSerializer(serializers.ModelSerializer):
    """Serializer для создания комментария."""

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_at',)

    def create(self, validated_data):
        """Создание комментария."""

        validated_data['user'] = self.initial_data.get('user')
        validated_data['post'] = self.initial_data.get('post')
        validated_data['text'] = self.initial_data.get('text')
        return super().create(validated_data)


class EditCommentSerializer(serializers.ModelSerializer):
    """Serializer для изменения комментария."""

    class Meta:
        model = Comment
        fields = ('text',)

    def update(self, instance, validated_data):
        """Изменение поста."""

        instance = instance[0]
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance


class AddLikeSerializer(serializers.ModelSerializer):
    """Serializer для создания лайка."""

    class Meta:
        model = Like
        fields = ('id',)

    def create(self, validated_data):
        """Создание лайка."""

        validated_data['user'] = self.initial_data.get('user')
        validated_data['post'] = self.initial_data.get('post')
        return super().create(validated_data)

    def validate(self, data):
        """Валидация данных на наличие лайка."""

        if Like.objects.filter(
            user_id=self.initial_data.get('user').id,
            post_id=self.initial_data.get('post').id
        ):
            raise ValidationError('На данной записи уже есть лайк от этого пользователя')
        return data

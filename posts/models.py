from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    """Пост."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=256, blank=True, null=True)
    location = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    """Комментарий."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')


class Like(models.Model):
    """Лайк."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'post'),
                name='unique_like'
            ),
        )


class PostImage(models.Model):
    """Фотографии поста."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')

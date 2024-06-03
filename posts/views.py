from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Post, Comment, Like
from .permissions import IsOwner
from .serializers import PostSerializer, EditCommentSerializer, AddCommentSerializer, AddLikeSerializer


class PostViewSet(ModelViewSet):
    """ViewSet для постов."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        """Получение и проверка прав."""

        if self.action in [
            'create',
            'add_comment',
            'edit_comment',
            'del_comment',
            'add_like',
            'del_like'
        ]:
            return [IsAuthenticated()]
        if self.action in [
            'destroy',
            'update',
            'partial_update'
        ]:
            return [IsOwner()]
        return []

    @action(detail=True, methods=['POST'])
    def add_comment(self, request, pk=None):
        """Добавление комментария."""

        user = request.user
        post = self.get_object()
        text = request.data['text']
        data = {
            'post': post,
            'user': user,
            'text': text
        }
        serializer = AddCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'])
    def del_comment(self, request, pk=None):
        """Удаление комментария.
        Query params: comment_id.
        """

        if request.query_params.get('comment_id'):
            comment_id = request.query_params.get('comment_id')
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        post = self.get_object()
        user = request.user
        post_owner = post.user
        if not Comment.objects.filter(id=comment_id, post=post):
            return Response(status=status.HTTP_404_NOT_FOUND)
        if Comment.objects.filter(
                id=comment_id,
                user=user,
                post=post
        ) or user.is_staff or user == post_owner:
            Comment.objects.get(id=comment_id,
                                post=post
                                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                'Комментарий пользователя не найден',
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['PATCH'])
    def edit_comment(self, request, pk=None):
        """Изменение комментария.
        Query params: comment_id.
        """

        post = self.get_object()
        text = request.data['text']
        if request.query_params.get('comment_id'):
            comment_id = request.query_params.get('comment_id')
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user = request.user
        instance = Comment.objects.filter(
                id=comment_id,
                user=user,
                post=post
        )
        if not instance:
            return Response('Комментарий пользователя не найден',
                            status=status.HTTP_404_NOT_FOUND)
        data = {
            'text': text
        }
        serializer = EditCommentSerializer(data=data, instance=instance)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['POST'])
    def add_like(self, request, pk=None):
        """Добавление лайка."""

        post = self.get_object()
        user = request.user
        data = {
            'post': post,
            'user': user,
        }
        serializer = AddLikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['DELETE'])
    def del_like(self, request, pk=None):
        """Удаление лайка."""

        post = self.get_object()
        user = request.user
        if Like.objects.filter(user=user, post=post):
            Like.objects.get(user=user, post=post).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                'Лайк от этого пользователя на данной записи отсутствует',
                status=status.HTTP_404_NOT_FOUND
            )

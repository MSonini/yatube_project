from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст',
                            help_text='Текст новой записи',)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey('Group',
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text='Группа, к которой относится запись')
    image = models.ImageField('Картинка',
                              upload_to='posts/',
                              blank=True,)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(max_length=200,)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey('Post',
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Запись')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')
    text = models.TextField(max_length=200,
                            verbose_name='Текст',
                            help_text='Текст комментария',)

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return self.text[:30]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор')

    class Meta:
        unique_together = ['user', 'author']

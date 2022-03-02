from django import forms

from .models import Comment, Post
from .validators import clean_text


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {'text': forms.Textarea}
        labels = {
            'text': 'Введите текст нового поста',
            'group': 'Выберите группу',
            'image': 'Загрузите картинку',
        }
        help_texts = {'group': 'К этой группе будет относиться ваш пост'}
        validators = {'text': clean_text}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': forms.Textarea}
        labels = {'text': 'Текст комментария'}
        validators = {'text': clean_text}

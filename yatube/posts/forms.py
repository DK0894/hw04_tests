from django import forms

from .models import Post
from .validators import clean_text


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')
        widgets = {'text': forms.Textarea}
        labels = {'text': 'Введите текст нового поста',
                  'group': 'Выберите группу'}
        help_texts = {'group': 'К этой группе будет относиться ваш пост'}
        validators = {'text': clean_text}

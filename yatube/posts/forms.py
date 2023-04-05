from django import forms
from django.contrib.auth import get_user_model

from posts.models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Hапишите ваш комментарий'}
        widgets = {'text': forms.Textarea({'rows': 3})}

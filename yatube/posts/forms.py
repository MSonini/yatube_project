from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'cols': 40,
                'placeholder': 'Текст записи'
            }),
            'group': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'text': 'Текст записи',
            'group': 'Группа'
        }
        help_texts = {
            'text': 'Текст новой записи',
            'group': 'Группа, к которой относится запись',
        }

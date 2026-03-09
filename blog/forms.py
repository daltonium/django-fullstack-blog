from django import forms
from .models import Post, Comment, Tag


class PostForm(forms.ModelForm):
    tag_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'django, python, tutorial ...',
            'class': 'tag-input',
        }),
        label='Tags (comma separated)',
    )

    class Meta:
        model = Post
        fields = ['title', 'excerpt', 'body', 'category', 'cover_image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Your post title...'}),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief summary of your post...'}),
            'body': forms.Textarea(attrs={'rows': 18, 'placeholder': 'Write your post content here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            existing_tags = ', '.join(self.instance.tags.values_list('name', flat=True))
            self.fields['tag_input'].initial = existing_tags

    def save(self, commit=True):
        post = super().save(commit=commit)
        if commit:
            self._save_tags(post)
        return post

    def _save_tags(self, post):
        tag_names = [
            t.strip().lower()
            for t in self.cleaned_data.get('tag_input', '').split(',')
            if t.strip()
        ]
        tags = []
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        post.tags.set(tags)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts...',
            }),
        }
        labels = {'body': ''}


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search posts...',
            'autocomplete': 'off',
        }),
        label='',
    )

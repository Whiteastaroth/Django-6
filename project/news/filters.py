import django_filters
from django import forms
from .models import New

CATEGORIES_CHOICES = [
    ('uncos', 'Новости'),
    ('articles', 'Статьи'),
]


class NewFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Поиск по названию'
    )
    category = django_filters.ChoiceFilter(
        choices=CATEGORIES_CHOICES,
        label='Поиск по категории',
        empty_label = 'Любой'
    )
    data_pub = django_filters.DateFilter(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Поиск по дате'
    )

    class Meta:
        model = New
        fields = ['title', 'category', 'data_pub']
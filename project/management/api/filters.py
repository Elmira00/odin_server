import django_filters
from management.models import Problem

class ProblemFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__category', lookup_expr='icontains')

    created_date = django_filters.DateFilter(field_name='created_at', lookup_expr='date')

    id = django_filters.NumberFilter(field_name='id')

    class Meta:
        model = Problem
        fields = ['category', 'created_date', 'id']

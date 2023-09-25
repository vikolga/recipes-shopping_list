from django_filters.rest_framework import FilterSet, filters

class LimitFilter(FilterSet):
    recipes_limit = filters.NumberFilter(method='recipes_limit')

    def recipes_limit(self, queryset, name, value):
        return queryset.recipes_limit(value)
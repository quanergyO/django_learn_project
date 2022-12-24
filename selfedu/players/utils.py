from django.db.models import Count
from django.core.cache import cache

from .models import Category


class DataMixin:
    paginate_by = 3

    def get_user_context(self, **kwargs):
        contex = kwargs
        cats = cache.get('cats')
        if not cats:
            cats = Category.objects.all()
            cache.set('cats', cats, 60)

        contex['cats'] = cats
        if 'cat_selected' not in contex:
            contex['cat_selected'] = 0
        return contex

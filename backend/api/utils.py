from datetime import datetime

from django.http import HttpResponse
from django.db.models import Sum
from requests import Response
from rest_framework import status

from recipes.models import IngredientRecipes


def get_shopping_cart(user):
    """Функция скачивания списка покупок."""
    if user.is_anonymous:
        return Response(
            {'error': 'Учетные данные не были предоставлены.'},
            status=status.HTTP_401_UNAUTHORIZED)
    ingredients = IngredientRecipes.objects.filter(
        recipe__shopping_cart__user=user
    ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
        amount=Sum('amount')
    )
    data_shopping_cart = datetime.today()
    list_shopping = ('Список покупок из рецептов от '
                     f'{data_shopping_cart:%d.%m.%Y}\n')
    list_shopping += '\n'.join([
        f'- {ingredient["ingredient__name"]}'
        f'({ingredient["ingredient__measurement_unit"]}) : '
        f'{ingredient["amount"]}'
        for ingredient in ingredients
    ])
    file = 'shopping_cart.txt'
    response = HttpResponse(list_shopping, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file}'
    return response

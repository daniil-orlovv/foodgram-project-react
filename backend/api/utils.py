from recipes.models import RecipeIngredient, RecipeTag


def bulk_create_recipe_ingredients(recipe, ingredients):
    ingredient_list = []

    for ingredient in ingredients:
        cur_ingr = ingredient.get('id')
        cur_amount = ingredient.get('amount')
        ingredient_obj = RecipeIngredient(
            recipe=recipe,
            ingredient=cur_ingr,
            amount=cur_amount
        )
        ingredient_list.append(ingredient_obj)

    RecipeIngredient.objects.bulk_create(ingredient_list)


def bulk_create_recipe_tags(recipe, tags):
    tags_list = []

    for tag_id in tags:
        tag_obj = RecipeTag(
            recipe=recipe,
            tag=tag_id
        )
        tags_list.append(tag_obj)
    RecipeTag.objects.bulk_create(tags_list)

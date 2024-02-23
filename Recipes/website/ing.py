from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import driver
import json

ing = Blueprint('ing', __name__)

# Define a route for the home page
@ing.route('/')
def home():
    return render_template('home.html')


def get_recipes(tx, ingredients):
    result = tx.run("""
       MATCH (r:Recipe)
       WHERE all(i in $ingredients WHERE exists((r)-[:CONTAINS_INGREDIENT]->(:Ingredient {name: i})))
       RETURN r.name AS name,[(r)-[:CONTAINS_INGREDIENT]->(i) | i.name] AS ingredients,
         r.skillLevel as Level
       ORDER BY size(ingredients)
       LIMIT 40
    """, ingredients=ingredients)

    return list(result)

def get_recipe_by_ingredient(ingredient):
    with driver.session() as session:
        result = session.run("""
            MATCH (r:Recipe)-[:CONTAINS_INGREDIENT]->(i:Ingredient {name: $ingredient})
            RETURN r.name AS name, [(r)-[:CONTAINS_INGREDIENT]->(i) | i.name] AS ingredients,
                r.skillLevel AS level
            LIMIT 1
        """, ingredient=ingredient)
        
        recipe = result.single()
        if recipe is not None:
            recipe_data = {
                'name': recipe['name'],
                'ingredients': recipe['ingredients'],
                'level': recipe['level']
            }
            return recipe_data
        else:
            return None



# Define a route for the search page
@ing.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    ingredients = [ingredient.strip() for ingredient in query.split(',')]
    nodes = {}
    for ingredient in ingredients:
        recipe = get_recipe_by_ingredient(ingredient)
        if recipe is not None:
            recipe_name = recipe['name']
            if recipe_name in nodes:
                nodes[recipe_name].append(recipe_name)
            else:
                nodes[recipe_name] = [recipe_name]
    return render_template('search.html', nodes=nodes)



@ing.route('/about')
def about():
    return render_template('about.html')


@ing.route('/find')
def find():
    return render_template('find.html')


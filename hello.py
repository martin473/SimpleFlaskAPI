from flask import Flask, jsonify, request, make_response
import json
from markupsafe import escape

#specify db name
database = 'data.json'
app = Flask(__name__)

#this page opens the db, and returns a list of the names
#of every recipe in json format
@app.route('/recipes')
def get_recipes():
    f = open(database,)
    recipes = json.load(f)
    names = []
    for recipe in recipes['recipes']:
        names.append(recipe['name'])
    response = {"recipeNames": names}
    jsonify(response)
    f.close()
    return response

#if <recipeName> exists in the json db, this will
#show the ingredients and number of steps in the
#recipe in JSON. Otherwise it returns empty JSON of {}
#recipe must fit the proper format. If a recipe is 
#improperly formatted via other POST methods, this
#webpage will fail
@app.route('/recipes/details/<recipeName>')
def get_recipe_details(recipeName):
    f = open(database,)
    recipes = json.load(f)
    details = ""
    numSteps = 0
    recipeName = recipeName.replace('"', '')
    for recipe in recipes['recipes']:
        if recipe['name'] == escape(recipeName):
          details = recipe
    if details:
        for step in details['instructions']:
            numSteps += 1
        details = { "details": {"ingredients": 
            details['ingredients'], "numSteps": numSteps}}
    else:
        details = {}
    f.close()
    return jsonify(details)

#No input validation is run. Proper input is expected.
#check data.json to review proper format.
#Will save a new recipe to the database. If the recipe
#already exists, it will return an error message
@app.route('/recipes', methods=['POST'])
def add_recipe():
  newRecipe = request.get_json()
  f = open(database,)
  recipes = json.load(f)
  f.close()
  for recipe in recipes['recipes']:
      if recipe['name'] == escape(newRecipe['name']):
          return jsonify('{"error": "Recipe already exists"}', 400)
  recipes['recipes'].append(newRecipe)
  f = open(database, "w")
  json.dump(recipes, f)
  f.close()
  return '', 201

#Same formatting issues as previous method. Will over-
#write an existing recipe with whatever input is entered
#Will update a current recipe. If it doesn't exist, will
#return an error
@app.route('/recipes', methods=['PUT'])
def update_recipe():
  updatedRecipe = request.get_json()
  f = open(database,)
  recipes = json.load(f)
  f.close()
  currRecipe = -1
  for recipe in recipes['recipes']:
      currRecipe += 1
      if recipe['name'] == escape(updatedRecipe['name']):
          recipe = updatedRecipe
          name = recipe['name']
          recipes['recipes'][currRecipe] = updatedRecipe
          f = open(database, "w")
          json.dump(recipes, f)
          f.close()
          return '', 204
  return jsonify('{"error": "Recipe doesn\'t exists"}', 404)
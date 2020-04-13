import os
from flask import Flask, render_template, request, url_for, redirect
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import re
import requests

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)

def update_quantity_in_category(category):
    """ Updates the number of recipes in the given recipe category """

    # counts the number of recipes
    counter = mongo.db.recipes.find({'category' : category}).count()

    # updates quantity in the database
    mongo.db.recipe_categories.update({'name': category},
        {
            '$set' : {
                'number_of_recipes' : counter
            }
        })


def validate_form(form, collection):
    """ Returns an error list if the recipe, recipe collection or review form fails on validation """
    
    # variable initialization
    max_title = 50
    max_ingredients = 500
    max_method = 1500
    max_recipe_img_URL = 250
    max_servings = 100
    max_category_name = 50
    max_category_img_URL = 250
    max_review = 250
    error_list = []

    # validates recipe form
    if collection == 'recipe':
        if not form['title'] or len(form['title']) > max_title:
            error_list.append('Title must not be empty or more than {} characters!'.format(max_title))

        if not form['ingredients'] or len(form['ingredients']) > max_ingredients:
            error_list.append('Ingredients must not be empty or more than {} characters!'.format(max_ingredients))

        if not form['method'] or len(form['method']) > max_method:
            error_list.append('Method must not be empty or more than {} characters!'.format(max_method))

        if 'appliance_categories' not in form:
            error_list.append('At least one of the appliances should be checked!')

        if not form['img_link'] or len(form['img_link']) > max_recipe_img_URL:
            error_list.append('Image URL must not be empty or more than {} characters!!'.format(max_recipe_img_URL))

        try:
            if not form['servings'] or int(form['servings']) > max_servings:
                error_list.append('Servings must not be empty or more than {}!'.format(max_servings))

        except ValueError:
            error_list.append('Servings is not a number!')
    
    # validates recipe category form
    elif collection == 'recipe_category':
        if not form['name'] or len(form['name']) > max_category_name:
            error_list.append('Category name must not be empty or more than {} characters!'.format(max_category_name))

        if not form['img_link'] or len(form['img_link']) > max_category_img_URL:
            error_list.append('Image URL must not be empty or more than {} characters!'.format(max_category_img_URL))
    
    # validates review form
    elif collection == 'review':
        if not form['review'] or len(form['review']) > max_review:
            error_list.append('Review must not be empty or more than {} characters!'.format(max_review))

    # returns errors if there is any        
    return error_list


def validate_image(image):
    """ Returns image URL if the URL is an image, otherwise returns a fallback URL """
    
    # sets fallback URL
    fallback_URL = url_for('static', filename='images/default.png')

    try:
        # tries to get a response and the content type of the URL
        resp = requests.get(image)
        r = resp.headers.get('content-type')

        # tests if the URL is valid and image
        if resp.status_code == 200:
            # URL is valid
            if r == 'image/jpeg' or r == 'image/bmp' or r == 'image/png' or r == 'image/gif':
                # URL is image
                return image
            
            else:
                # URL is not an image
                return fallback_URL

        else:
            # URL is invalid
            return fallback_URL

    except:
        # URL is invalid
        return fallback_URL


@app.route('/')
def index():
    """ Returns the landing page """

    # initializes page title
    page_title = 'Home'

    # renders the landing page
    return render_template('index.html', page_title=page_title)


@app.route('/search', methods=['GET'])
def search():
    """ Returns all recipes, recipes by category, all appliances or appliances by category and both categories """

    if request.args['collection'] == 'recipes':
        if request.args['find'] == 'all':
            # initializes page title and header
            page_title = 'All recipes'
            page_header = 'All recipes search results:'
            
            # returns all recipes
            return render_template('search.html', recipes=mongo.db.recipes.find().sort('title'), page_title=page_title, page_header=page_header)

        else:
            # initializes page title and header
            page_title = 'Recipes by category'
            page_header = 'Recipes by category search results:'
            
            # searches for recipes by category
            recipes = mongo.db.recipes.find({"category": request.args['find']}).sort('title')
            
            if recipes.count() > 0:
                # returns search results
                return render_template('search.html', recipes=recipes, page_title=page_title, page_header=page_header)
            else:
                # returns an error message if there is no result
                return render_template('error.html', msg='No results found!')
    
    elif request.args['collection'] == 'recipe_categories':
        # initializes page title and header
        page_title = 'Recipe categories'
        page_header = 'Recipe categories search results:'
        
        # returns all recipe categories
        return render_template('search.html', recipe_categories=mongo.db.recipe_categories.find().sort('name'), page_title=page_title, page_header=page_header)
    
    elif request.args['collection'] == 'appliances':
        if request.args['find'] == 'all':
            # initializes page title and header
            page_title = 'All appliances'
            page_header = 'All appliances search results:'
            
            # returns all appliances
            return render_template('search.html', appliances=mongo.db.appliances.find().sort('brand'), page_title=page_title, page_header=page_header)
        
        else:
            # initializes page title and header
            page_title = 'Appliances by category'
            page_header = 'Appliances by category search results:'

            # searches for appliances by category
            appliances = mongo.db.appliances.find({"type": request.args['find']}).sort('brand')
            
            if appliances.count() > 0:
                # returns search results
                return render_template('search.html', appliances=appliances, page_title=page_title, page_header=page_header)
            
            else:
                # returns an error message if there is no result
                return render_template('error.html', msg='No results found!')
    
    elif request.args['collection'] == 'appliance_categories':
        # initializes page title and header
        page_title = 'Appliance categories'
        page_header = 'Appliance categories search results:'
        
        # returns appliance categories
        return render_template('search.html', appliance_categories=mongo.db.appliance_categories.find().sort('name'), page_title=page_title, page_header=page_header)
    
    else:
        # returns an error message on incorrect argument
        return render_template('error.html', msg='Bad argument error! (/search)')


@app.route('/', methods=['POST'])
@app.route('/navsearch', methods=['POST'])
def navsearch():
    """ Returns ingredient search results """

    # initializes page title and header
    page_title = 'Ingredient search'
    page_header = 'Ingredient search results:'

    # regex search
    search_text = re.compile(request.form.get('search'), re.IGNORECASE)
    recipes = mongo.db.recipes.find({'ingredients': {'$in': [search_text]}}).sort('title')

    if recipes.count() > 0:
        # returns the results
        return render_template('navsearch.html', recipes=recipes, page_title=page_title, page_header=page_header)
    
    else:
        # returns to an error message if there is no reult
        return render_template('error.html', msg='No result found!')


@app.route('/view/<db_id>', methods=['GET'])
def view(db_id):
    """ Returns a recipe or an appliance to view individually """

    if request.args['collection'] == 'recipes':
        # initializes page title
        page_title = 'View a recipe'
        
        # increases view stat
        mongo.db.recipes.update({'_id': ObjectId(db_id)},
        {
            '$inc' : {
                'view_stat' : 1
            }
        })
        
        # returns the view of the selected recipe
        return render_template('view.html', recipe=mongo.db.recipes.find_one({"_id": ObjectId(db_id)}), page_title=page_title)
    
    elif request.args['collection'] == 'appliances':
        # initializes page title
        page_title = 'View an appliance'

        # increases view stat
        mongo.db.appliances.update({'_id': ObjectId(db_id)},
        {
            '$inc' : {
                'view_stat' : 1
            }
        })

        # returns the view of the selected appliance
        return render_template('view.html', appliance=mongo.db.appliances.find_one({"_id": ObjectId(db_id)}), page_title=page_title)
    
    else:
        # returns an error message on incorrect argument
        return render_template('error.html', msg='Bad argument error! (/view)')


@app.route('/add_form', methods=['GET'])
def add_form():
    """ Returns a form for a new recipe or recipe category """

    if request.args['collection'] == 'recipe':
        # initializes page title and header
        page_title = 'Add recipe'
        page_header = 'Add a new recipe:'
        
        # returns the add recipe template
        return render_template('add_form.html', collection=mongo.db.recipe_categories.find().sort('name'), categories=mongo.db.appliance_categories.find().sort('name)'), page_title=page_title, page_header=page_header)
    
    elif request.args['collection'] == 'category':
        # initializes page title and header
        page_title = 'Add recipe category'
        page_header = 'Add a new recipe category:'
        
        # returns the add recipe category template
        return render_template('add_form.html', page_title=page_title, page_header=page_header)
    
    else:
        # returns an error message on incorrect argument
        return render_template('error.html', msg='Bad argument error! (/add_form)')


@app.route('/edit_form/<db_id>', methods=['GET'])
def edit_form(db_id):
    """ Returns a form to edit an existing recipe or recipe category """

    if request.args['collection'] == 'recipe':
        # initializes page title and header
        page_title = 'Update recipe'
        page_header = 'Update a recipe:'

        # returns the edit recipe template
        return render_template('edit_form.html', collection=mongo.db.recipe_categories.find().sort('name'), recipe = mongo.db.recipes.find_one({"_id": ObjectId(db_id)}), categories=mongo.db.appliance_categories.find().sort('name'), page_title=page_title, page_header=page_header)
    
    elif request.args['collection'] == 'recipe_category':
        # initializes page title and header
        page_title = 'Update recipe category'
        page_header = 'Update a recipe category:'
        
        # returns the edit recipe category template
        return render_template('edit_form.html', recipe_category=mongo.db.recipe_categories.find_one({"_id": ObjectId(db_id)}), page_title=page_title, page_header=page_header)
    
    else:
        # returns an error message on incorrect argument
        return render_template('error.html', msg='Bad argument error! (/edit_form)')


@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    """ Inserts a recipe into the database and redirects to the list of all recipes """

    # validates request form
    form = request.form
    appliance_list = request.form.getlist('appliance_categories')
    error_list = validate_form(form, 'recipe')

    if error_list == []:
        # validates image URL
        image_URL = validate_image(form['img_link'])

        # inserts recipe
        recipe = {
            'title' :  request.form.get('title'),
            'category' : request.form.get('category'),
            'ingredients' : request.form.get('ingredients').split('\n'),
            'method' : request.form.get('method').split('\n'),
            'appliances' : request.form.getlist('appliance_categories'),
            'img_link' : image_URL,
            'reviews' : [],
            'servings' : request.form.get('servings'),
            'view_stat' : 0
        }
        mongo.db.recipes.insert_one(recipe)

        # updates recipe numbers in category
        update_quantity_in_category(request.form.get('category'))

        # redirects to the landing page
        return redirect(url_for('index'))
    
    else:
        # initializes page title and header
        page_title = 'Add recipe'
        page_header = 'Add a new recipe:'
        
        # sends error list back to the form to correct mistakes
        return render_template('add_form.html', collection=mongo.db.recipe_categories.find().sort('name'), categories=mongo.db.appliance_categories.find().sort('name)'), errors=error_list, form=form, appliance_list=appliance_list, page_title=page_title, page_header=page_header)


@app.route('/insert_recipe_category', methods=['POST'])
def insert_recipe_category():
    """ Inserts a recipe category into the database and redirects to the list of all recipe categories """

    # validates request form
    form = request.form
    error_list = validate_form(form, 'recipe_category')

    if error_list == []:
        # validates image URL
        image_URL = validate_image(form['img_link'])

        # inserts recipe category
        recipe_category = {
            'name' :  request.form.get('name'),
            'img_link' : image_URL,
            'number_of_recipes' : 0
        }
        mongo.db.recipe_categories.insert_one(recipe_category)

        # redirects to the landing page
        return redirect(url_for('index'))
    
    else:
        # initializes page title and header
        page_title = 'Add recipe category'
        page_header = 'Add a new recipe category:'
        
        # sends error list back to the form to correct mistakes
        return render_template('add_form.html', errors=error_list, form=form, page_title=page_title, page_header=page_header)


@app.route('/update_recipe/<db_id>', methods=['POST'])
def update_recipe(db_id):
    """ Updates a recipe in the database and redirects to the list of all recipes """

    # validates request form
    form = request.form
    appliance_list = request.form.getlist('appliance_categories')
    error_list = validate_form(form, 'recipe')

    if error_list == []:
        # validates image URL
        image_URL = validate_image(form['img_link'])

        # keeps the old category name in case of change
        previous_category = mongo.db.recipes.find_one({'_id': ObjectId(db_id)})['category']
        
        # updates recipe
        mongo.db.recipes.update({'_id': ObjectId(db_id)},
        {
            '$set': {
                'title' :  request.form.get('title'),
                'category' : request.form.get('category'),
                'ingredients' : request.form.get('ingredients').split('\n'),
                'method' : request.form.get('method').split('\n'),
                'appliances' : request.form.getlist('appliance_categories'),
                'img_link' : image_URL,
                'servings' : request.form.get('servings')
            }
        })

        # updates counter in the old category (the recipe was taken from)
        update_quantity_in_category(previous_category)

        # updates counter in the new category (the recipe was moved to)
        update_quantity_in_category(request.form.get('category'))

        # redirects to the landing page
        return redirect(url_for('index'))
    
    else:
        # initializes page title and header
        page_title = 'Update recipe'
        page_header = 'Update a recipe:'

        # sends error list back to the form to correct mistakes
        return render_template('edit_form.html', collection=mongo.db.recipe_categories.find().sort('name'), recipe = mongo.db.recipes.find_one({"_id": ObjectId(db_id)}), categories=mongo.db.appliance_categories.find().sort('name'), errors=error_list, form=form, appliance_list=appliance_list, page_title=page_title, page_header=page_header)


@app.route('/update_recipe_category/<db_id>', methods=['POST'])
def update_recipe_category(db_id):
    """ Updates a recipe category in the database and redirects to the list of all recipe categories """

    # validates request form
    form = request.form
    error_list = validate_form(form, 'recipe_category')

    if error_list == []:
        # validates image URL
        image_URL = validate_image(form['img_link'])

        # keeps the old category name in case of change
        previous_name = mongo.db.recipe_categories.find_one({'_id': ObjectId(db_id)})['name']

        # updates recipe category
        mongo.db.recipe_categories.update({'_id': ObjectId(db_id)},
        {
            '$set':{
                'name' :  request.form.get('name'),
                'img_link' : image_URL
            }
        })

        # updates the old category name to the new one in the correspondent recipes
        mongo.db.recipes.update_many({'category' : previous_name},
        {
            '$set': {
                'category' : request.form.get('name')
            }
        })

        # redirects to the landing page
        return redirect(url_for('index'))
    
    else:
        # initializes page title and header
        page_title = 'Update recipe category'
        page_header = 'Update a recipe category:'
        
        # sends error list back to the form to correct mistakes
        return render_template('edit_form.html', recipe_category=mongo.db.recipe_categories.find_one({"_id": ObjectId(db_id)}), errors=error_list, form=form, page_title=page_title, page_header=page_header)


@app.route('/delete_recipe/<db_id>')
def delete_recipe(db_id):
    """ Removes a recipe from the database """

    # keeps recipe category link
    category = mongo.db.recipes.find_one({'_id': ObjectId(db_id)})['category']

    # removes recipe
    mongo.db.recipes.remove({'_id': ObjectId(db_id)})

    # updates counter in the category
    update_quantity_in_category(category)

    # redirects to the landing page
    return redirect(url_for('index'))


@app.route('/delete_recipe_category/<db_id>')
def delete_recipe_category(db_id):
    """ Removes a recipe category and all the recipes in the category from the database """

    # determines the category name by id
    category_name = mongo.db.recipe_categories.find_one({'_id': ObjectId(db_id)})['name']

    # removes all the recipes in the category
    mongo.db.recipes.remove({'category' : category_name})

    # removes the recipe category
    mongo.db.recipe_categories.remove({'_id': ObjectId(db_id)})

    # redirects to the landing page
    return redirect(url_for('index'))


@app.route('/add_review/<db_id>', methods=['POST'])
def add_review(db_id):
    """ Adds a review to a recipe or an appliance and refreshes the view page """
    
    if request.args['collection'] == 'recipe':
        # validates request form
        form = request.form
        error_list = validate_form(form, 'review')

        if error_list == []:
            # adds review to recipe
            mongo.db.recipes.update({'_id': ObjectId(db_id)},
            {
                '$push' : {
                    'reviews' : request.form.get('review')
                }
            })

            # redirects to the landing page
            return redirect(url_for('index'))
        
        else:
            # initializes page title
            page_title = 'View a recipe'

            # sends error list back to the form to correct mistakes
            return render_template('view.html', recipe=mongo.db.recipes.find_one({"_id": ObjectId(db_id)}), errors=error_list, form=form, page_title=page_title)
    
    elif request.args['collection'] == 'appliance':
        # validates request form
        form = request.form
        error_list = validate_form(form, 'review')
        
        if error_list == []:
            # adds review to the appliance
            mongo.db.appliances.update({'_id': ObjectId(db_id)},
            {
                '$push' : {
                    'reviews' : request.form.get('review')
                }
            })

            # redirects to the landing page
            return redirect(url_for('index'))
        
        else:
            # initializes page title
            page_title = 'View an appliance'

            # sends error list back to the form to correct mistakes
            return render_template('view.html', appliance=mongo.db.appliances.find_one({"_id": ObjectId(db_id)}), errors=error_list, form=form)
    
    else:
        # returns an error message on incorrect argument
        return render_template('error.html', msg='Bad argument error! (/add_review)')


@app.errorhandler(404)
def page_not_found(e):
    """ Page not found """

    return render_template('error.html', msg='Page not found error! (404)')


@app.errorhandler(400)
def handle_bad_request(e):
    """ Bad request error """

    return render_template('error.html', msg='Bad request error! (400)')


@app.errorhandler(500)
def server_error(e):
    """ Internal server error """

    return render_template('error.html', msg='Internal server error! (500)')


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', '5000')),
            debug=True)

import os
from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    if request.args['collection'] == 'recipes':
        if request.args['find'] == 'all':
            return render_template('search.html', recipes = mongo.db.recipes.find())
        else:
            return render_template('search.html', recipes = mongo.db.recipes.find({"category": request.args['find']}))
    elif request.args['collection'] == 'recipe_categories':
        return render_template('search.html', recipe_categories = mongo.db.recipe_categories.find())
    elif request.args['collection'] == 'appliances':
        if request.args['find'] == 'all':
            return render_template('search.html', appliances = mongo.db.appliances.find())
        else:
            return render_template('search.html', appliances = mongo.db.appliances.find({"type": request.args['find']}))
    elif request.args['collection'] == 'appliance_categories':
        return render_template('search.html', appliance_categories = mongo.db.appliance_categories.find())
    else:
        return 'Bad arguments!'


@app.route('/view/<db_id>', methods=['GET'])
def view(db_id):
    if request.args['collection'] == 'recipes':
        return render_template('view.html', recipe = mongo.db.recipes.find_one({"_id": ObjectId(db_id)}))
    elif request.args['collection'] == 'appliances':
        return render_template('view.html', appliance = mongo.db.appliances.find_one({"_id": ObjectId(db_id)}))
    else:
        return 'Bad arguments!'

@app.route('/add_form')
def add_form():
    return render_template('add_form.html')


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', '5000')),
            debug=True)

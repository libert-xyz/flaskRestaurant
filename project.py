from flask import Flask

app = Flask(__name__)

##Restaurants

@app.route('/')
@app.route('/restaurants')
def restaurants():
    return 'all restaurants'

@app.route('/restaurant/new')
def newRestaurant():
    return 'new restaurant'

@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant(restaurant_id):
    return 'edit Restaurant'


@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteRestaurant(restaurant_id):
    return 'delete Restaurant'


#MenuItems


@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>')
def menuRestaurant(restaurant_id):
    return "Restaurant menu"

@app.route('/restaurant/<int:restaurant_id>/menu/new')
def newMenuItem(restaurant_id):
    return 'New menu item'

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit')
def editMenuItem(restaurant_id,menu_id):
    return 'Edit menu item'

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete')
def deleteMenuItem(restaurant_id,menu_id):
    return 'Delete menu item'



if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.debug = True

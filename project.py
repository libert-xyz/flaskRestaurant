from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)


#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurantes = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}


##Restaurants

@app.route('/')
@app.route('/restaurants')
def restaurants():
    return render_template('restaurants.html',restaurants=restaurantes,restaurant_id=restaurant['id'])

@app.route('/restaurant/new',methods=['GET','POST'])
def newRestaurant():
    if request.method == 'POST':
        return redirect(url_for('restaurants'))
    else:
        return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit',methods=['GET','POST'])
def editRestaurant(restaurant_id):
    if request.method == 'POST':
        return redirect(url_for('restaurants'))
    else:
        return render_template('editRestaurant.html',restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/delete',methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    if request.method == 'POST':
        return redirect(url_for('restaurants'))
    else:
        return render_template('deleteRestaurant.html',restaurant=restaurant['name'],restaurant_id=restaurant_id)


#MenuItems


@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>')
def menuRestaurant(restaurant_id):
    return render_template('menu.html',items=items,restaurant_id=restaurant['id'])

@app.route('/restaurant/<int:restaurant_id>/menu/new',methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        return redirect(url_for('menuRestaurant',restaurant_id=restaurant_id))
    else:
        return render_template('newMenuItem.html',restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',methods=['GET','POST'])
def editMenuItem(restaurant_id,menu_id):
    if request.method == 'POST':
        return redirect(url_for('menuRestaurant',restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html',restaurant_id=restaurant_id,menu_id=menu_id)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',methods=['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    if request.method == 'POST':
        return redirect(url_for('menuRestaurant',restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html',restaurant_id=restaurant_id,menu_id=menu_id,menu=item['name'])


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.debug = True

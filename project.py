from flask import Flask, render_template, url_for, request, redirect
#Database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from database import Restaurant, MenutItem
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///restaurantmenu.db')
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


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
    restaurantes = session.query(Restaurant).all()
    return render_template('restaurants.html',restaurantes=restaurantes)

@app.route('/restaurant/new',methods=['GET','POST'])
def newRestaurant():
    if request.method == 'POST':
        if request.form['name'] != '':
            restaurant = Restaurant(name=request.form['name'])
            session.add(restaurant)
            session.commit()
            return redirect(url_for('restaurants'))
        else:
            return 'Error'
    else:
        return render_template('newRestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit',methods=['GET','POST'])
def editRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name'] != '':
            restaurant.name = request.form['name']
            session.add(restaurant)
            session.commit()
            return redirect(url_for('restaurants'))
        else:
            return 'Error'
    else:
        return render_template('editRestaurant.html',restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete',methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('restaurants'))
    else:
        return render_template('deleteRestaurant.html',restaurant=restaurant)


#MenuItems


@app.route('/restaurant/<int:restaurant_id>/menu')
@app.route('/restaurant/<int:restaurant_id>')
def menuRestaurant(restaurant_id):
    menu = session.query(MenutItem).filter_by(restaurant_id=restaurant_id).all()
    restaurantName = session.query(Restaurant).filter_by(id=restaurant_id).one()
    return render_template('menu.html',menu=menu,restaurant_id=restaurant_id,restaurant=restaurantName)

@app.route('/restaurant/<int:restaurant_id>/menu/new',methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newMenu = MenutItem(name=request.form['name'],description=request.form['description'],price=request.form['price'],restaurant_id=restaurant_id)
        session.add(newMenu)
        session.commit()
        return redirect(url_for('menuRestaurant',restaurant_id=restaurant_id))
    else:
        return render_template('newMenuItem.html',restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',methods=['GET','POST'])
def editMenuItem(restaurant_id,menu_id):
    menu = session.query(MenutItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name'] != '':
            menu.name = request.form['name']
            menu.description = request.form['description']
            menu.price = request.form['price']
            session.add(menu)
            session.commit()
            return redirect(url_for('menuRestaurant',restaurant_id=restaurant_id))

        else:
            return 'Error'
    else:
        return render_template('editMenuItem.html',restaurant_id=restaurant_id,menu=menu)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',methods=['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    deleteItem = session.query(MenutItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('menuRestaurant',restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html',restaurant_id=restaurant_id,menu_id=menu_id,menu=deleteItem)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    app.debug = True

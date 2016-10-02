from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database import Base, Restaurant, MenutItem, User


#Connect to Database and create database session
engine = create_engine('sqlite:///restaurantmenuwithUsers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#session imports
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
        open('client_secret.json','r').read())['web']['client_id']

@app.route('/login')
def showLogin():
    #state tokens , anti csfr
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))

    login_session['state'] = state
    #return "The current session state is: %s" %login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    #client sending to the server / server sending to the client
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        #authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json',scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the auth code'),401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #check that the access token is valid
    access_token = credentials.access_token
    print 'Access token: %s' %access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    #if error in access_token info, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
                json.dumps("Token user ID doesn't match"),401)
        response.headers['contentType'] = 'application/json'
        return response

    #verify that the access token is valid for the app


    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                json.dumps("Token client ID doesn't match"),401)
        print "Token client ID does not match app's"
        response.headers['contentType'] = 'application/json'
        return response


    #check to see if user is already logged in

    stored_credentials = login_session.get('credentials')
    print 'Login Credentials: %s' %stored_credentials
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Already logged in"),200)
        response.headers['Content-Type'] = 'application/json'
        return response


    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])

    userId = getUserId(login_session['email'])
    #userInfo = getUserInfo(userId)


    if userId != None:
        print 'Login sessions: %s' %login_session
        print "done!"
        login_session['user_id'] = userId
        return output
    else:
        createUser(login_session)
        login_session['user_id'] = userId
        print 'User %s created' %login_session['username']
        return output




@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']
    print 'In gdisconnect access token is %s' %access_token
    print 'User name is: '
    print login_session['username']

    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    print 'result is '
    print result

    if result['status'] == '200':
	del login_session['credentials']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

#JSON APIs to view Restaurant Information
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenutItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenutItem).filter_by(id = menu_id).one()
    return jsonify(Menu_Item = Menu_Item.serialize)

@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants= [r.serialize for r in restaurants])


#Show all restaurants
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
  restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
  if 'username' not in login_session:
      return render_template('publicrestaurants.html', restaurants = restaurants)
  else:
      return render_template('restaurants.html', restaurants = restaurants)

#Create a new restaurant
@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
  if 'username' not in login_session:
      return redirect('login')
  if request.method == 'POST':
      #newRestaurant = Restaurant(name = request.form['name'],user_id=login_session['user_id'])
      newRestaurant = Restaurant(name = request.form['name'],user_id=login_session['user_id'])

      session.add(newRestaurant)
      flash('New Restaurant %s Successfully Created' % newRestaurant.name)
      session.commit()
      return redirect(url_for('showRestaurants'))
  else:
      return render_template('newRestaurant.html')

#Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
  if 'username' not in login_session:
      return redirect('login')

  editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  if restaurant.user_id == login_session['user_id']:
      if request.method == 'POST':
          if request.form['name']:
            editedRestaurant.name = request.form['name']
            flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
            return redirect(url_for('showRestaurants'))
      else:
        return render_template('editRestaurant.html', restaurant = editedRestaurant)

  else:
      return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))


#Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
  if 'username' not in login_session:
      return redirect('login')

  restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
  if restaurantToDelete.user_id == login_session['user_id']:
      if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % restaurantToDelete.name)
        session.commit()
        return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
      else:
        return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)
  else:
      return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))


#Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenutItem).filter_by(restaurant_id = restaurant_id).all()
    creator = getUserInfo(restaurant.user_id)
    if 'username' in login_session and restaurant.user_id == login_session['user_id']:
        return render_template('menu.html', items = items, restaurant = restaurant, creator= creator)
    else:
        return render_template('publicmenu.html', items = items, restaurant = restaurant, creator= creator)

#Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
  if 'username' not in login_session:
      return redirect('login')

  restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
  if request.method == 'POST':
      newItem = MenutItem(name = request.form['name'],
                description = request.form['description'], price = request.form['price'],
                course = request.form['course'], restaurant_id = restaurant_id,
                user_id=restaurant.user_id)
      session.add(newItem)
      session.commit()
      flash('New Menu %s Item Successfully Created' % (newItem.name))
      return redirect(url_for('showMenu', restaurant_id = restaurant_id))
  else:
      return render_template('newmenuitem.html', restaurant_id = restaurant_id)

#Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('login')
    editedItem = session.query(MenutItem).filter_by(id = menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if restaurant.user_id == login_session['user_id']:
        if request.method == 'POST':
            if request.form['name']:
                editedItem.name = request.form['name']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['price']:
                editedItem.price = request.form['price']
            if request.form['course']:
                editedItem.course = request.form['course']
            session.add(editedItem)
            session.commit()
            flash('Menu Item Successfully Edited')
            return redirect(url_for('showMenu', restaurant_id = restaurant_id))
        else:
            return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)
    else:
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))


#Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    if 'username' not in login_session:
        return redirect('login')

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    itemToDelete = session.query(MenutItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item = itemToDelete)


#User Management

def createUser(login_session):
    newUser = User(name=login_session['username'],email=login_session['email'],picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

#Return user object
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/users')
def listUsers():
    users = session.query(User).all()
    return render_template('allusers.html',users=users)

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Phylum, Order, Family, Class, Genus, Species, Sighting
from flask import session as login_session
from flask import make_response
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests
from datetime import datetime

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "The Fungus Among Us"

engine = create_engine('sqlite:///fungusamongus.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

rank_to_model = {'phylum': Phylum, 'class': Class, 'order': Order,
                 'family': Family, 'genus': Genus, 'species': Species}

# Login and Logout routes
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['user_id']
        del login_session['provider']
        del login_session['state']
        flash("You have successfully been logged out.")
        return redirect(url_for('index'))
    else:
        flash("You were not logged in")
        return redirect(url_for('index'))
    return


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def create_user(login_session):
    new_user = User(user_name=login_session['username'], user_email=login_session[
                   'email'], user_picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(user_email=login_session['email']).one()
    return user.user_id


def get_user_info(user_id):
    user = session.query(User).filter_by(user_id=user_id).one()
    return user


def get_user_id(user_email):
    try:
        user = session.query(User).filter_by(user_email=user_email).one()
        return user.user_id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
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


# Application routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    if 'username' not in login_session:

        return render_template('index.html')

    user_id = login_session['user_id']
    user = get_user_info(user_id)
    sightings = session.query(Sighting).filter_by(created_by=user_id).all()

    return render_template('home.html', user=user, sightings=sightings)

@app.route('/sighting', defaults={'sighting_id': None}, strict_slashes=False, methods=['GET', 'POST'])
@app.route('/sighting/<int:sighting_id>/', methods=['GET', 'POST'])
def sightings(sighting_id):
    if not sighting_id:
        phylum_query = session.query(Sighting.phylum_id.distinct().label('phylum_id'))
        class_query = session.query(Sighting.class_id.distinct().label('class_id'))
        order_query = session.query(Sighting.order_id.distinct().label('order_id'))
        family_query = session.query(Sighting.family_id.distinct().label('family_id'))
        genus_query = session.query(Sighting.genus_id.distinct().label('genus_id'))
        species_query = session.query(Sighting.species_id.distinct().label('species_id'))

        phylum_seen = [row.phylum_id for row in phylum_query.all()]
        class_seen = [row.class_id for row in class_query.all()]
        order_seen = [row.order_id for row in order_query.all()]
        family_seen = [row.family_id for row in family_query.all()]
        genus_seen = [row.genus_id for row in genus_query.all()]
        species_seen = [row.species_id for row in species_query.all()]

        sightings = session.query(Sighting).all()


        return render_template(
            'sightings.html',
            phylum_seen=phylum_seen,
            class_seen=class_seen,
            order_seen=order_seen,
            family_seen=family_seen,
            genus_seen=genus_seen,
            species_seen=species_seen,
            sightings=sightings
            )
    else:
        if 'username' not in login_session:
            user_id = None
        else:
            user_id = login_session['user_id']

        sighting = session.query(Sighting).get(sighting_id)

        return render_template('sightings.html',
                               sighting_id=sighting_id,
                               sighting=sighting,
                               user_id=user_id)


@app.route('/sighting/add/', defaults={'species': None}, methods=['GET', 'POST'])
@app.route('/sighting/add/<species>/', methods=['GET', 'POST'])
def new_sighting(species):
    if 'username' not in login_session:
        return render_template('login.html')
    user_id = login_session['user_id']
    if species:
        all_species = session.query(Species).filter_by(species_name=species).one()
    else:
        all_species = session.query(Species).order_by(Species.species_name.asc()).all()

    if request.method == 'POST':
        # Set form results to variables
        species = request.form['species']
        location = request.form['location']
        comment = request.form['comment']
        image = request.form['image']

        species = session.query(Species).get(species)
        genus = species.parent[0]
        family = genus.parent[0]
        order = family.parent[0]
        clss = order.parent[0]
        phylum = clss.parent[0]

        new_sighting = Sighting()
        new_sighting.phylum_id = phylum.rank_id
        new_sighting.class_id = clss.rank_id
        new_sighting.order_id = order.rank_id
        new_sighting.family_id = family.rank_id
        new_sighting.genus_id = genus.rank_id
        new_sighting.species_id = species.rank_id
        new_sighting.sighting_location = location
        new_sighting.sighting_comment = comment
        new_sighting.sighting_image = image
        new_sighting.created_by = user_id
        new_sighting.modified_by = user_id

        session.add(new_sighting)
        session.commit()

        return redirect(url_for('sightings'))


    return render_template('new-sighting.html', all_species=all_species)


@app.route('/sighting/edit/<int:sighting_id>/', methods=['GET', 'POST'])
def edit_sighting(sighting_id):
    if 'username' not in login_session:
        return render_template('login.html')

    user_id = login_session['user_id']
    sighting = session.query(Sighting).get(sighting_id)
    all_species = session.query(Species).order_by(Species.species_name.asc()).all()

    if request.method == 'POST':
        # Set form results to variables
        species = request.form['species']
        location = request.form['location']
        comment = request.form['comment']
        image = request.form['image']

        species = session.query(Species).get(species)
        genus = species.parent[0]
        family = genus.parent[0]
        order = family.parent[0]
        clss = order.parent[0]
        phylum = clss.parent[0]

        sighting.phylum_id = phylum.rank_id
        sighting.class_id = clss.rank_id
        sighting.order_id = order.rank_id
        sighting.family_id = family.rank_id
        sighting.genus_id = genus.rank_id
        sighting.species_id = species.rank_id
        sighting.sighting_location = location
        sighting.sighting_comment = comment
        sighting.sighting_image = image
        sighting.modified_by = user_id
        sighting.datetime_modified = datetime.utcnow()

        session.commit()

        return redirect(url_for('sightings', sighting_id=sighting_id))

    return render_template('new-sighting.html',
                           sighting=sighting,
                           all_species=all_species)


@app.route('/sighting/delete/<int:sighting_id>/', methods=['GET', 'POST'])
def delete_sighting(sighting_id):
    sighting = session.query(Sighting).get(sighting_id)

    if request.method == 'POST':
        session.delete(sighting)
        session.commit()

        return redirect(url_for('home'))

    return render_template('delete-sighting.html', sighting=sighting)

@app.route('/rank/<rank>')
def rank(rank):
    if not rank:
        return render_template('index.html')
    else:
        if rank in rank_to_model.keys():
            model = rank_to_model[rank]
            rank_entries = session.query(model).all()

    name_field = '{}_name'.format(rank)
    rank_name = getattr(model, name_field)
    rank_content = rank_entries

    return render_template('rank.html', rank=rank, name_field=name_field,
                           rank_content=rank_content)

@app.route('/tax/<string:tax_type>/<int:tax_id>')
def tax(tax_type, tax_id):
    if not tax_type and not tax_id:
        return render_template('index.html')
    else:
        if tax_type in rank_to_model.keys() and isinstance(tax_id, int):
            model = rank_to_model[tax_type]
            tax = session.query(model).get(tax_id)

    return render_template('tax.html', tax_type=tax_type, tax=tax)

# API routes
@app.route('/api/v1/fungi', defaults={'rank': None})
@app.route('/api/v1/fungi/<string:rank>/')
def get_phylum(rank):
    if not rank:
        return jsonify(ranksAvailable=rank_to_model.keys())
    else:
        if rank in rank_to_model.keys():
            model = rank_to_model[rank]
            rank_entries = session.query(model).all()


            return jsonify([entry.serialize for entry in rank_entries])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
app.run(host='0.0.0.0', port=5000)

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)
from database_setup import (Base,
                            User,
                            Phylum,
                            Order,
                            Family,
                            Class,
                            Genus,
                            Species,
                            Sighting)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
from flask import make_response
from functools import wraps
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


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash('You are not allowed to access there')
            return redirect('/login')
    return decorated_function


# Login and Logout routes
@app.route('/login')
def login():
    '''
    Creates state variable using random characters and adds it to the
    User's login_session variable.

    Returns:
        Returns Login template page.
    '''
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


@app.route('/logout')
def logout():
    '''
    Logs user out by removing login_session informatition using gdisconnect()
    or fbdisconnect() functions based on user OAuth2 method used.

    If User not previously logged in, flash message information is relayed
    and user is redirected to Index page.

    If User was previously logged in, flash message information of successfull
    logout is relayed, user is logged out and redirected to Index page.

    Returns:
        Index template page.
    '''
    # Conditional check for provider key in session
    if 'provider' in login_session:
        # Find user session provider and use appropriate logout function
        if login_session['provider'] == 'google':
            gdisconnect()
        # Delete user session login information
        del login_session['user_id']
        del login_session['provider']
        del login_session['state']

        # Flash message of successfull logout
        flash("You have successfully been logged out.")

        return redirect(url_for('index'))
    else:
        # Flash message if user was not previously logged in
        flash("You were not logged in")

        return redirect(url_for('index'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''
    Performs proper OAuth2 authentication between google API and the
    application.

    Returns:
        401 response if user login_session state token cannot be validated.

        401 response if google API authorization code fails to upgrade to a
        credential fails.

        500 response if google object token given by google API is invalid.

        200 response and user already conected message if user already
        connected.

        Welcome message if proper Authorization exchange is performed between
        application server and google API.
    '''
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
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
    output += '''' " style = "width: 300px; height: 300px; border-radius: 150px
    ;-webkit-border-radius: 150px;-moz-border-radius: 150px;">
    '''
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")

    return output


# User Helper Functions
def create_user(login_session):
    '''
    Creates a new user in the database.

    Returns:
        user.user_id: generated distinct integer value identifying the newly
        created user.
    '''
    # Create transient object by passing login session variables to the User
    # object model
    new_user = User(
        user_name=login_session['username'],
        user_email=login_session['email'],
        user_picture=login_session['picture'])
    # Add new user model to database
    session.add(new_user)
    session.commit()

    # Query database using login session email and return matching user object
    user = (
        session.query(User)
        .filter_by(user_email=login_session['email'])
        .one()
    )

    # Return query user object's user_id attribute
    return user.user_id


def get_user_info(user_id):
    '''
    Query database and return user object matching user_id variable.

    Args:
        user_id: user account ID

    Returns:
        User object found in database with matching user_id argument.
    '''
    user = session.query(User).filter_by(user_id=user_id).one()

    # Return query result user object
    return user


def get_user_id(user_email):
    '''
    Query database and return user ID for user object with matching user_email
    argument.

    Args:
        user_email: user account email.

    Returns:
        User ID from queried user object if user object is found using
        user_email argument.

        None if no User object matches user_email argument.
    '''
    try:
        # Query database of User object with matching user_email attribute
        user = session.query(User).filter_by(user_email=user_email).one()

        # Return query result User object use ID
        return user.user_id
    except:
        # Return None
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    '''
    Performs proper OAuth2 disconnect between application and google API and
    removes user information from user login_session.

    Returns:
        401 response if user was not connected at time of function running.

        200 response and message indicating a successfull disconnect was
        performed.
    '''
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
        response = make_response(
            json.dumps('Failed to revoke token for given user.'),
            400)
        response.headers['Content-Type'] = 'application/json'

        return response


# Application routes
@app.route('/')
def index():
    '''
    Render Index page

    Returns:
        Index template page.
    '''

    # Return rendering of Index page.
    return render_template('index.html')


@app.route('/home')
@login_required
def home():
    '''
    Loads user Home page with user information and database sightings created
    created by the user.

    Returns:
        Home page template.
    '''
    user_id = login_session['user_id']
    user = get_user_info(user_id)
    sightings = session.query(Sighting).filter_by(created_by=user_id).all()

    return render_template('home.html', user=user, sightings=sightings)


@app.route('/sighting',
           defaults={'sighting_id': None},
           strict_slashes=False,
           methods=['GET', 'POST'])
@app.route('/sighting/<int:sighting_id>/', methods=['GET', 'POST'])
def sightings(sighting_id):
    '''
    Renders mushroom sighting page.

    Args:
        sighting_id: mushroom sighting ID

    Returns:
        Global statistics page containing information for all of the sightings
        entered into the database if no mushroom sighting ID is passed.

        Specific mushroom sighting page with mushroom sighting details if
        sighting ID is passed.
    '''
    if not sighting_id:
        # Query Sighting table for each distinct taxon
        phylum_query = (
            session.query(Sighting.phylum_id.distinct().label('phylum_id'))
        )
        class_query = (
            session.query(Sighting.class_id.distinct().label('class_id'))
        )
        order_query = (
            session.query(Sighting.order_id.distinct().label('order_id'))
        )
        family_query = (
            session.query(Sighting.family_id.distinct().label('family_id'))
        )
        genus_query = (
            session.query(Sighting.genus_id.distinct().label('genus_id'))
        )
        species_query = (
            session.query(Sighting.species_id.distinct().label('species_id'))
        )

        # Generate a list of IDs for each taxon
        phylum_seen = [row.phylum_id for row in phylum_query.all()]
        class_seen = [row.class_id for row in class_query.all()]
        order_seen = [row.order_id for row in order_query.all()]
        family_seen = [row.family_id for row in family_query.all()]
        genus_seen = [row.genus_id for row in genus_query.all()]
        species_seen = [row.species_id for row in species_query.all()]

        # Get all Sighting object models from the databse
        sightings = session.query(Sighting).all()

        # Return render of sighting template with global statistics
        return render_template('sightings.html',
                               phylum_seen=phylum_seen,
                               class_seen=class_seen,
                               order_seen=order_seen,
                               family_seen=family_seen,
                               genus_seen=genus_seen,
                               species_seen=species_seen,
                               sightings=sightings)
    else:
        if 'username' not in login_session:
            user_id = None
        else:
            user_id = login_session['user_id']

        # Retrieve mushroom sighting from databse using sighting_id argument
        sighting = session.query(Sighting).get(sighting_id)

        # Return render of sighting template for specific mushroom sighting
        return render_template('sightings.html',
                               sighting_id=sighting_id,
                               sighting=sighting,
                               user_id=user_id)


@app.route(
    '/sighting/add/', defaults={'species': None}, methods=['GET', 'POST']
)
@app.route(
    '/sighting/add/<species>/', methods=['GET', 'POST']
)
@login_required
def new_sighting(species):
    '''
    Renders mushroom new sighting page.

    Args:
        species: species can be passed to create sighting for specific species.
        Argument is optional.

    Returns:
        Mushroom sighting page containing form with prefilled dropdown
        selections.
    '''
    # Obtain user login_session user_id
    user_id = login_session['user_id']

    # If species argument is passed, the species is retrieved from database
    # else, all species are retrieved from database
    if species:
        all_species = (
            session.query(Species).filter_by(species_name=species).one()
        )
    else:
        all_species = (
            session.query(Species).order_by(Species.species_name.asc()).all()
        )

    if request.method == 'POST':
        # Set form results to variables
        species = request.form['species']
        location = request.form['location']
        comment = request.form['comment']
        image = request.form['image']

        # Retrieve species from database user form entry and use to retrieve
        # all required taxonomic information for the species
        species = session.query(Species).get(species)
        genus = species.parent[0]
        family = genus.parent[0]
        order = family.parent[0]
        clss = order.parent[0]
        phylum = clss.parent[0]

        # Create new Sighting model object
        new_sighting = Sighting()
        # Add required attributes to new sighting object
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

        # Add new sighting to database
        session.add(new_sighting)
        session.commit()

        # Redirect user to Sightings template after submittal
        return redirect(url_for('sightings'))

    return render_template('new-sighting.html', all_species=all_species)


@app.route('/sighting/edit/<int:sighting_id>/', methods=['GET', 'POST'])
@login_required
def edit_sighting(sighting_id):
    '''
    Allows user to edit existing mushroom sighting.

    Args:
        sighting_id: Sighting ID for exising Sighting entry.

    Return:
        New sighting template page with form prefilled containing existing
        sighting information.
    '''
    user_id = login_session['user_id']
    # Retrieve Sighting object from data batabase using sighting_id argument
    sighting = session.query(Sighting).get(sighting_id)
    # Retrieve all species
    all_species = (
        session.query(Species).order_by(Species.species_name.asc()).all()
    )

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

        # Add required attributes to sighting object being edited
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

        # Redirect user to sighting page after submittal
        return redirect(url_for('sightings', sighting_id=sighting_id))

    return render_template('new-sighting.html',
                           sighting=sighting,
                           all_species=all_species)


@app.route('/sighting/delete/<int:sighting_id>/', methods=['GET', 'POST'])
def delete_sighting(sighting_id):
    '''
    Deletes existing mushroom sighting from application database.

    Args:
        sighting_id: Existing mushroom Sighting object ID.

    Returns:
        Delete mushroom sighting page.
    '''
    sighting = session.query(Sighting).get(sighting_id)

    if request.method == 'POST':
        session.delete(sighting)
        session.commit()

        return redirect(url_for('home'))

    return render_template('delete-sighting.html', sighting=sighting)


@app.route('/rank/<rank>')
def rank(rank):
    '''
    Returns information for taxonomic ranks available in the database.

    Args:
        rank: taxanomic rank name.

    Returns:
        Rank template page.
    '''
    if not rank:
        return render_template('index.html')
    else:
        if rank in rank_to_model.keys():
            model = rank_to_model[rank]
            rank_entries = session.query(model).all()

    name_field = '{}_name'.format(rank)
    rank_content = rank_entries

    return render_template('rank.html', rank=rank, name_field=name_field,
                           rank_content=rank_content)


@app.route('/tax/<string:tax_type>/<int:tax_id>')
def tax(tax_type, tax_id):
    '''
    Returns information for a specifica taxon.

    Args:
        tax_type: Taxonomic type.
        tax_id: Taxonomic entry ID

    Returns:
        Tax template page for for taxon corresponding to passed arguments.
    '''
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
    '''
    API route for taxonomic rank information

    Args:
        rank: Taxonomic rank name.

    Returns:
        JSON object containing information for taxonic rank variable passed
        or all taxonomic ranks if not rank argument is given.
    '''
    if not rank:
        return jsonify(ranksAvailable=rank_to_model.keys())
    else:
        if rank in rank_to_model.keys():
            model = rank_to_model[rank]
            rank_entries = session.query(model).all()

            return jsonify([entry.serialize for entry in rank_entries])


@app.route('/api/v1/sighting', defaults={'sighting_id': None})
@app.route('/api/v1/sighting/<int:sighting_id>/')
def get_sighting(sighting_id):
    '''
    API route for mushroom sighting information

    Args:
        sighting_id: Mushroom sighting ID.

    Returns:
        JSON object containing information for mushroom sighting_id variable
        passed or all mushroom sightings if no sighting_id argument is given.
    '''
    if not sighting_id:
        all_sightings = session.query(Sighting).all()

        return jsonify([sighting.serialize for sighting in all_sightings])
    else:
        sighting = session.query(Sighting).get(sighting_id)

        return jsonify(sighting.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
app.run(host='0.0.0.0', port=5000)

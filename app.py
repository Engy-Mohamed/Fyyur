#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only 
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migarte = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show (db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id=db.Column(db.Integer,db.ForeignKey('artists.id'))
    venue_id=db.Column(db.Integer,db.ForeignKey('venues.id'))
    start_time =db.Column(db.DateTime,nullable =False)
    def __repr__(self):
        return f'<Show: artist id {self.artist_id} venue id{self.venue_id} {self.start_time}>'

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable =False)
    genres = db.Column(db.ARRAY(db.String()),nullable =False)
    city = db.Column(db.String(120),nullable =False)
    state = db.Column(db.String(120),nullable =False)
    address = db.Column(db.String(120),nullable =False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean,nullable =False,default=False)
    seeking_description =db.Column(db.String(500))
    shows = db.relationship(Show,backref='venues',lazy=True)
    def __repr__(self):
        return f'<Venue: {self.id} {self.name} >'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable =False)
    city = db.Column(db.String(120),nullable =False)
    state = db.Column(db.String(120),nullable =False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()),nullable =False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean,nullable =False,default=False)
    seeking_description=db.Column(db.String(500))
    shows = db.relationship(Show,backref='artists',lazy=True)
    def __repr__(self):
        return f'<Artist: {self.id} {self.name} >'

    
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    print(value)
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  venues = Venue.query.options(load_only('id','name')).order_by(Venue.id.desc()).limit(10)
  artists = Artist.query.options(load_only('id','name')).order_by(Artist.id.desc()).limit(10)
  return render_template('pages/home.html',venues=venues,artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.options(load_only('id','name','city','state')).all()
  data=[]
  
  for venue in venues:
      NewCiry=True
      num_upcoming_shows=len(Show.query.filter(Show.venue_id==venue.id and Show.start_time>datetime.now()).all())
      if len(data) > 0:
          for d in data:
              if d['city']==venue.city and  d['state']==venue.state:
                  d['venues'].append({"id":venue.id,"name":venue.name,"num_upcoming_shows":num_upcoming_shows})
                  NewCiry =False
      if NewCiry :
          data.append({"city":venue.city,"state":venue.state,
                       "venues":[{"id":venue.id,"name":venue.name,"num_upcoming_shows":num_upcoming_shows}]})  

  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_str = search_term=request.form.get('search_term', '')
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_str}%')).all()
    data =[]
    for venue in venues:
        num_upcoming_shows=len(Show.query.filter(Show.venue_id==venue.id and Show.start_time>datetime.now()).all())
        data.append({"id": venue.id,
        "name": venue.name,"num_upcoming_shows": num_upcoming_shows})
    response={"count": len(venues),"data": data}
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/searchForArtist/<search_term>', methods=['POST'])
def search_ForArtist(search_term):
    
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    data =[]
     
    for artist in artists:
        data.append({"id": artist.id,"name": artist.name})
   
    return jsonify({ 'artists': data })




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  print(venue.genres)
  result_upcoming_shows =  Show.query.with_entities(Show.start_time,Artist.id,Artist.name,Artist.image_link).join(Artist).filter(Show.venue_id==venue_id ).filter( Show.start_time > datetime.now()).all()
  result_past_shows =  Show.query.with_entities(Show.start_time,Artist.id,Artist.name,Artist.image_link).join(Artist).filter(Show.venue_id==venue_id ).filter( Show.start_time < datetime.now()).all()
  upcoming_shows=[]
  past_shows =[]
  print(result_upcoming_shows)
  print(result_past_shows )
  for show in result_upcoming_shows:
      upcoming_shows.append({'artist_id':show.id,'artist_name':show.name,'artist_image_link':show.image_link,'start_time':show.start_time} ) 
  for show in result_past_shows:
      past_shows.append({'artist_id':show.id,'artist_name':show.name,'artist_image_link':show.image_link,'start_time':show.start_time} ) 

  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website":venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past_shows ,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }


  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
   error = False
  
   try:
       name = request.form['name']
       city = request.form['city']
       state = request.form['state']
       address = request.form['address']
       phone = request.form['phone']
       genres = request.form.getlist('genres')
       image_link = request.form['image_link']
       facebook_link = request.form['facebook_link']
       website = request.form['website']
       seeking_talent = True if 'seeking_talent' in request.form else False 
       seeking_description = request.form['seeking_description']

       venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
       db.session.add(venue)
       db.session.commit()
   except:
       error = True
       db.session.rollback()
       print(sys.exc_info())
   finally: 
       db.session.close()
   if error:
       flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
   if not error:
       # on successful db insert, flash success
       flash('Venue ' + request.form['name'] + ' was successfully listed!')
   return redirect(url_for('index'))


  
 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases qwhere the session commit could fail.
    error=False
    try:
        Show.query.filter_by(venue_id=venue_id).delete()
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally: 
       db.session.close()
    if error:
       flash('An error occurred. the Venue could not be Deleted.')
    if not error:
       # on successful db insert, flash success
       flash('Venue was successfully Deleted!')
    return jsonify({ 'success': True })

 
   # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
   # clicking that button delete it from the db then redirect the user to the homepage
   # implement the redirect in the show_venue
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.options(load_only('id','name')).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_str = search_term=request.form.get('search_term', '')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_str}%')).all()
    data =[]
    for artist in artists:
        num_upcoming_shows=len(Show.query.filter(Show.artist_id==artist.id and Show.start_time>datetime.now()).all())
        data.append({"id": artist.id,
        "name": artist.name,"num_upcoming_shows": num_upcoming_shows})
    response={"count": len(artists),"data": data}
 
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    print(artist.genres)
    result_upcoming_shows =  Show.query.with_entities(Show.start_time,Venue.id,Venue.name,Venue.image_link).join(Venue).filter(Show.artist_id==artist_id ).filter( Show.start_time > datetime.now()).all()
    result_past_shows =  Show.query.with_entities(Show.start_time,Venue.id,Venue.name,Venue.image_link).join(Venue).filter(Show.artist_id==artist_id ).filter( Show.start_time < datetime.now()).all()
    upcoming_shows=[]
    past_shows =[]
    for show in result_upcoming_shows:
        upcoming_shows.append({'venue_id':show.id,'venue_name':show.name,'venue_image_link':show.image_link,'start_time':show.start_time} ) 
    for show in result_past_shows:
        past_shows.append({'venue_id':show.id,'venue_name':show.name,'venue_image_link':show.image_link,'start_time':show.start_time} )
    data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website":artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":past_shows ,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
   
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    try:
        artist = Artist.query.get(artist_id)
        artist.name = request.form['name']    
        artist.city = request.form['city'] 
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.image_link = request.form['image_link']
        artist.facebook_link = request.form['facebook_link']
        artist.website = request.form['website']
        artist.seeking_venue = True if 'seeking_venue' in request.form else False 
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally: 
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name']+ ' could not be Updated.')
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully Updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue=Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
  
    try:
        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.image_link = request.form['image_link']
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        venue.seeking_talent = True if 'seeking_talent' in request.form else False 
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + request.form['name']+ ' could not be Updated.')
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        name = request.form['name']    
        city = request.form['city'] 
        state = request.form['state']
        phone = request.form['phone']
        genres = request.form.getlist('genres')
        print(genres)
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        website = request.form['website']
        seeking_venue = True if 'seeking_venue' in request.form else False 
        seeking_description = request.form['seeking_description']
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally: 
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('index'))

 


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = Show.query.with_entities(Venue.id.label('venue_id'),Venue.name.label('venue_name'),Artist.id.label('artist_id'),Artist.name.label('artist_name'),Artist.image_link.label('artist_image_link'),Show.start_time).join(Venue).join(Artist).all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
   # on successful db insert, flash success
    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
     
    return render_template('pages/home.html')




@app.route('/shows/createShow', methods=['POST'])
def create_show_ForVenue():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    
    # on successful db insert, flash success
    error = False
    try:
        artist_id = request.get_json()['artist_id']
        
        venue_id = request.get_json()['venue_id']
        
        start_time = request.get_json()['start_time']
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        print(artist_id+" "+venue_id+" "+start_time)
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

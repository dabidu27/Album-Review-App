
from user_manager import UserManager
from review_manager import ReviewManager
from flask import Flask, jsonify, request, session
import os
from spotify import get_spotify_token, search_for_artist_albums, search_for_album
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY')
review_manager = ReviewManager()
user_manager = UserManager()

with sqlite3.connect('musicboxd.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS albums (
            album_id TEXT PRIMARY KEY NOT NULL,
            album_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            artist_id TEXT NOT NULL,
            release_date TEXT NOT NULL,
            cover TEXT NOT NULL
        )
    ''')
    conn.commit()

@app.route('/')
def home():
    return 'musicboxd_backend is up and running'

#USER FUNCTIONS

@app.route('/register', methods = ['POST'])
def register():

    data = request.json
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
            return jsonify({"error": "Username and password required"}), 400    

    success, message = user_manager.register_user(username, password)

    status_code = 200 if success else 400

    return jsonify({'message': message}), status_code

@app.route('/login', methods = ['POST'])
def login():

    data = request.json

    username = data.get('username')
    password = data.get('password')

    if not username or not password:

        return jsonify({'error': 'Username and password required'}), 400
    
    success, message, user_id = user_manager.login_user(username, password)

    status_code = 200 if success else 400

    if success:
        session['user_id'] = user_id

    return jsonify({'message': message, 'user_id': user_id}), status_code

@app.route('/logout', methods = ['POST'])

def logout():
    
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/change_password', methods = ['POST'])
def change_password():

    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')

    if not username or not new_password:
        return jsonify({'error': 'Username and  new password required'}), 400
    
    success, message, user_id = user_manager.change_user_password(username, new_password)

    status_code = 200 if success else 400

    if success:
        session['user_id'] = user_id

    return jsonify({'message': message}), status_code

#REVIEWS FUNCTIONS

@app.route('/search/artist/<artist_name>', methods = ['GET'])
def search_artists_albums(artist_name):
    with sqlite3.connect('musicboxd.db') as conn:

        cursor = conn.cursor()
        token = get_spotify_token()
        albums_list = []
        albums = search_for_artist_albums(token, artist_name)
        for album in albums:
                album_data = {'album_id':album['id'], 'album_name': album['name'], 'artist_name': album['artists'][0]['name'], 'artist_id': album['artists'][0]['id'], 'release_date': album['release_date'], 'cover': album['images'][0]['url']}
                cursor.execute('INSERT OR IGNORE INTO albums VALUES(?, ?, ?, ?, ?, ?)', (album_data['album_id'], album_data['album_name'], album_data['artist_name'], album_data['artist_id'], album_data['release_date'], album_data['cover'])) 
                albums_list.append(album_data)
        conn.commit()
    return jsonify(albums_list)

@app.route('/search/album/<album_name>', methods = ['GET'])

def search_album(album_name):

    with sqlite3.connect('musicboxd.db') as conn:

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM albums WHERE album_name = ?', (album_name, ))
        albums = cursor.fetchall()
        
        if not albums:

            token = get_spotify_token()
            album = search_for_album(token, album_name) #returns a dictionary

            album_id = album['id']
            album_name = album['name']
            artist_name = album['artists'][0]['name']
            artist_id = album['artists'][0]['id']
            release_date = album['release_date']
            cover = album['images'][0]['url']
            cursor.execute('''
                           INSERT OR IGNORE INTO albums (album_id, album_name, artist_name, artist_id, release_date, cover) VALUES (?, ?, ?, ?, ?, ?)
                           ''',(album_id, album_name, artist_name, artist_id, release_date, cover))
            conn.commit()
        
        cursor.execute('SELECT * FROM albums WHERE album_name = ?', (album_name, ))
        albums = cursor.fetchall()
        
        result = [
            {
                'album_id': row[0],
                'album_name': row[1],
                'artist_name': row[2],
                'artist_id': row[3],
                'release_date': row[4],
                'cover': row[5]
            }
            for row in albums
        ]

    return jsonify(result)

@app.route('/album/<album_id>/rating', methods = ['POST'])
def rate_album(album_id):

    data = request.json

    rating = data.get('rating')
    review = data.get('review', '')
    user_id = session.get('user_id')

    if rating is None or user_id is None:
        return jsonify({'error': 'Rating and user_id are required'}), 400
    
    success, message = review_manager.add_review(user_id, album_id, rating, review)

    status_code = 200 if success else 400

    return jsonify({'message': message}), status_code

@app.route('/album/<album_id>/delete_rating', methods = ['DELETE'])
def delete_rate(album_id):

    user_id = session.get('user_id')

    success, message = review_manager.delete_review(user_id, album_id)

    status_code = 200 if success else 400

    return jsonify({'message': message}), status_code

#FAVORITES FUNCTION

@app.route('/album/<album_id>/add_favorite', methods = ['POST'])
def add_to_favorites(album_id):

    data = request.json
    user_id = data.get('user_id')

    if not user_id:

        return jsonify({'error': 'User is not logged in'})
    
    success, message = user_manager.add_favourite(user_id, album_id)
    status_code = 200 if success else 400

    return jsonify({'message': message}), status_code

@app.route('/user/get_favorites', methods = ['GET'])
def get_user_favorites():

    user_id = session.get('user_id')

    if not user_id:

        return jsonify({'error': 'User is not logged in'})
    
    favorites = user_manager.get_favorites(user_id)

    favorites_list = [row[0] for row in favorites]

    return jsonify({'favorites': favorites_list}), 200

#FOLLOWERS FUNCTIONS
@app.route('/user/<followed_username>/follow', methods = ['POST'])
def follow(followed_username):

    follower_id = session.get('user_id')

    if not follower_id:
        return jsonify({'error': 'User has to be logged in'}), 401
    
    with sqlite3.connect('musicboxd.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (followed_username, ))
        followed_id = cursor.fetchone()[0]
    
    success, message = user_manager.follow_user(follower_id, followed_id)

    status = 200 if success else 400

    return jsonify({'message': message}), status

@app.route('/user/<followed_id>/unfollow', methods = ['POST'])
def unfollow(followed_id):

    follower_id = session.get('user_id')

    if not follower_id:
        
        return jsonify({'error': 'User has to be logged in'}), 401
    
    success, message = user_manager.unfollow_user(follower_id, followed_id)

    status = 200 if success else 400

    return jsonify({'message': message}), status

@app.route('/user/<user_id>/get_followers', methods = ['GET'])
def follower(user_id):
    followers = user_manager.get_followers(user_id)
    return jsonify(followers)

@app.route('/user/<user_id>/get_following', methods = ['GET'])
def following(user_id):
    following = user_manager.get_following(user_id)
    return jsonify(following)


#USER PROFILE
@app.route('/user/<username>/profile', methods = ['GET'])
def get_profile(username):
    with user_manager.connect() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT id, username, bio, picture FROM users WHERE LOWER(username) = ?', (username.lower(), ))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = {'id': user[0], 'username': user[1], 'bio': user[2], 'picture': user[3]}

        cursor.execute('''
            SELECT a.album_name, a.artist_name, a.release_date, a.cover
            FROM favorites f
            JOIN albums a ON f.album_id = a.album_id
            WHERE f.user_id = ?
        ''', (user_data['id'], ))
        favorites = cursor.fetchall()
        user_data['favorites'] = [
            {'album_name': fav[0], 'artist_name': fav[1], 'release_date':fav[2], 'cover': fav[3]}
            for fav in favorites
        ]

        cursor.execute('SELECT COUNT(*) FROM followers WHERE followed_id = ?', (user_data['id'], ))
        user_data['followers_count'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM followers WHERE follower_id = ?', (user_data['id'], ))
        user_data['following_count'] = cursor.fetchone()[0]

        reviews = review_manager.get_user_reviews(user[0])
        user_data['reviews'] = reviews

        return jsonify(user_data)

@app.route('/user/profile', methods = ['GET'])
def get_own_profile():

    user_id = session.get('user_id')

    with user_manager.connect() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT id, username, bio, picture FROM users WHERE id = ?', (user_id, ))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_data = {'id': user[0], 'username': user[1], 'bio': user[2], 'picture': user[3]}

        cursor.execute('''
            SELECT a.album_name, a.artist_name, a.release_date, a.cover
            FROM favorites f
            JOIN albums a ON f.album_id = a.album_id
            WHERE f.user_id = ?
        ''', (user_data['id'], ))
        favorites = cursor.fetchall()
        user_data['favorites'] = [
            {'album_name': fav[0], 'artist_name': fav[1], 'release_date':fav[2], 'cover': fav[3]}
            for fav in favorites
        ]

        cursor.execute('SELECT COUNT(*) FROM followers WHERE followed_id = ?', (user_data['id'], ))
        user_data['followers_count'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM followers WHERE follower_id = ?', (user_data['id'], ))
        user_data['following_count'] = cursor.fetchone()[0]

        reviews = review_manager.get_user_reviews(user[0])
        user_data['reviews'] = reviews

        return jsonify(user_data)

@app.route('/user/friends_activity')
def friends_activity():

    user_id = session.get('user_id')
    recent_activity = review_manager.friends_recent_activity(user_id)

    recent_activity_list = []

    for activity in recent_activity:
        recent_activity_list.append({'album_name': activity[0], 'artist_name': activity[1], 'cover': activity[2], 'rating': activity[3], 'review': activity[4]})

    return jsonify({'recent_activity': recent_activity_list})

@app.route('/user/update_bio', methods = ['POST'])
def update_bio():

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401
    
    data = request.json
    bio = data.get('bio', '')

    with user_manager.connect() as conn:

        cursor = conn.cursor()
        cursor.execute('UPDATE users SET bio = ? WHERE id = ?', (bio, user_id))
        conn.commit()
    
    return jsonify({'message': 'Bio successfully updated'}), 200

@app.route('/user/update_picture', methods = ['POST'])
def update_picture():

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401
    
    data = request.json
    picture = data.get('picture', '')

    with user_manager.connect() as conn:

        cursor = conn.cursor()
        cursor.execute('UPDATE users SET picture = ? WHERE id = ?', (picture, user_id))
        conn.commit()

    return jsonify({'message': 'Profile picture successfully updated'}), 200

#RECOMANDATION ENGINE

@app.route('/user/get_recommendations', methods = ['GET'])
def get_recommendations():

    full_recommendations_list = []
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401
  
    with user_manager.connect() as  conn:

            cursor = conn.cursor()
            cursor.execute('SELECT album_id FROM recomandations WHERE user_id = ? ORDER BY RANDOM() LIMIT 10', (user_id, ))
            recommendations = cursor.fetchall()
            recommendations_list = [album[0] for album in recommendations]
            for album_id in recommendations_list:

                cursor.execute('SELECT album_name, artist_name, release_date, cover FROM albums WHERE album_id = ?', (album_id,))
                row = cursor.fetchone()
                album_data = {'album_name': row[0], 'artist_name': row[1], 'release_date': row[2], 'cover': row[3]}
                full_recommendations_list.append(album_data)

    return jsonify({'recommendations': full_recommendations_list})


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)


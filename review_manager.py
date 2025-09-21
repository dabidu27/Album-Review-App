import sqlite3

class ReviewManager:

    def __init__(self, db_path = 'musicboxd.db'):

        self.db_path = db_path
        self.ensure_table()

    def connect(self):

        return sqlite3.connect(self.db_path, check_same_thread = False)

    def ensure_table(self):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                album_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 0 AND rating <= 5),
                review TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

            conn.commit()
    
    def add_review(self, user_id, album_id, rating, review):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute('SELECT * FROM reviews WHERE user_id = ? AND album_id = ?', (int(user_id), album_id))
            row = cursor.fetchone()

            if row:
                    cursor.execute('UPDATE reviews SET rating = ?, review = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND album_id = ?', (rating, review, user_id, album_id))

            else:
                cursor.execute('INSERT INTO reviews (user_id, album_id, rating, review) VALUES (?, ?, ?, ?)', (user_id, album_id, rating, review))

            conn.commit()
        
        return True, 'Review added successfully'
    
    def delete_review(self, user_id, album_id):

        with self.connect() as conn:

            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM reviews WHERE user_id = ? AND album_id = ?', (user_id, album_id))
            
            conn.commit()
        
        return True, 'Review deleted'
    
    def get_reviews_for_album(self, album_id):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute('SELECT r.rating, r.review FROM reviews WHERE album_id = ?', (album_id, ))
            return cursor.fetchall()
    
    def get_user_reviews(self, user_id):

        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute('SELECT a.album_name, a.artist_name, a.cover, r.rating, r.review FROM reviews r JOIN albums a ON r.album_id = a.album_id WHERE user_id = ?', (user_id,))
            return cursor.fetchall()
        
    def friends_recent_activity(self, user_id):

        recent_activity = []
        with self.connect() as conn:

            cursor = conn.cursor()

            cursor.execute('SELECT follower_id FROM followers WHERE follwed_id = ?', (user_id, ))
            friends = cursor.fetchall()
            friends = [id[0] for id in friends]

            for friend_id in friends:

                cursor.execute(
                    '''
                    SELECT a.album_name, a.artist_name, a.cover, r.rating, r.review FROM reviews r JOIN albums a ON r.album_id = a.album_id WHERE user_id = ? AND (created_at >= datetime('now', '-7 days') OR updated_at >= datetime('now', '-7 days'))
                    ORDER BY COALESCE(updated_at, created_at) DESC
                    ''', (friend_id, ))
                recent_activity.append(cursor.fetchall())
        
        return recent_activity

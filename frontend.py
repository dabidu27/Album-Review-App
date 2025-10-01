import streamlit as st
import requests

backend_url = 'http://localhost:5000'

st.set_page_config(page_title = 'Album Review')

def login():

    st.title('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type = 'password')
    login_button = st.button('Login')
    register_button = st.button('Register')

    if login_button:

        if not username or not password:
            st.warning('Please enter both username and password')
            return
        
        response = requests.post(f'{backend_url}/login', json = {'username': username, 'password': password})
        user_id = response.json()['user_id']
        if response.status_code == 200:

            st.success('Login successfull!')
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['user_id'] = user_id
            st.rerun()
        else:
            st.error(response.json().get('message'))
    
    if register_button:

        st.session_state['show_register'] = True
        st.rerun()
    
def register():
    
    st.title('Register')

    username = st.text_input('Choose a username: ')
    password = st.text_input('Choose a password: ', type = 'password')

    register_button = st.button('Create Account')
    back_button = st.button('Back to Login')

    if register_button:

        if not username or not password:
            st.warning('Please enter both username and password')
            return
        
        response = requests.post(f'{backend_url}/register', json = {'username': username, 'password': password})

        if response.status_code == 200:

            st.success('Registration successful! Please log in.')
            st.session_state['show_register'] = False
        else:
            st.error(response.json().get('message'))
    
    if back_button:

        st.session_state['show_register'] = False
        st.rerun()


def search_album_page():
    st.title('Search for an Album')
    search_mode = st.radio('Search by', ['Album', 'Artist'])

    if 'last_search_mode' not in st.session_state:
        st.session_state['last_search_mode'] = search_mode
    if st.session_state['last_search_mode'] != search_mode:
        st.session_state['album_search_results'] = []
        st.session_state['album_search_performed'] = False
        st.session_state['last_search_mode'] = search_mode

    #SEARCH BY ALBUM MODE

    if search_mode == 'Album':
        album_name = st.text_input('Enter album name')
        search_album_button = st.button('Search', key = 'album_search_btn')

        if 'album_search_performed' not in st.session_state:
            st.session_state['album_search_performed'] = False

        if search_album_button and album_name:
            
            st.session_state['album_search_performed'] = True

            response = requests.get(f'{backend_url}/search/album/{album_name}')
            if response.status_code == 200 and response.json():
                
                st.session_state['album_search_results'] = response.json()
            else:
                st.session_state['album_search_results'] = []

        albums = st.session_state['album_search_results']
        if albums:
            cols = st.columns(5)
            for idx, album in enumerate(albums):
                with cols[idx % 5]:

                    #DISPLAY ALBUM INFO

                    st.image(album['cover'], width=200)
                    st.write(f"**{album['album_name']}** by {album['artist_name']}")
                    st.write(f'Release date: {album['release_date']}')

                    #ADD TO FAVORITES

                    fav_key = f"fav_album_{album['album_id']}_{idx}"
                    if st.button('Add to favorites', key=fav_key):

                        user_id = st.session_state['user_id']
                        if not user_id:
                            st.warning('You must be logged in to add album to favorites')
                        else:
                            fav_response = requests.post(f"{backend_url}/album/{album['album_id']}/add_favorite", json = {'user_id': user_id})

                            if fav_response.status_code == 200:
                                st.success('Added to favorites')
                            else:
                                 st.error(fav_response.json().get('message'))

                    #ADD REVIEW

                    with st.form(key = f"review_form_{album['album_id']}_{idx}"):
                        
                        st.markdown('**Leave a rating**')
                        rating = st.slider('Rating', 0, 5, 3, key=f"review_{album['album_id']}_{idx}")
                        review = st.text_area('Add review', key = f"'review_{album['album_id']}_{idx}")
                        submit_review = st.form_submit_button('Submit review')

                        if submit_review:
                            user_id = st.session_state.get('user_id')
                            if not user_id:
                                st.warning('You have to be logged in to review albums')
                            else:
                                review_response = requests.post(f"{backend_url}/album/{album['album_id']}/rating", json = {'rating': rating, 'review': review, 'user_id': user_id})

                                if review_response.status_code == 200:
                                    st.success('Review submitted')
                                else:
                                    st.error(review_response.json().get('message'))

        elif st.session_state.get('album_search_performed'):
            st.warning('No albums found')

    #SEARCH BY ARTIST MODE

    else:

        artist_name = st.text_input('Enter artist name')
        search_album_button = st.button('Search', key = 'album_search_btn')

        if 'album_search_performed' not in st.session_state:
            st.session_state['album_search_performed'] = False

        if search_album_button and artist_name:

            st.session_state['album_search_performed'] = True
            
            response = requests.get(f'{backend_url}/search/artist/{artist_name}')
            if response.status_code == 200 and response.json():
                
                st.session_state['album_search_results'] = response.json()
            else:
                st.session_state['album_search_results'] = []
                
        albums = st.session_state['album_search_results']
        if albums:
                cols = st.columns(5)
                for idx, album in enumerate(albums):
                    
                    with cols[idx % 5]:

                        #DISPLAY ALBUM INFO

                        st.image(album['cover'], width=200)
                        st.write(f"**{album['album_name']}** by {album['artist_name']}")
                        st.write(f"Release date: {album['release_date']}")

                        #ADD TO FAVORITES

                        fav_key = f"fav_album_{album['album_id']}_{idx}"
                        if st.button('Add to favorites', key=fav_key):

                            user_id = st.session_state['user_id']
                            if not user_id:
                                st.warning('You must be logged in to add album to favorites')
                            else:
                                fav_response = requests.post(f"{backend_url}/album/{album['album_id']}/add_favorite", json = {'user_id': user_id})

                                if fav_response.status_code == 200:
                                    st.success('Added to favorites')
                                else:
                                    st.error(fav_response.json().get('message'))
                        
                        #ADD REVIEW

                        with st.form(key = f"review_form_{album['album_id']}_{idx}"):

                            st.markdown('**Leave a review**')
                            rating = st.slider('Rating', 0, 5, 3, key=f"review_{album['album_id']}_{idx}")
                            review = st.text_area('Add review', key = f"'review_{album['album_id']}_{idx}")
                            submit_review = st.form_submit_button('Submit review')

                            if submit_review:

                                user_id = st.session_state.get('user_id')

                                if not user_id:
                                    st.warning('You have to be logged in to review albums')
                                else:
                                    review_response = requests.post(f"{backend_url}/album/{album['album_id']}/rating", json = {'rating': rating, 'review': review, 'user_id': user_id})

                                    if review_response.status_code == 200:
                                        st.success('Review submitted')
                                    else:
                                        st.error(review_response.json().get('message'))
        elif st.session_state.get('album_search_performed'):
            st.warning('No albums found')

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 0

if 'album_search_results' not in st.session_state:
    st.session_state['album_search_results'] = []


if not st.session_state['logged_in']:

    if st.session_state['show_register']:
        register()
    else:
        login()

    st.stop()
else:
    search_album_page()
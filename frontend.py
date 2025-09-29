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

        if response.status_code == 200:

            st.success('Login successfull!')
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
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
    album_name = st.text_input('Enter album name')
    if st.button('Search'):

        if not album_name:
            st.warning('Please enter album name')
            return
        
        response = requests.get(f'{backend_url}/search/album/{album_name}')
        if response.status_code == 200 and response.json():

            albums = response.json()
            for album in albums:

                st.image(album['cover'], width=200)
                st.write(f"**{album['album_name']}** by {album['artist_name']}")
                st.write(f'Release date: {album['release_date']}')
        else:
            st.warning('No album found')

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'show_register' not in st.session_state:
    st.session_state['show_register'] = False

if not st.session_state['logged_in']:

    if st.session_state['show_register']:
        register()
    else:
        login()

    st.stop()
else:
    search_album_page()
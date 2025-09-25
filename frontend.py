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
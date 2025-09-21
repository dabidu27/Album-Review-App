import requests
import json
import sqlite3

s = requests.Session()

response = s.get('http://localhost:5000/')
print(response.text)

"""
#TEST REGISTER

data = {'username': 'david', 'password': 'davidstefan27'}

response = s.post('http://localhost:5000/register', json = data)

print(f'Status code: {response.status_code}')
print("Response (Rating):", response.text)
"""

#TEST LOGIN

data = {'username': 'david', 'password': 'davidstefan27'}

response = s.post('http://localhost:5000/login', json = data)

print(f'Status code: {response.status_code}')
print("Response (Rating):", response.text)

"""
#TEST SEARCH ALBUMS BY ARTIST

response = s.get('http://localhost:5000/search/artist/MasinaGalbena')

albums = response.json()

for album in albums:
    print(album)

"""

#TEST SEARCH ALBUM AND ADD REVIEW

#test search by name. get the album details in json form
response = s.get('http://localhost:5000/search/album/Deira')

#use .json() to load album details into a python dict

album = response.json()
#get the album_id
album_id = album[0]['album_id']

#params for the post request
data = {'rating': 5, 'review': 'cool'}

#test add review. use the previously obtained album_id
response = s.post(f'http://localhost:5000/album/{album_id}/rating', json = data)

print("Status Code (Rating):", response.status_code)
print("Response (Rating):", response.text)

"""
#TEST DELETE REVIEW

#test search by name. get the album details in json form
response = s.get('http://localhost:5000/search/album/Deira')

#use .json() to load album details into a python dict
album = response.json()

#get the album_id
album_id = album['id']

#test delete

response = s.delete(f'http://localhost:5000/album/{album_id}/delete_rating')

print('Status code:', response.status_code)
print('Response:', response.text)
""" 

#TEST ADD TO FAVORITES
"""
#test search by name. get the album details in json form
response = s.get('http://localhost:5000/search/album/LoveLetters')

#use .json() to load album details into a python dict
album = response.json()

#get the album_id
album_id = album['id']

response = s.post(f'http://localhost:5000/album/{album_id}/add_favorite')

print('Status code:', response.status_code)
print('Response:', response.text)
"""
#TEST GET FAVORITES
"""
response = s.get('http://localhost:5000/user/get_favorites')
favorites = response.json() #turns the response into a dictionary that looks like this : {'favorites': [album_id1, album_id2, ...]}
favorites = favorites.get('favorites', 'No favorites added') #gets the album_ids list
print(favorites)
"""

"""
#TEST SEARCH ARTIST ALBUMS

response = s.get('http://localhost:5000/search/artist/CharliXCX')
albums = response.json()
albums = albums['albums']
print(albums)
"""
#TEST RECOMMENDATION ENGINE

"""
response = s.get('http://localhost:5000/create_recommendations')
print('Status code:', response.status_code)
print('Response:', response.text)
response = s.get('http://localhost:5000/user/get_recommendations')
recommendations = response.json()
print(recommendations)
"""

#TEST GET OWN PROFILE

response = s.get('http://localhost:5000/user/profile')
profile = response.json()
print(profile)

#TEST SEARCH ALBUM AND ADD REVIEW

#test search by name. get the album details in json form
response = s.get('http://localhost:5000/search/album/BRAT')

#use .json() to load album details into a python dict

album = response.json()
#get the album_id
album_id = album[0]['album_id']

#params for the post request
data = {'rating': 5, 'review': 'brat af'}

#test add review. use the previously obtained album_id
response = s.post(f'http://localhost:5000/album/{album_id}/rating', json = data)

print("Status Code (Rating):", response.status_code)
print("Response (Rating):", response.text)

#TEST GET OWN PROFILE

response = s.get('http://localhost:5000/user/profile')
profile = response.json()
print(profile)
import requests

url = "https://www.facebook.com/benteulla.lynge/friends"

response = requests.get(url)

print(response.text)

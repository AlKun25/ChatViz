import requests

# Change the URL to match your server's address
url = 'http://localhost:8000/endpoint'

# Example input string
input_string = 'Hello, Flask!'

# Send GET request with the input string
response = requests.get(url, params={'input': input_string})

# Print the response
print(response.json())

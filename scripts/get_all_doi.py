import requests

# Define the author's name
author_name = "Christian Parisod"

# Search for the author's publications on CrossRef
url = f"https://api.crossref.org/works?query={author_name}&rows=100"

response = requests.get(url)
data = response.json()

# Extract DOIs from the returned data
dois = [item['DOI'] for item in data['message']['items']]

# Print all DOIs
for doi in dois:
    print(doi)
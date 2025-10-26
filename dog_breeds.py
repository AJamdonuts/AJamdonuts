
import requests

API_KEY = "live_ZsXsTeqiqp2q3pnpbZ62irPQL6CyVohL5xaD9aJVL9zTVesTppc0eXPvpmB0qcSY"
headers = {"x-api-key": API_KEY}

# Get all breeds
breeds = requests.get("https://api.thedogapi.com/v1/breeds", headers=headers).json()

breed_popularity = []

for breed in breeds:
    breed_id = breed['id']        # Define breed_id here inside the loop
    name = breed['name']
    
    # Fetch images for this breed
    try:
        response = requests.get(
            f"https://api.thedogapi.com/v1/images/search?breed_id={breed_id}&limit=100",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        images = response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Failed for {name}: {e}")
        images = []

    breed_popularity.append((name, len(images)))

# Sort by number of images
breed_popularity.sort(key=lambda x: x[1], reverse=True)

# Optional: print top 10
for name, count in breed_popularity[:10]:
    print(f"{name}: {count} images")


top_breed_name, top_count = breed_popularity[0]
top_breed_id = next(b['id'] for b in breeds if b['name'] == top_breed_name)
print(f"Top breed: {top_breed_name} with {top_count} images")

try:
    response = requests.get(
        f"https://api.thedogapi.com/v1/images/search?breed_id={top_breed_id}&limit=1",
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    image_data = response.json()
    image_url = image_data[0]['url']
    print(f"Image URL: {image_url}")
except (requests.RequestException, ValueError) as e:
    print(f"Failed to fetch top breed image: {e}")
    image_url = None

if image_url:
    img_resp = requests.get(image_url, stream=True)
    if img_resp.status_code == 200:
        with open("assets/top_breed.png", "wb") as f:
            for chunk in img_resp:
                f.write(chunk)
        print("Saved top breed image as assets/top_breed.png")


import requests
import os
from datetime import datetime
import time

API_KEY = "live_ZsXsTeqiqp2q3pnpbZ62irPQL6CyVohL5xaD9aJVL9zTVesTppc0eXPvpmB0qcSY"  # put your live Dog API key
HEADERS = {"x-api-key": API_KEY}

# Ensure assets folder exists
repo_root = os.path.dirname(__file__)
assets_dir = os.path.join(repo_root, "assets")
os.makedirs(assets_dir, exist_ok=True)
image_path = os.path.join(assets_dir, "top_breed.png")

# File to cache breed counts (prevents repeated full scans)
cache_file = os.path.join(repo_root, "breed_counts.json")

# Step 1: Fetch all breeds
breeds = requests.get("https://api.thedogapi.com/v1/breeds", headers=HEADERS).json()

# Step 2: Count available images for each breed (just 1 per breed for speed)
breed_popularity = []
for breed in breeds:
    name = breed["name"]
    breed_id = breed["id"]

    try:
        response = requests.get(
            f"https://api.thedogapi.com/v1/images/search?breed_id={breed_id}&limit=1",
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()
        images = response.json()
        count = len(images)
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            print(f"Rate limited on {name}, sleeping 10s...")
            time.sleep(10)
            count = 0
        else:
            print(f"Failed for {name}: {e}")
            count = 0
    except requests.RequestException as e:
        print(f"Failed for {name}: {e}")
        count = 0

    breed_popularity.append((name, count))
    time.sleep(1.0)  # slight delay to avoid rate limiting

# Step 3: Pick top breed
breed_popularity.sort(key=lambda x: x[1], reverse=True)
top_breed_name, _ = breed_popularity[0]
top_breed_id = next(b['id'] for b in breeds if b['name'] == top_breed_name)
print(f"Top breed today: {top_breed_name}")

# Step 4: Download top breed image
try:
    response = requests.get(
        f"https://api.thedogapi.com/v1/images/search?breed_id={top_breed_id}&limit=1",
        headers=HEADERS,
        timeout=15
    )
    response.raise_for_status()
    image_url = response.json()[0]["url"]
    print(f"Image URL: {image_url}")
    img_resp = requests.get(image_url, stream=True)
    if img_resp.status_code == 200:
        with open(image_path, "wb") as f:
            for chunk in img_resp:
                f.write(chunk)
        print(f"Saved top breed image: {image_path}")
except requests.exceptions.HTTPError as e:
    if response.status_code == 429:
        print("Rate limited fetching top breed image, skipping...")
except requests.RequestException as e:
    print(f"Failed to fetch top breed image: {e}")

# Step 5: Update README with breed name and date
# Step 5: Update README with image and text
readme_path = os.path.join(repo_root, "README.md")
today_str = datetime.utcnow().strftime("%Y-%m-%d")
ts_str = datetime.utcnow().strftime("%Y%m%d")  # cache-buster for image

# HTML for resized image + text underneath
new_readme_content = f'<img src="assets/top_breed.png?ts={ts_str}" alt="Top Dog Breed" width="300" height="auto"/>\n\n🐾 Most uploaded dog breed today ({today_str}): {top_breed_name}\n'

# Replace old block if it exists
if os.path.exists(readme_path):
    with open(readme_path, "r") as f:
        lines = f.readlines()

    with open(readme_path, "w") as f:
        replaced = False
        for line in lines:
            if line.startswith('<img src="assets/top_breed.png'):
                f.write(new_readme_content)
                replaced = True
                # skip the old text line below the image
                continue
            elif line.startswith("🐾 Most uploaded dog breed today"):
                continue
            else:
                f.write(line)
        if not replaced:
            f.write("\n" + new_readme_content)
else:
    with open(readme_path, "w") as f:
        f.write(new_readme_content)


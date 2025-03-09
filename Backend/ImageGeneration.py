import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

data_dir = "Data"
os.makedirs(data_dir, exist_ok=True)

def open_images(prompt):
    """Opens the generated images one by one."""
    prompt = prompt.replace(" ", "_")
    files = [os.path.join(data_dir, f"{prompt}{i}.jpg") for i in range(1, 5)]

    for image_path in files:
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Allow time for image viewer to open
        except IOError:
            print(f"Unable to open {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

async def query(payload):
    """Sends request to Hugging Face API and returns image content."""
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.content
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

async def generate_images(prompt: str):
    """Generates 4 AI images asynchronously and saves them."""
    tasks = []
    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  # Ensure valid image data
            image_path = os.path.join(data_dir, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_bytes)

def GenerateImages(prompt: str):
    """Handles the generation and opening of images."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_images(prompt))
    loop.close()
    
    open_images(prompt)

def monitor_file():
    """Continuously checks for image generation requests."""
    file_path = os.path.join("Frontend", "Files", "ImageGeneration.data")
    
    retries = 0
    max_retries = 10  # Prevent infinite loop if file is missing

    while retries < max_retries:
        try:
            with open(file_path, "r") as f:
                data = f.read().strip()

            if "," not in data:
                print("Invalid file format. Retrying...")
                retries += 1
                sleep(1)
                continue

            prompt, status = data.split(",")

            if status.strip().lower() == "true":
                print("Generating Images...")
                GenerateImages(prompt.strip())

                # Reset file status after processing
                with open(file_path, "w") as f:
                    f.write("False,False")

                break  # Exit loop after generating images
            else:
                sleep(1)  # Avoid unnecessary CPU usage

        except FileNotFoundError:
            print(f"File '{file_path}' not found. Retrying...")
            retries += 1
            sleep(1)

        except Exception as e:
            print(f"Unexpected error: {e}")
            retries += 1
            sleep(1)

monitor_file()

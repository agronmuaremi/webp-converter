import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request

# Initialize the storage account credentials using the DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a BlobServiceClient using the DefaultAzureCredential
blob_service_client = BlobServiceClient(account_url="https://agronmuaremicomsa.blob.core.windows.net/", credential=credential)

# Define the conversion function
def convert_to_webp(blob_client):
    # Get the blob content as bytes
    blob_content = blob_client.download_blob().readall()

    # Convert the image to webp using Pillow library
    from PIL import Image
    from io import BytesIO
    img = Image.open(BytesIO(blob_content))
    img = img.convert("RGB")
    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=50)

    # Upload the webp image to the destination container
    filename_without_extension = os.path.splitext(blob_client.blob_name)[0]
    destination_blob_client = blob_service_client.get_blob_client(destination_container_name, secure_filename(filename_without_extension) + ".webp")
    destination_blob_client.upload_blob(buffer.getvalue(), overwrite=True)

# Define the main function
def convert_images_to_webp():
    # Get the list of blobs in the source container
    source_container_client = blob_service_client.get_container_client(source_container_name)
    blob_list = source_container_client.list_blobs()

    # Convert each image to webp and save to the destination container
    for blob in blob_list:
        blob_client = blob_service_client.get_blob_client(source_container_name, blob.name)
        convert_to_webp(blob_client)

# To initiate conversion on button click
# You can use any web framework for this, here's an example using Flask:

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        global source_container_name
        global destination_container_name
        source_container_name = request.form.get("source-container")
        destination_container_name = request.form.get("destination-container")
        convert_images_to_webp()
        return render_template("success.html")
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run()
from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
import numpy as np
import io
import base64

app = Flask(__name__)

# Function to calculate the dynamic threshold and percentages
def calculate_light_dark_percentage(image):
    # Convert the image to grayscale
    image = image.convert('L')
    image_array = np.array(image)

    # Generate histogram and calculate dynamic threshold
    histogram, bin_edges = np.histogram(image_array, bins=256, range=(0, 255))
    first_spike_index = np.argmax(histogram > 0)
    last_spike_index = len(histogram) - np.argmax(histogram[::-1] > 0) - 1
    threshold = (bin_edges[first_spike_index] + bin_edges[last_spike_index]) / 2

    # Calculate light and dark pixel percentages
    total_pixels = image_array.size
    light_pixels = np.sum(image_array >= threshold)
    dark_pixels = np.sum(image_array < threshold)
    light_percentage = round((light_pixels / total_pixels) * 100, 2)
    dark_percentage = round((dark_pixels / total_pixels) * 100, 2)

    return light_percentage, dark_percentage

# Convert the image to base64 format for displaying on the front-end
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file:
            image = Image.open(file)
            light_perc, dark_perc = calculate_light_dark_percentage(image)
            uploaded_image_base64 = image_to_base64(image)  # Convert the image to base64 for display
            return render_template("result.html", light=light_perc, dark=dark_perc, uploaded_image=uploaded_image_base64)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

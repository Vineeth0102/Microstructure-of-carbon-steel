from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import io
import base64
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Function to calculate the dynamic threshold and percentages for a single image
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
        files = request.files.getlist("images")  # Get all uploaded images
        if files:
            logger.info(f"{len(files)} image(s) uploaded.")
            light_percentages = []
            dark_percentages = []
            images_base64 = []
            
            # Process each image
            for idx, file in enumerate(files):
                try:
                    image = Image.open(file)
                    light_perc, dark_perc = calculate_light_dark_percentage(image)
                    light_percentages.append(light_perc)
                    dark_percentages.append(dark_perc)
                    images_base64.append(image_to_base64(image))
                    logger.info(f"Processed image {idx + 1}: Light={light_perc}%, Dark={dark_perc}%")
                except Exception as e:
                    logger.error(f"Error processing image {idx + 1}: {e}")
    
            # Calculate average light and dark percentages
            avg_light_perc = round(sum(light_percentages) / len(light_percentages), 2)
            avg_dark_perc = round(sum(dark_percentages) / len(dark_percentages), 2)
            logger.info(f"Average Light={avg_light_perc}%, Average Dark={avg_dark_perc}%")
            
            return render_template("result.html", 
                                   light=avg_light_perc, 
                                   dark=avg_dark_perc, 
                                   images=images_base64)
        else:
            logger.warning("No images were uploaded.")
    else:
        logger.info("Rendering upload page.")
    return render_template("index.html")

if __name__ == "__main__":
    # Set up logging
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    handler.setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    # app.run(debug=True)
    app.run()
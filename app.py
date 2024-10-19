from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import io
import base64

app = Flask(__name__)

# Function to calculate the dynamic threshold and percentages for a single image
def calculate_light_dark_percentage(image):
    # Convert the image to grayscale
    image = image.convert('L')
    image_array = np.array(image)
    
    print("[INFO] Image successfully converted to grayscale")  # Console log

    # Generate histogram and calculate dynamic threshold
    histogram, bin_edges = np.histogram(image_array, bins=256, range=(0, 255))
    first_spike_index = np.argmax(histogram > 0)
    last_spike_index = len(histogram) - np.argmax(histogram[::-1] > 0) - 1
    threshold = (bin_edges[first_spike_index] + bin_edges[last_spike_index]) / 2

    print(f"[INFO] First Spike Index: {first_spike_index}, Last Spike Index: {last_spike_index}")  # Console log
    print(f"[INFO] Calculated Threshold Value: {threshold}")  # Console log

    # Calculate light and dark pixel percentages
    total_pixels = image_array.size
    light_pixels = np.sum(image_array >= threshold)
    dark_pixels = np.sum(image_array < threshold)
    light_percentage = round((light_pixels / total_pixels) * 100, 2)
    dark_percentage = round((dark_pixels / total_pixels) * 100, 2)

    print(f"[INFO] Light Pixels: {light_pixels}, Dark Pixels: {dark_pixels}, Total Pixels: {total_pixels}")  # Console log
    print(f"[INFO] Light Percentage: {light_percentage}%, Dark Percentage: {dark_percentage}%")  # Console log

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
        print(f"[INFO] Number of images uploaded: {len(files)}")  # Console log

        if files:
            light_percentages = []
            dark_percentages = []
            images_base64 = []
            
            # Process each image
            for idx, file in enumerate(files):
                print(f"[INFO] Processing image {idx + 1}")  # Console log
                image = Image.open(file)
                light_perc, dark_perc = calculate_light_dark_percentage(image)
                light_percentages.append(light_perc)
                dark_percentages.append(dark_perc)
                images_base64.append(image_to_base64(image))  # Store image as base64

            # Calculate average light and dark percentages
            if len(files) > 1:
                avg_light_perc = round(sum(light_percentages) / len(light_percentages), 2)
                avg_dark_perc = round(sum(dark_percentages) / len(dark_percentages), 2)
                print(f"[INFO] Average Light Percentage: {avg_light_perc}%, Average Dark Percentage: {avg_dark_perc}%")  # Console log
            else:
                avg_light_perc = light_percentages[0]
                avg_dark_perc = dark_percentages[0]
                print(f"[INFO] Single Image Light Percentage: {avg_light_perc}%, Dark Percentage: {avg_dark_perc}%")  # Console log
            
            return render_template("result.html", 
                                   light=avg_light_perc, 
                                   dark=avg_dark_perc, 
                                   images=images_base64)
    return render_template("index.html")

if __name__ == "__main__":
    # app.run(debug=True)
    app.run()

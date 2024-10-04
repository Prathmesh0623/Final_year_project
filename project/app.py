from flask import Flask, request, render_template, jsonify, send_from_directory
import geemap
import ee

app = Flask(__name__)

# Initialize Earth Engine
ee.Authenticate()
ee.Initialize(project='ee-prathmeshkl2003')

@app.route('/')
def index():
    return render_template('tool.html')

@app.route('/generate-map', methods=['POST'])
def generate_map():
    try:
        # Extract and validate coordinates from the form
        coords = []
        for i in range(1, 5):
            lon = request.form.get(f'longitude{i}')
            lat = request.form.get(f'latitude{i}')
            if lon is None or lat is None:
                return jsonify({'error': 'Missing coordinate input.'})
            try:
                coords.append((float(lon), float(lat)))
            except ValueError:
                return jsonify({'error': f'Invalid coordinate input for point {i}.'})

        # Create a polygon using the coordinates
        nashik_bounds = ee.Geometry.Polygon([coords + [coords[0]]])  # Close the polygon

        # Initialize geemap and set map center
        Map = geemap.Map(center=[coords[0][1], coords[0][0]], zoom=8)

        # Loop through points and fetch satellite imagery
        for lon, lat in coords:
            point = ee.Geometry.Point([lon, lat])
            image = ee.ImageCollection('COPERNICUS/S2') \
                        .filterBounds(point) \
                        .filterDate('2023-01-01', '2023-12-31') \
                        .sort('CLOUDY_PIXEL_PERCENTAGE') \
                        .first()

            if image is None:
                continue  # Handle case where no images are found

            # Visualization parameters
            vis_params = {
                'min': 0,
                'max': 3000,
                'bands': ['B4', 'B3', 'B2']
            }

            Map.addLayer(image, vis_params, f'Sentinel-2 True Color ({lat}, {lon})')

        Map.addLayerControl()

        # Save map as an HTML file
        map_output_path = 'templates/map_result.html'
        Map.save(map_output_path)

        # Return the path to the generated map
        return render_template('map_result.html')
    
    except Exception as e:
        print(f"Error while generating map: {str(e)}")
        return jsonify({'error': str(e)})


# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)

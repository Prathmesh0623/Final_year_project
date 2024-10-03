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
        # Extract coordinates from the form
        lon1 = float(request.form['longitude1'])
        lat1 = float(request.form['latitude1'])
        lon2 = float(request.form['longitude2'])
        lat2 = float(request.form['latitude2'])
        lon3 = float(request.form['longitude3'])
        lat3 = float(request.form['latitude3'])
        lon4 = float(request.form['longitude4'])
        lat4 = float(request.form['latitude4'])

        # Create a polygon using the coordinates
        nashik_bounds = ee.Geometry.Polygon(
            [[[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon4, lat4], [lon1, lat1]]]
        )

        # Initialize geemap and set map center
        Map = geemap.Map(center=[lat1, lon1], zoom=8)
        
        points = nashik_bounds.coordinates().getInfo()

        # Loop through points and fetch satellite imagery
        for coord in points[0]:
            lon, lat = coord
            point = ee.Geometry.Point([lon, lat])
            image = ee.ImageCollection('COPERNICUS/S2') \
                        .filterBounds(point) \
                        .filterDate('2023-01-01', '2023-12-31') \
                        .sort('CLOUDY_PIXEL_PERCENTAGE') \
                        .first()

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
        return jsonify({'map_url': 'map_result.html'})
    
    except Exception as e:
        return jsonify({'error': str(e)})

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)

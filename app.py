from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Enable CORS so your Netlify frontend can talk to this server
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Health check route so Render knows the server is awake
@app.route('/', methods=['GET'])
def health_check():
    return "Rimon Studio Secure Backend is Running!"

# 1. Photoroom (Passport) Route
@app.route('/api/passport', methods=['POST'])
def process_passport():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
        
    file = request.files['image']
    headers = {'x-api-key': os.getenv('PHOTOROOM_API_KEY')}
    data = {'bg_color': '#4DA6FF', 'format': 'png'}
    files = {'image_file': (file.filename, file.read(), file.content_type)}
    
    try:
        response = requests.post('https://sdk.photoroom.com/v1/segment', headers=headers, data=data, files=files)
        if response.status_code == 200:
            return Response(response.content, mimetype='image/png')
        else:
            return jsonify({'error': f"Photoroom Error: {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. Stability AI (Upscale) Route
@app.route('/api/upscale', methods=['POST'])
def process_upscale():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
        
    file = request.files['image']
    headers = {
        'Authorization': f"Bearer {os.getenv('STABILITY_API_KEY')}",
        'Accept': 'image/*'
    }
    data = {
        'prompt': 'Professional 8K UHD photorealistic upscale. Crystal clear details, hyper-detailed textures, zero-interpolation artifacts, pristine quality.',
        'output_format': 'png'
    }
    files = {'image': (file.filename, file.read(), file.content_type)}
    
    try:
        response = requests.post('https://api.stability.ai/v2beta/stable-image/upscale/fast', headers=headers, data=data, files=files)
        if response.status_code == 200:
            return Response(response.content, mimetype='image/png')
        else:
            return jsonify({'error': f"Stability Error: {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
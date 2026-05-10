from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Enable CORS so your Netlify frontend can talk to this server securely
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Health check route so Render knows the server is awake
@app.route('/', methods=['GET'])
def health_check():
    return "Rimon Studio V3 Backend is Running Successfully!"

# 1. REMOVE.BG (Passport) Route - Free and No Watermark
@app.route('/api/passport', methods=['POST'])
def process_passport():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
        
    file = request.files['image']
    
    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': (file.filename, file.read(), file.content_type)},
            data={'size': 'auto', 'bg_color': '#4DA6FF'}, # Light blue passport background
            headers={'X-Api-Key': os.getenv('REMOVE_BG_API_KEY')}
        )
        
        if response.status_code == 200:
            return Response(response.content, mimetype='image/png')
        else:
            return jsonify({'error': f"Remove.bg Error: {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. STABILITY AI (Upscale) Route - Free Credits and No Watermark
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

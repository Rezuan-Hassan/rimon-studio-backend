from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/', methods=['GET'])
def health_check():
    return "Rimon Studio V2 Backend is Running!"

# 1. NEW REMOVE.BG (Passport) Route - NO WATERMARK
@app.route('/api/passport', methods=['POST'])
def process_passport():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
        
    file = request.files['image']
    
    try:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': (file.filename, file.read(), file.content_type)},
            data={'size': 'auto', 'bg_color': '#4DA6FF'},
            headers={'X-Api-Key': os.getenv('REMOVE_BG_API_KEY')}
        )
        
        if response.status_code == 200:
            return Response(response.content, mimetype='image/png')
        else:
            return jsonify({'error': f"Remove.bg Error: {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. NEW DEEPAI (Upscale) Route
@app.route('/api/upscale', methods=['POST'])
def process_upscale():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
        
    file = request.files['image']
    
    try:
        # Step 1: Send the image to DeepAI
        response = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            files={'image': (file.filename, file.read(), file.content_type)},
            headers={'api-key': os.getenv('DEEPAI_API_KEY')}
        )
        
        if response.status_code == 200:
            result_json = response.json()
            # DeepAI returns a web link to the new image, so we need to download it
            if 'output_url' in result_json:
                img_url = result_json['output_url']
                img_response = requests.get(img_url)
                return Response(img_response.content, mimetype='image/jpeg')
            else:
                return jsonify({'error': 'No output URL returned from DeepAI'}), 500
        else:
            return jsonify({'error': f"DeepAI Error: {response.text}"}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

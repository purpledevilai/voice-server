from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests
import os
import base64
import tempfile
import whisper

# Load environment variables from .env file
load_dotenv()

# Load Whisper model
print("Loading model...")
model = whisper.load_model("base")

# Create Flask app
app = Flask(__name__)

# Response endpoint
@app.route('/response', methods=['POST'])
def response():
    try:
        # Get body out of request
        body = request.get_json()
        context_id = body.get('context_id')
        base64_audio = body.get('audio')

        print(f"Session ID: {context_id}")

        # Check if required fields are present
        if not context_id:
            raise Exception("context_id field is required")
        if not base64_audio:
            raise Exception("audio field is required")

        # Decode base64 audio
        audio_data = base64.b64decode(base64_audio)

        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_path = temp_audio_file.name

        print(f"Audio saved to: {temp_audio_path}")

        # Get transcription from Whisper model
        transcription_result = model.transcribe(temp_audio_path)
        transcription = transcription_result.get("text", "No transcription available")
        print(f"Transcription: {transcription}")

        # Make API call to Ajentify
        response = requests.post("https://api.ajentify.com/chat", json={
            "context_id": context_id,
            "message": transcription
        })
        llm_response = response.json().get("response", "No response from Ajentify")

        # Call ElevenLabs API for text-to-speech
        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/IKne3meq5aSn9XLyUdCD"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.getenv('ELEVENLABS_API_KEY')
        }

        data = {
            "text": llm_response,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = requests.post(url, json=data, headers=headers, stream=True)

        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.status_code} {response.text}")
        
        print("Got response back from ElevenLabs API")

        # Save TTS response to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as output_audio_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    output_audio_file.write(chunk)
            output_audio_path = output_audio_file.name

        # Read the audio file and encode it as Base64
        with open(output_audio_path, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

        # Return the Base64-encoded audio as a JSON response
        return jsonify({
            "context_id": context_id,
            "transcription": transcription,
            "audio_base64": encoded_audio
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400

    finally:
        # Clean up temporary files
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if 'output_audio_path' in locals() and os.path.exists(output_audio_path):
            os.remove(output_audio_path)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy"
    })

# Start app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)), debug=os.getenv('DEBUG', False))

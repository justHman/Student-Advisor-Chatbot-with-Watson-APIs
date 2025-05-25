from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import ibm_db
import os
import io
from dotenv import load_dotenv
from ibmservices import WatsonAssistant, SpeechToText, TextToSpeech

# Load biến môi trường từ file .env
# Important: .env file should be in the PARENT directory (WatsonStudentAdvisor)
# So we go up one level to load it.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


# Khởi tạo Flask app
app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app) # Cho phép CORS để giao tiếp với front-end

# Khởi tạo Watson services
assistant = WatsonAssistant()
stt = SpeechToText()
tts = TextToSpeech()

# Kết nối Db2
conn = None
try:
    conn_str = (
        f"DATABASE={os.getenv('DB2_DATABASE')};"
        f"HOSTNAME={os.getenv('DB2_HOST')};"
        f"PORT={os.getenv('DB2_PORT')};"
        f"UID={os.getenv('DB2_USERNAME')};"
        f"PWD={os.getenv('DB2_PASSWORD')};SECURITY=SSL;"
    )
    conn = ibm_db.connect(conn_str, "", "")
    print("Successfully connected to Db2")
except Exception as e:
    print(f"Error connecting to Db2: {e}")
    conn = None # Ensure conn is None if connection fails

@app.route('/')
def index():
    return app.send_static_file('index.html')

# Endpoint 1: Speech to Text
@app.route('/api/stt', methods=['POST'])
def speech_to_text_endpoint(): # Renamed function
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file part'}), 400
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected audio file'}), 400

        transcript = stt.transcribe(audio_file)
        if transcript:
            return jsonify({'transcript': transcript})
        else:
            return jsonify({'error': 'Could not transcribe audio or audio empty'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint 2: Watson Assistant
@app.route('/api/message', methods=['POST'])
def assistant_message_endpoint(): # Renamed function
    try:
        text = request.json['text']
        session_id = assistant.create_session()
        response = assistant.send_message(session_id, text)
        assistant.delete_session(session_id)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint 3: Text to Speech
@app.route('/api/tts', methods=['POST'])
def text_to_speech_endpoint(): # Renamed function
    try:
        text = request.json['text']
        audio_content = tts.synthesize(text)
        return send_file(io.BytesIO(audio_content), mimetype='audio/wav', as_attachment=True, download_name='output.wav')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint 4: Db2 Courses
@app.route('/courses', methods=['GET'])
def get_courses():
    if not conn:
        return jsonify({'error': 'Database connection not established'}), 500
    try:
        course_id_param = request.args.get('id', "") # Renamed to avoid conflict
        # Basic sanitization/check for course_id_param
        if not isinstance(course_id_param, str):
             return jsonify({'error': 'Invalid course ID parameter'}), 400

        query = "SELECT NAME, DESCRIPTION FROM COURSES WHERE NAME LIKE ?"
        stmt = ibm_db.prepare(conn, query)
        search_term = f"%{course_id_param}%"
        ibm_db.bind_param(stmt, 1, search_term)
        ibm_db.execute(stmt)
        
        result_list = [] # Renamed to avoid conflict
        row = ibm_db.fetch_assoc(stmt)
        while row:
            result_list.append({'name': row['NAME'], 'description': row['DESCRIPTION']})
            row = ibm_db.fetch_assoc(stmt)
        return jsonify({'courses': result_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Đóng kết nối Db2 khi server dừng
@app.teardown_appcontext
def close_db(e=None):
    if conn:
        ibm_db.close(conn)
        print("Db2 connection closed.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
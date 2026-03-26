import os
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'ml-evaluator', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

_ml_engine = None

def get_ml_engine():
    global _ml_engine
    if _ml_engine is None:
        try:
            from ml_engine import process_evaluation_request
            _ml_engine = process_evaluation_request
            print("✓ ML Engine loaded")
        except Exception as e:
            print(f"✗ ML Engine error: {e}")
            raise
    return _ml_engine

@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "ml-evaluator-api"})

@app.route('/api/evaluate', methods=['POST'])
@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        if 'candidates_file' not in request.files or 'rubric_file' not in request.files:
            return jsonify({"error": "Missing files"}), 400
        
        candidates_file = request.files['candidates_file']
        rubric_file = request.files['rubric_file']
        
        candidates_text = candidates_file.read().decode('utf-8')
        rubric_text = rubric_file.read().decode('utf-8')
        
        ml_engine = get_ml_engine()
        results = ml_engine(
            candidates_csv=candidates_text,
            rubric_text=rubric_text
        )
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/')
@app.route('/api')
def root():
    return jsonify({"message": "ML Evaluator API"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8000)))


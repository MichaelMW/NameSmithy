#!/usr/bin/env python
"""
NameSmithy Flask Server
Production-ready server using original working models
"""

from flask import Flask, send_from_directory, jsonify, request, render_template_string, Response
import os
import pickle
import numpy as np
from pathlib import Path

app = Flask(__name__)

# Global variables for models
gbr_model = None
known_names = {}
rnn_parameters = None
chars = sorted(list(set('abcdefghijklmnopqqrstuvwxyz ')))
char_to_int = {c: i for i, c in enumerate(chars)}
int_to_char = {i: c for i, c in enumerate(chars)}

# Global state for generation tracking
generation_sessions = {}

def name_to_vec(name, max_length=15):
    """Convert name to vector (original logic)."""
    name = name.lower()
    filler = max_length - len(name)
    return [char_to_int.get(char, 0) for char in name + ' ' * filler]

def format_score(score):
    """Format score for display."""
    if isinstance(score, str):
        return score
    return round(score * 100, 1) if score is not None else "N/A"

def load_original_models():
    """Load the original working models from local models directory."""
    global gbr_model, known_names
    
    print("🔨 Loading models from local directory...")
    base_path = Path(__file__).absolute().parent / "models"  # Use local models folder
    print("🔍 Base path resolved to: {}".format(base_path))
    
    # Load GBR model
    try:
        gbr_path = base_path / "judge" / "gbr.n100.genz.v3"
        print("🔍 Looking for GBR model at: {}".format(gbr_path))
        if not gbr_path.exists():
            print("❌ GBR model file not found at expected path")
            gbr_model = None
        else:
            with open(str(gbr_path), 'rb') as f:
                gbr_model = pickle.load(f)
            print("✅ Loaded GBR model")
    except Exception as e:
        print("❌ Could not load GBR model: {}".format(e))
        gbr_model = None
    
    # Load known names
    try:
        popularity_path = base_path / "names" / "genz.avg.tsv"
        print("🔍 Looking for known names at: {}".format(popularity_path))
        with open(str(popularity_path), 'r') as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) >= 3:
                    name = parts[0]
                    sex = 0 if parts[1] == "F" else 1
                    rank = float(parts[2])
                    vec = name_to_vec(name)
                    feature_key = tuple([sex] + vec)
                    known_names[feature_key] = rank
        
        # Load bad words with negative scores
        bad_words_path = base_path / "badwords" / "bad.merged.txt"
        print("🔍 Looking for bad words at: {}".format(bad_words_path))
        if not bad_words_path.exists():
            print("⚠️  Bad words file not found, continuing without it")
        else:
            with open(str(bad_words_path), 'r') as f:
                for line in f.readlines():
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        bad_word = parts[0]
                        score = float(parts[1])
                        vec = name_to_vec(bad_word)
                        # Add for both genders
                        known_names[tuple([0] + vec)] = score  # Female
                        known_names[tuple([1] + vec)] = score  # Male
        
        print("✅ Loaded {} known names".format(len(known_names)))
    except Exception as e:
        print("❌ Could not load known names: {}".format(e))

def score_name_original(name, gender='F'):
    """Score a name using original logic."""
    if gbr_model is None:
        return {
            'name': name,
            'score': 'Model not loaded',
            'known_rank': 'Model not loaded',
            'appropriate': True,
            'error': 'GBR model not loaded'
        }
    
    # Original scoring logic (from judge.py)
    gender_bit = 0 if gender == 'F' else 1
    name_vec = name_to_vec(name.lower())
    feature_vector = [[gender_bit] + name_vec]
    
    # Always calculate predicted score using GBR model
    predicted_score = gbr_model.predict(feature_vector)[0]
    
    # Look up known rank (historical data including bad words)
    lookup_key = tuple(feature_vector[0])
    known_rank = known_names.get(lookup_key, None)
    
    # For display purposes, we always show the predicted score as the main score
    # Historical score is shown separately for reference
    final_score = predicted_score
    
    # Determine appropriateness based on known bad words or predicted score
    if known_rank is not None and known_rank < 0:
        # Known bad word - override with historical negative score for appropriateness
        appropriate = False
        display_score = known_rank  # Show the negative score for bad words
    else:
        appropriate = bool(predicted_score >= 0)
        display_score = predicted_score
    
    return {
        'name': name.capitalize(),
        'score': format_score(display_score),
        'raw_score': display_score,
        'predicted_score': format_score(predicted_score),
        'historical_score': format_score(known_rank) if known_rank is not None else None,
        'known_rank': "Found: {}".format(format_score(known_rank)) if known_rank is not None else "Not found",
        'score_source': "Predicted",
        'appropriate': appropriate,
        'quality_tier': get_quality_tier(display_score)
    }

def get_quality_tier(score):
    """Get quality description."""
    if score is None:
        return "Unknown"
    if score < 0:
        return "Inappropriate"
    elif score < 0.2:
        return "Poor"
    elif score < 0.4:
        return "Fair" 
    elif score < 0.6:
        return "Good"
    elif score < 0.8:
        return "Very Good"
    else:
        return "Excellent"

def softmax(x):
    """Compute softmax values for x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def generate_name_rnn(gender='F', seed=None):
    """Generate a name using simple RNN-like logic."""
    if seed is None:
        import time
        # Use high-precision time for maximum randomness
        current_time = time.time()
        seed = int((current_time * 1000000) % 999999)
    
    # Set both numpy and python random seeds for consistency
    np.random.seed(seed)
    import random
    random.seed(seed)
    
    # Simple character-level name generation
    vocab_size = len(chars)
    
    # Start with empty character
    name = ""
    current_char = " "  # Start with space
    max_length = 15
    
    # Generate character by character
    for i in range(max_length):
        if current_char == '\n' or len(name) > 12:
            break
            
        # Simple pattern-based generation for demo
        if len(name) == 0:
            # First character - use common starting letters with more variety
            if gender == 'F':
                first_chars = ['a', 'e', 'i', 'o', 'j', 'm', 's', 'k', 'l', 'c', 'n', 'r', 'b', 'h', 'g', 'v', 'z', 'p']
                weights = [0.12, 0.10, 0.08, 0.06, 0.08, 0.08, 0.07, 0.06, 0.06, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03, 0.02, 0.02, 0.01]
                current_char = np.random.choice(first_chars, p=weights)
            else:
                first_chars = ['a', 'j', 'm', 'r', 'd', 'c', 'b', 'l', 't', 'n', 's', 'k', 'g', 'h', 'w', 'p', 'v', 'z']
                weights = [0.10, 0.09, 0.08, 0.08, 0.07, 0.07, 0.06, 0.06, 0.06, 0.05, 0.05, 0.04, 0.04, 0.04, 0.03, 0.03, 0.02, 0.02]
                current_char = np.random.choice(first_chars, p=weights)
        else:
            # Pattern-based next character
            last_char = name[-1] if name else ' '
            
            # Vowel after consonant, consonant after vowel pattern
            vowels = 'aeiou'
            consonants = 'bcdfghjklmnpqrstvwxyz'
            
            if last_char in vowels:
                # After vowel, often consonant or another vowel
                consonant_prob = 0.6 + np.random.random() * 0.2  # 0.6-0.8 probability
                if np.random.random() < consonant_prob:
                    current_char = np.random.choice(list(consonants))
                else:
                    current_char = np.random.choice(list(vowels))
            else:
                # After consonant, often vowel
                vowel_prob = 0.7 + np.random.random() * 0.2  # 0.7-0.9 probability
                if np.random.random() < vowel_prob:
                    current_char = np.random.choice(list(vowels))
                else:
                    current_char = np.random.choice(list(consonants))
            
            # End name probability with some variation
            min_length = 3 + np.random.randint(0, 3)  # 3-5 minimum length
            end_prob = 0.2 + (len(name) - min_length) * 0.1  # Increasing probability
            if len(name) >= min_length and np.random.random() < end_prob:
                break
        
        name += current_char
    
    # Clean up the name
    name = name.strip().capitalize()
    
    # Ensure reasonable length
    if len(name) < 3:
        name += np.random.choice(['a', 'e', 'i', 'o'])
    
    return name if name else "Nora"

# Initialize global randomness and models on startup
import time
import random
# Seed global random state with high-precision time for maximum entropy
random.seed(int(time.time() * 1000000) % 999999)
np.random.seed(int(time.time() * 1000000) % 999999)

load_original_models()

# Serve static files from docs directory
@app.route('/')
def index():
    """Serve the main web interface"""
    try:
        return send_from_directory('docs', 'index.html')
    except Exception as e:
        return "Error loading web interface: {}".format(str(e)), 500

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static assets (CSS, JS, images)"""
    try:
        return send_from_directory('docs', filename)
    except Exception as e:
        return "File not found: {}".format(filename), 404

# API Endpoints
@app.route('/api/status')
def api_status():
    """Check API status"""
    return jsonify({
        'status': 'online',
        'gbr_loaded': gbr_model is not None,
        'known_names_count': len(known_names),
        'version': '1.0.0'
    })

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Start name generation and return session ID."""
    try:
        data = request.get_json() or {}
        count = int(data.get('count', 5))
        gender = data.get('gender', 'F')
        style = data.get('style', 'random')
        min_score = float(data.get('min_score', 70))
        max_score = float(data.get('max_score', 100))
        
        # Create session ID
        import time
        import threading
        session_id = str(int(time.time() * 1000))
        
        # Initialize session state
        generation_sessions[session_id] = {
            'status': 'running',
            'attempts': 0,
            'found': 0,
            'target': count,
            'results': [],
            'start_time': time.time()
        }
        
        # Start generation in background thread
        def generate_in_background():
            try:
                results = []
                generated_names = set()
                attempts = 0
                min_threshold = min_score / 100.0
                max_threshold = max_score / 100.0
                
                # Create highly randomized base seed using multiple time components
                import random
                current_time = time.time()
                microseconds = int((current_time * 1000000) % 1000000)
                base_seed = (int(current_time * 1000) + microseconds + random.randint(0, 999999)) % 999999
                
                print("🎯 Session {} - Generating {} {} names with style '{}' and score range {}-{} (base_seed: {})".format(
                    session_id, count, gender, style, min_score, max_score, base_seed))
                
                while len(results) < count and generation_sessions.get(session_id, {}).get('status') == 'running':
                    attempts += 1
                    # Generate highly random seed for each attempt
                    current_micro = int((time.time() * 1000000) % 1000000)
                    seed = (base_seed + attempts * 23 + current_micro + np.random.randint(0, 10000)) % 999999
                    
                    # Update session progress
                    if session_id in generation_sessions:
                        generation_sessions[session_id]['attempts'] = attempts
                        generation_sessions[session_id]['found'] = len(results)
                    
                    name = generate_name_rnn(gender, seed)
                    
                    if name and len(name) >= 3 and name.lower() not in generated_names:
                        generated_names.add(name.lower())
                        score_result = score_name_original(name, gender)
                        
                        # Apply style filtering
                        should_include = True
                        if style == 'popular':
                            should_include = score_result.get('known_rank') != 'Not found'
                        elif style == 'unique':
                            should_include = score_result.get('known_rank') == 'Not found'
                        
                        # Check score range
                        score_in_range = (min_threshold <= score_result['raw_score'] <= max_threshold)
                        if should_include and score_in_range:
                            results.append(score_result)
                            # Update session results immediately when found
                            if session_id in generation_sessions:
                                generation_sessions[session_id]['results'] = results
                            print("✅ Session {} - Found qualifying name #{}: {} (score: {:.1f})".format(
                                session_id, len(results), name, score_result['raw_score'] * 100))
                
                # Update final results
                if session_id in generation_sessions:
                    results.sort(key=lambda x: x.get('raw_score', 0), reverse=True)
                    generation_sessions[session_id]['results'] = results
                    generation_sessions[session_id]['status'] = 'completed'
                    print("✅ Session {} - Completed with {} names".format(session_id, len(results)))
                    
            except Exception as e:
                print("❌ Session {} - Error: {}".format(session_id, e))
                if session_id in generation_sessions:
                    generation_sessions[session_id]['status'] = 'error'
                    generation_sessions[session_id]['error'] = str(e)
        
        # Start background thread
        thread = threading.Thread(target=generate_in_background)
        thread.daemon = True
        thread.start()
        
        response_data = {
            'success': True,
            'session_id': session_id,
            'status': 'started'
        }
        print("🔧 DEBUG - API /generate response: {}".format(response_data))
        return jsonify(response_data)
        
    except Exception as e:
        print("❌ Error starting generation: {}".format(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/status/<session_id>')
def api_generate_status(session_id):
    """Get generation progress for a session."""
    if session_id not in generation_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = generation_sessions[session_id]
    import time
    elapsed = time.time() - session['start_time']
    
    response = {
        'status': session['status'],
        'attempts': session['attempts'],
        'found': session['found'],
        'target': session['target'],
        'elapsed': int(elapsed)
    }
    
    if session['status'] == 'completed':
        response['results'] = session['results']
        print("🔧 DEBUG - Status response (completed): {} results".format(len(session['results'])))
    elif session['status'] == 'error':
        response['error'] = session.get('error', 'Unknown error')
        print("🔧 DEBUG - Status response (error): {}".format(response['error']))
    elif session['status'] == 'aborted':
        response['results'] = session.get('final_results', [])
        print("🔧 DEBUG - Status response (aborted): {} partial results".format(len(response['results'])))
    
    return jsonify(response)

@app.route('/api/generate/abort/<session_id>', methods=['POST'])
def api_generate_abort(session_id):
    """Abort a generation session and return partial results."""
    if session_id in generation_sessions:
        session = generation_sessions[session_id]
        
        print("🔧 DEBUG - Session state before abort: status={}, found={}, results_count={}".format(
            session.get('status'), session.get('found'), len(session.get('results', []))))
        
        # Sort any partial results by score before returning
        partial_results = session.get('results', [])
        partial_results.sort(key=lambda x: x.get('raw_score', 0), reverse=True)
        
        session['status'] = 'aborted'
        session['final_results'] = partial_results  # Store for status endpoint
        
        print("🛑 Session {} - Aborted by user, returning {} partial results".format(
            session_id, len(partial_results)))
        
        if len(partial_results) > 0:
            print("🔧 DEBUG - Partial results: {}".format([r['name'] for r in partial_results]))
        
        return jsonify({
            'success': True, 
            'message': 'Generation aborted',
            'partial_results': partial_results,
            'found_count': len(partial_results)
        })
    else:
        return jsonify({'error': 'Session not found'}), 404

@app.route('/api/evaluate', methods=['POST'])
def api_evaluate():
    """Evaluate a name using original models."""
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        gender = data.get('gender', 'F')
        
        print("🔍 API received: name='{}', gender='{}'".format(name, gender))
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if gender not in ['F', 'M']:
            return jsonify({'error': 'Gender must be F or M'}), 400
        
        result = score_name_original(name, gender)
        print("📊 API result: {}".format(result))
        
        response = {
            'success': True,
            'result': result
        }
        print("📡 API response: {}".format(response))
        
        return jsonify(response)
        
    except Exception as e:
        print("❌ Error evaluating name: {}".format(e))
        return jsonify({'error': 'Failed to evaluate name: {}'.format(str(e))}), 500

@app.route('/api/test-bad-words')
def api_test_bad_words():
    """Test bad word detection."""
    try:
        bad_words = ['shit', 'poop', 'damn', 'stupid', 'hell']
        good_names = ['Emma', 'Oliver', 'Sophia', 'Liam']
        
        results = {
            'bad_words': [],
            'good_names': []
        }
        
        for word in bad_words:
            result = score_name_original(word, 'F')
            results['bad_words'].append(result)
        
        for name in good_names:
            result = score_name_original(name, 'F')
            results['good_names'].append(result)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Development endpoints
@app.route('/test')
def test_page():
    """Simple test page for API testing"""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>NameSmithy API Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .test-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
            pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
            input, select { padding: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>🔨 NameSmithy API Test Page</h1>
        
        <div class="test-section">
            <h3>1. API Status</h3>
            <button onclick="testStatus()">Check Status</button>
            <pre id="status-result"></pre>
        </div>
        
        <div class="test-section">
            <h3>2. Generate Names</h3>
            <input type="number" id="gen-count" value="5" min="1" max="50"> names
            <select id="gen-gender">
                <option value="F">Female</option>
                <option value="M">Male</option>
            </select>
            <input type="number" id="gen-min-score" value="0" min="0" max="100"> min score
            <button onclick="testGenerate()">Generate</button>
            <pre id="generate-result"></pre>
        </div>
        
        <div class="test-section">
            <h3>3. Evaluate Name</h3>
            <input type="text" id="eval-name" placeholder="Enter name..." value="Emma">
            <select id="eval-gender">
                <option value="F">Female</option>
                <option value="M">Male</option>
            </select>
            <button onclick="testEvaluate()">Evaluate</button>
            <pre id="evaluate-result"></pre>
        </div>
        
        <div class="test-section">
            <h3>4. Test Bad Words</h3>
            <button onclick="testBadWords()">Test Bad Words</button>
            <pre id="badwords-result"></pre>
        </div>
        
        <script>
            async function apiCall(endpoint, method = 'GET', data = null) {
                try {
                    const options = {
                        method: method,
                        headers: {'Content-Type': 'application/json'}
                    };
                    if (data) options.body = JSON.stringify(data);
                    
                    const response = await fetch(endpoint, options);
                    const result = await response.json();
                    return result;
                } catch (error) {
                    return {error: error.message};
                }
            }
            
            async function testStatus() {
                const result = await apiCall('/api/status');
                document.getElementById('status-result').textContent = JSON.stringify(result, null, 2);
            }
            
            async function testGenerate() {
                const count = document.getElementById('gen-count').value;
                const gender = document.getElementById('gen-gender').value;
                const min_score = document.getElementById('gen-min-score').value;
                
                const result = await apiCall('/api/generate', 'POST', {
                    count: parseInt(count),
                    gender: gender,
                    min_score: parseInt(min_score),
                    style: min_score > 0 ? 'filtered' : 'random'
                });
                document.getElementById('generate-result').textContent = JSON.stringify(result, null, 2);
            }
            
            async function testEvaluate() {
                const name = document.getElementById('eval-name').value;
                const gender = document.getElementById('eval-gender').value;
                
                const result = await apiCall('/api/evaluate', 'POST', {
                    name: name,
                    gender: gender
                });
                document.getElementById('evaluate-result').textContent = JSON.stringify(result, null, 2);
            }
            
            async function testBadWords() {
                const result = await apiCall('/api/test-bad-words');
                document.getElementById('badwords-result').textContent = JSON.stringify(result, null, 2);
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    import socket
    
    def find_free_port(start_port=5000):
        """Find a free port starting from start_port"""
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return None
    
    port = find_free_port(5000)
    if port is None:
        print("❌ Could not find a free port")
        exit(1)
    
    print("🚀 Starting NameSmithy Server...")
    print("📍 Web Interface: http://localhost:{}".format(port))
    print("🧪 API Test Page: http://localhost:{}/test".format(port))
    print("📡 API Status: http://localhost:{}/api/status".format(port))
    print("⚠️  Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=port, debug=True)
# app.py
from flask import Flask, render_template, jsonify, request, abort
import json
from functools import lru_cache, wraps
import os
from pathlib import Path
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable admin mode for development
os.environ['ADMIN_MODE'] = 'true'

app = Flask(__name__, static_folder='images', static_url_path='/images')

# Admin access control
ADMIN_MODE = os.environ.get('ADMIN_MODE', 'false').lower() == 'true'

# File paths
CONFIG_DIR = Path('config')
DATA_DIR = Path('data')
ATTRIBUTES_FILE = CONFIG_DIR / 'attributes.json'
TOOLTIPS_DIR = CONFIG_DIR / 'tooltips'
PROFILES_FILE = DATA_DIR / 'profiles.json'
ARCHETYPES_FILE = DATA_DIR / 'archetypal_profiles.json'

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ADMIN_MODE:
            return jsonify({"error": "Admin mode disabled"}), 403
        return f(*args, **kwargs)
    return decorated_function

def ensure_directories():
    """Ensure all required directories exist"""
    DATA_DIR.mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)
    TOOLTIPS_DIR.mkdir(exist_ok=True)
    return DATA_DIR, CONFIG_DIR

@lru_cache()
def load_attributes_config():
    """Load the attributes configuration"""
    if not ATTRIBUTES_FILE.exists():
        return {}
    with open(ATTRIBUTES_FILE, 'r') as f:
        return json.load(f)

@lru_cache()
def load_tooltips(lang='en'):
    """Load tooltips for specified language"""
    tooltip_file = TOOLTIPS_DIR / f'{lang}.json'
    if not tooltip_file.exists():
        return {}
    with open(tooltip_file, 'r') as f:
        return json.load(f)

def get_default_values():
    """Get default values for all attributes from config"""
    config = load_attributes_config()
    default_values = {}
    
    for category in config.get('categories', {}).values():
        for section in category.get('sections', {}).values():
            for attr_id, attr in section.get('attributes', {}).items():
                default_values[attr_id] = attr.get('default_value', 5)
    
    return default_values

@lru_cache()
def load_profiles():
    ensure_directories()
    if not PROFILES_FILE.exists():
        return {}
    with open(PROFILES_FILE, 'r') as f:
        return json.load(f)

def create_default_archetypes():
    archetypes = {
        "spazz": generate_archetype_values(high=["explosiveness", "strength", "cardio"], 
                                         low=["controlledMovements", "controlledEgo", "safetyConsciousness"]),
        "brute": generate_archetype_values(high=["strength", "gripStrength", "weight"], 
                                         low=["flexibility", "mobility", "controlledMovements"]),
        "veteran": generate_archetype_values(high=["depthOfKnowledge", "controlledMovements", "controlledEgo"], 
                                          low=["explosiveness", "cardio", "strength"]),
        "professor": generate_archetype_values(high=["depthOfKnowledge", "communicative", "feedbackReceptivity"], 
                                            low=["explosiveness", "strength", "cardio"]),
        "competitor": generate_archetype_values(high=["cardio", "explosiveness", "specificWork"], 
                                             low=["controlledEgo", "friendlyAttitude", "communicative"]),
        "stinky_troll": generate_archetype_values(high=["strength", "weight", "gripStrength"],
                                                low=["hygiene", "personalCleanliness", "equipmentHygiene"])
    }
    return archetypes

def generate_archetype_values(high=None, low=None):
    attributes = {
        # Technical Attributes
        "controlledMovements": random.randint(4, 7),
        "controlledSubmissions": random.randint(4, 7),
        "modularIntensity": random.randint(4, 7),
        "depthOfKnowledge": random.randint(4, 7),
        "injuryKnowledge": random.randint(4, 7),
        "specificWork": random.randint(4, 7),
        
        # Mindset
        "controlledEgo": random.randint(4, 7),
        "friendlyAttitude": random.randint(4, 7),
        "rdMindset": random.randint(4, 7),
        "notOvertalking": random.randint(4, 7),
        "communicative": random.randint(4, 7),
        "feedbackReceptivity": random.randint(4, 7),
        "safetyConsciousness": random.randint(4, 7),
        "recoveryAwareness": random.randint(4, 7),
        "identifyWeaknesses": random.randint(4, 7),
        "reliability": random.randint(4, 7),
        
        # Physical Attributes
        "strength": random.randint(4, 7),
        "gripStrength": random.randint(4, 7),
        "flexibility": random.randint(4, 7),
        "mobility": random.randint(4, 7),
        "weight": random.randint(4, 7),
        "cardio": random.randint(4, 7),
        "explosiveness": random.randint(4, 7),
        "coordination": random.randint(4, 7),
        "reactionTime": random.randint(4, 7),
        "constitution": random.randint(4, 7),
        "hygiene": random.randint(4, 7)
    }
    
    if high:
        for attr in high:
            attributes[attr] = random.randint(8, 10)
    
    if low:
        for attr in low:
            attributes[attr] = random.randint(1, 3)
    
    return attributes

@lru_cache()
def load_archetypal_profiles():
    ensure_directories()
    if not ARCHETYPES_FILE.exists():
        return {}
    try:
        with open(ARCHETYPES_FILE, 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return {}

def save_profiles(profiles_data):
    ensure_directories()
    try:
        temp_file = PROFILES_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(profiles_data, f, indent=4)
        temp_file.replace(PROFILES_FILE)
    except Exception as e:
        print(f"Error saving profiles: {str(e)}")
        raise

def clear_caches():
    load_profiles.cache_clear()
    load_archetypal_profiles.cache_clear()
    load_attributes_config.cache_clear()
    load_tooltips.cache_clear()

def save_archetypes(archetypes_data):
    ensure_directories()
    try:
        temp_file = ARCHETYPES_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(archetypes_data, f, indent=4)
        temp_file.replace(ARCHETYPES_FILE)
    except Exception as e:
        print(f"Error saving archetypes: {str(e)}")
        raise

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
@admin_required
def admin_panel():
    return render_template('admin.html')

@app.route('/api/profiles')
def get_profiles():
    return jsonify(load_profiles())

@app.route('/api/profiles/<profile_name>')
def get_profile(profile_name):
    profiles = load_profiles()
    return jsonify(profiles.get(profile_name, {}))

@app.route('/api/profiles', methods=['POST'])
def create_profile():
    try:
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Profile name is required"}), 400

        profiles = load_profiles()
        profile_name = data['name']
        
        if profile_name in profiles:
            return jsonify({"error": "Profile already exists"}), 409

        if 'archetype' in data:
            archetypes = load_archetypal_profiles()
            archetype_name = data['archetype']
            if archetype_name in archetypes:
                profiles[profile_name] = archetypes[archetype_name].copy()
                profiles[profile_name].pop('metadata', None)
            else:
                return jsonify({"error": "Archetype not found"}), 404
        else:
            profiles[profile_name] = get_default_values()

        save_profiles(profiles)
        return jsonify(profiles[profile_name])
    except Exception as e:
        print(f"Error creating profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/archetypes')
def get_archetypes():
    return jsonify(load_archetypal_profiles())

@app.route('/api/archetypes/<archetype_name>')
def get_archetype(archetype_name):
    archetypes = load_archetypal_profiles()
    if archetype_name not in archetypes:
        return jsonify({"error": "Archetype not found"}), 404
    return jsonify(archetypes[archetype_name])

@app.route('/api/admin/archetypes/<archetype_name>', methods=['GET', 'PUT', 'POST'])
@admin_required
def admin_archetype(archetype_name):
    try:
        archetypes = load_archetypal_profiles()
        
        if request.method == 'GET':
            if archetype_name not in archetypes:
                return jsonify({"error": "Archetype not found"}), 404
            return jsonify(archetypes[archetype_name])
            
        elif request.method in ['PUT', 'POST']:
            data = request.json
            archetypes[archetype_name] = data
            save_archetypes(archetypes)
            clear_caches()
            return jsonify({"status": "success"})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/profiles/<profile_name>', methods=['POST'])
def update_profile(profile_name):
    try:
        profiles = load_profiles()
        data = request.json
        profiles[profile_name] = data
        save_profiles(profiles)
        clear_caches()
        return jsonify(profiles[profile_name])
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/config')
def get_config():
    lang = request.args.get('lang', 'en')
    return jsonify({
        'attributes': load_attributes_config(),
        'tooltips': load_tooltips(lang)
    })

if __name__ == '__main__':
    app.run(debug=True)
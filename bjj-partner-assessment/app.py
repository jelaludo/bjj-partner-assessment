# app.py
from flask import Flask, render_template, jsonify, request, abort
import json
from functools import lru_cache
import os
from pathlib import Path
import random

app = Flask(__name__)

# File paths
CONFIG_DIR = Path('config')
DATA_DIR = Path('data')
ATTRIBUTES_FILE = CONFIG_DIR / 'attributes.json'
TOOLTIPS_DIR = CONFIG_DIR / 'tooltips'
PROFILES_FILE = DATA_DIR / 'profiles.json'
ARCHETYPES_FILE = DATA_DIR / 'archetypal_profiles.json'

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

# Cache for profiles
@lru_cache()
def load_profiles():
    ensure_directories()
    if not PROFILES_FILE.exists():
        return {}
    with open(PROFILES_FILE, 'r') as f:
        return json.load(f)

# Add this function after ensure_data_directory()
def create_default_archetypes():
    archetypes = {
        "spazz": generate_archetype_values(high=["explosiveness", "strength", "cardio"], low=["controlledMovements", "controlledEgo", "safetyConsciousness"]),
        "brute": generate_archetype_values(high=["strength", "gripStrength", "weight"], low=["flexibility", "mobility", "controlledMovements"]),
        "veteran": generate_archetype_values(high=["depthOfKnowledge", "controlledMovements", "controlledEgo"], low=["explosiveness", "cardio", "strength"]),
        "professor": generate_archetype_values(high=["depthOfKnowledge", "communicative", "feedbackReceptivity"], low=["explosiveness", "strength", "cardio"]),
        "competitor": generate_archetype_values(high=["cardio", "explosiveness", "specificWork"], low=["controlledEgo", "friendlyAttitude", "communicative"])
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
    
    # Set high values (8-10)
    if high:
        for attr in high:
            attributes[attr] = random.randint(8, 10)
    
    # Set low values (1-3)
    if low:
        for attr in low:
            attributes[attr] = random.randint(1, 3)
    
    return attributes

# Modify the load_archetypal_profiles function
@lru_cache()
def load_archetypal_profiles():
    ensure_directories()
    print("\n=== Debug: Loading Archetypes ===")
    print(f"Checking file: {ARCHETYPES_FILE}")
    print(f"File exists: {ARCHETYPES_FILE.exists()}")
    
    if not ARCHETYPES_FILE.exists():
        print("File doesn't exist!")
        return {}
        
    try:
        with open(ARCHETYPES_FILE, 'r') as f:
            data = json.load(f)
            print(f"Loaded data keys: {list(data.keys())}")
            return data
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return {}

# Save profiles to JSON file
def save_profiles(profiles_data):
    ensure_directories()
    try:
        # Create a temporary file first
        temp_file = PROFILES_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(profiles_data, f, indent=4)
        
        # Then rename it to the actual file (atomic operation)
        temp_file.replace(PROFILES_FILE)
    except Exception as e:
        print(f"Error saving profiles: {str(e)}")
        raise

# Update clear_caches to include new functions
def clear_caches():
    load_profiles.cache_clear()
    load_archetypal_profiles.cache_clear()
    load_attributes_config.cache_clear()
    load_tooltips.cache_clear()

def save_archetypes(archetypes_data):
    ensure_directories()
    try:
        # Create a temporary file first
        temp_file = ARCHETYPES_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(archetypes_data, f, indent=4)
        
        # Then rename it to the actual file (atomic operation)
        temp_file.replace(ARCHETYPES_FILE)
    except Exception as e:
        print(f"Error saving archetypes: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

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
            # Create empty profile with default values from config
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
def get_specific_archetype(archetype_name):
    print(f"\n=== Debug: Archetype Request ===")
    print(f"Requested archetype: {archetype_name}")
    
    archetypes = load_archetypal_profiles()
    print(f"Available archetypes: {list(archetypes.keys())}")
    
    result = archetypes.get(archetype_name, {})
    print(f"Found data: {result}")
    print("===============================\n")
    return jsonify(result)

@app.route('/api/archetypes/<archetype_name>', methods=['POST'])
def update_archetype(archetype_name):
    try:
        archetypes = load_archetypal_profiles()
        if archetype_name not in archetypes:
            abort(404)
        
        data = request.json
        # Preserve metadata if it exists
        if 'metadata' in archetypes[archetype_name]:
            metadata = archetypes[archetype_name]['metadata']
            archetypes[archetype_name].update(data)
            archetypes[archetype_name]['metadata'] = metadata
        else:
            archetypes[archetype_name].update(data)
        
        save_archetypes(archetypes)
        clear_caches()
        
        return jsonify(archetypes[archetype_name])
    except Exception as e:
        print(f"Error updating archetype: {str(e)}")  # Server-side logging
        return jsonify({"error": str(e)}), 500

@app.route('/api/profiles/<profile_name>', methods=['POST'])
def update_profile(profile_name):
    try:
        profiles = load_profiles()
        data = request.json
        
        # Update existing profile or create new one
        profiles[profile_name] = data
        
        # Save to file
        save_profiles(profiles)
        clear_caches()  # Clear cache to ensure fresh data on next load
        
        return jsonify(profiles[profile_name])
    except Exception as e:
        print(f"Error updating profile: {str(e)}")  # Server-side logging
        return jsonify({"error": str(e)}), 500

@app.route('/api/config')
def get_config():
    """Get full configuration including attributes and tooltips"""
    lang = request.args.get('lang', 'en')
    return jsonify({
        'attributes': load_attributes_config(),
        'tooltips': load_tooltips(lang)
    })

if __name__ == '__main__':
    app.run(debug=True)
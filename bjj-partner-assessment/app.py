# app.py
from flask import Flask, render_template, jsonify, request
import json
from functools import lru_cache
import os

app = Flask(__name__)

# Cache for profiles
@lru_cache()
def load_profiles():
    with open('profiles.json', 'r') as f:
        return json.load(f)

# Cache for archetypal profiles
@lru_cache()
def load_archetypal_profiles():
    with open('archetypal_profiles.json', 'r') as f:
        return json.load(f)

# Save profiles to JSON file
def save_profiles(profiles_data):
    with open('profiles.json', 'w') as f:
        json.dump(profiles_data, f, indent=4)

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

@app.route('/api/profiles/<profile_name>', methods=['POST'])
def update_profile(profile_name):
    profiles = load_profiles()
    if profile_name not in profiles:
        profiles[profile_name] = {}
    
    data = request.json
    profiles[profile_name].update(data)
    save_profiles(profiles)  # Save changes to file
    return jsonify(profiles[profile_name])

@app.route('/api/archetypes')
def get_archetypes():
    return jsonify(load_archetypal_profiles())

@app.route('/api/archetypes/<archetype_name>')
def get_specific_archetype(archetype_name):
    archetypes = load_archetypal_profiles()
    return jsonify(archetypes.get(archetype_name, {}))

if __name__ == '__main__':
    app.run(debug=True)
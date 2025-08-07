from flask import Flask, render_template, request, jsonify
import json
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

def load_embeddings(file_path):
    """Load your existing embeddings function"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    embeddings = data['embeddings']
    names = data['names']
    return embeddings, names

# Load embeddings and set up KNN
embeddings, names = load_embeddings("saved_embeddings/mtg_embeddings_20250728_153743.json")

knn = NearestNeighbors(n_neighbors=21)  # Increased to handle up to 20 recommendations
knn.fit(embeddings)

def get_recommendations(card_name, all_names, all_embeddings, knn_model, n=10):
    """Modified version of your recommendation function"""
    if card_name not in all_names:
        return None
        
    idx = all_names.index(card_name)
    distances, indices = knn_model.kneighbors([all_embeddings[idx]], n_neighbors=n+1)
    
    recommendations = []
    for i, idx in enumerate(indices[0][1:]):  # Skip the first one (the card itself)
        recommendations.append({
            'rank': i+1,
            'name': all_names[idx],
            'distance': float(distances[0][i+1])
        })
    
    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    """Return card names that match the search query"""
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])
    
    # Find cards that contain the search query
    matches = [name for name in names if query in name.lower()]
    # Limit to first 10 matches to avoid overwhelming the UI
    return jsonify(matches[:10])

@app.route('/recommendations')
def recommendations():
    """Get recommendations for a specific card"""
    card_name = request.args.get('card')
    num_recommendations = int(request.args.get('n', 10))  # Get number from slider
    
    if not card_name:
        return jsonify({'error': 'No card specified'})
    
    recs = get_recommendations(card_name, names, embeddings, knn, n=num_recommendations)
    
    if recs is None:
        return jsonify({'error': f"Card '{card_name}' not found in dataset."})
    
    return jsonify({
        'card': card_name,
        'recommendations': recs
    })

if __name__ == '__main__':
    app.run(debug=True)

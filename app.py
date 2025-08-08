from flask import Flask, render_template, request, jsonify
import json
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)

def load_embeddings(file_path):
    """Load embeddings, names, and images"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    embeddings = data['embeddings']
    names = data['names']
    imgs = data['imgs']  # Load images
    return embeddings, names, imgs

# Load embeddings and set up KNN
embeddings, names, imgs = load_embeddings("saved_embeddings/mtg_embeddings_20250808.json")

knn = NearestNeighbors(n_neighbors=51)  # handle up to 50 recommendations
knn.fit(embeddings)

def get_recommendations(card_name, all_names, all_embeddings, all_imgs, knn_model, n=10):
    """Get recommendations including image links"""
    if card_name not in all_names:
        return None

    idx = all_names.index(card_name)
    distances, indices = knn_model.kneighbors([all_embeddings[idx]], n_neighbors=n+1)

    recommendations = []
    for i, rec_idx in enumerate(indices[0][1:]):  # Skip the card itself
        recommendations.append({
            'rank': i + 1,
            'name': all_names[rec_idx],
            'img': all_imgs[rec_idx],
            'distance': float(distances[0][i+1])
        })

    return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    """Return card names matching the search query"""
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])

    matches = [name for name in names if query in name.lower()]
    return jsonify(matches[:10])

@app.route('/recommendations')
def recommendations():
    """Get recommendations for a card"""
    card_name = request.args.get('card')
    num_recommendations = int(request.args.get('n', 10))

    if not card_name:
        return jsonify({'error': 'No card specified'})

    recs = get_recommendations(card_name, names, embeddings, imgs, knn, n=num_recommendations)

    if recs is None:
        return jsonify({'error': f"Card '{card_name}' not found in dataset."})

    selected_img = imgs[names.index(card_name)]

    return jsonify({
        'card': card_name,
        'card_img': selected_img,
        'recommendations': recs
    })

if __name__ == '__main__':
    app.run(debug=True)

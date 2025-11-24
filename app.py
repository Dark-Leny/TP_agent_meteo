from flask import Flask, render_template, request, jsonify
from agent_meteo import AgentMeteo
import os

app = Flask(__name__)
agent = AgentMeteo()

# Compteur simple pour suivre l'usage (respect CNIL : pas de données personnelles)
stats = {'total_requetes': 0}

@app.route('/')
def index():
    """Page d'accueil avec bannière CNIL"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint principal du chatbot
    Respecte les principes CNIL :
    - Pas de stockage des conversations
    - Pas de cookies de tracking
    - Réponse immédiate sans historisation
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Traiter le message
        resultat = agent.traiter_message(message)
        
        # Statistiques anonymes (conforme CNIL)
        stats['total_requetes'] += 1
        
        return jsonify(resultat)
        
    except Exception as e:
        print(f"Erreur serveur : {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur serveur. Réessayez plus tard.'
        }), 500

@app.route('/stats')
def get_stats():
    """Statistiques anonymes (pas de données personnelles)"""
    return jsonify(stats)

if __name__ == '__main__':
    # Vérifier que les clés API sont configurées
    if not os.getenv('MISTRAL_API_KEY') or not os.getenv('OPENWEATHER_API_KEY'):
        print("⚠️  ERREUR : Clés API manquantes dans le fichier .env")
        print("📝 Copiez .env.example vers .env et ajoutez vos clés API")
        exit(1)
    
    print("✅ Agent conversationnel météo démarré")
    print("📍 URL : http://localhost:5000")
    print("🤖 Conforme aux recommandations CNIL")
    print()
    print("Pour obtenir vos clés API :")
    print("  - Mistral AI : https://console.mistral.ai/")
    print("  - OpenWeatherMap : https://openweathermap.org/api")
    
    app.run(debug=True, port=5000
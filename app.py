from flask import Flask, render_template, request, jsonify
from agent_meteo import AgentMeteo
import os
import sqlite3 # NOUVEAU : pour la base de données
from datetime import datetime # NOUVEAU : pour l'horodatage

app = Flask(__name__)
agent = AgentMeteo()

# Compteur simple pour suivre l'usage (respect CNIL : pas de données personnelles)
stats = {'total_requetes': 0}

# NOUVEAU : Configuration de la base de données SQLite
DATABASE = 'conversations.db'

def init_db():
    """Initialise la base de données pour l'enregistrement opt-in des conversations."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horodatage TEXT NOT NULL,
            message_utilisateur TEXT NOT NULL,
            reponse_agent TEXT,
            ville_traitee TEXT
        );
    """)
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Page d'accueil avec bannière CNIL"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint principal du chatbot.
    Gère l'historique de session et l'enregistrement opt-in (consentement).
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        historique_session = data.get('historique', []) # NOUVEAU
        consentement = data.get('consentement', False) # NOUVEAU
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Traiter le message, en passant l'historique
        # L'historique n'est utilisé que pour le contexte de la réponse (non stocké par Flask)
        resultat = agent.traiter_message(message, historique=historique_session)
        
        # NOUVEAU : Enregistrement conditionnel avec consentement
        if consentement and resultat.get('success'):
            try:
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (horodatage, message_utilisateur, reponse_agent, ville_traitee)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    message,
                    resultat.get('message', 'N/A'),
                    resultat.get('data', {}).get('ville', 'N/A')
                ))
                conn.commit()
                conn.close()
            except Exception as db_e:
                print(f"⚠️ Erreur d'enregistrement DB : {db_e}")
        
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
    
    # Initialisation de la base de données
    init_db() # NOUVEAU
    
    print("✅ Agent conversationnel météo démarré")
    # ... (messages de console inchangés) ...
    
    app.run(debug=True, port=5000)
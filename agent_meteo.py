import os
import requests
from mistralai import Mistral
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class AgentMeteo:
    """
    Agent conversationnel météo conforme aux recommandations CNIL :
    - Transparence : l'utilisateur sait qu'il parle à un robot
    - Limitation des données : on ne collecte que la ville
    - Sécurité : clés API dans variables d'environnement
    """
    
    def __init__(self):
        self.mistral_client = Mistral(api_key=os.getenv('MISTRAL_API_KEY'))
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.model = "mistral-small-latest"  # Modèle gratuit et rapide
        
        # Contexte système pour guider l'agent
        self.system_prompt = """Tu es un assistant météo sympathique et concis.
        
IMPORTANT - Règles CNIL :
- Tu DOIS te présenter comme un agent conversationnel automatique
- Tu dois informer l'utilisateur que ses données ne sont pas stockées
- Tu dois limiter la collecte de données au strict nécessaire (ville uniquement)

Ton rôle :
1. Extraire le nom de la ville de la question de l'utilisateur
2. Si pas de ville mentionnée, demander poliment la ville
3. Répondre de manière naturelle et conversationnelle
4. Ne jamais inventer de données météo

Format de réponse :
- Si ville trouvée : réponds en JSON {"ville": "nom_ville"}
- Si pas de ville : réponds en JSON {"action": "demander_ville", "message": "ton message"}
"""
    
    def extraire_ville(self, message_utilisateur):
        """
        Utilise Mistral AI pour extraire le nom de la ville
        Respecte le RGPD : traite uniquement l'information nécessaire
        """
        try:
            response = self.mistral_client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": message_utilisateur}
                ],
                temperature=0.3,  # Faible température pour plus de cohérence
                response_format={"type": "json_object"}
            )
            
            import json
            resultat = json.loads(response.choices[0].message.content)
            return resultat
            
        except Exception as e:
            print(f"Erreur Mistral AI : {e}")
            return {"action": "erreur", "message": "Désolé, je n'ai pas compris. Quelle ville vous intéresse ?"}
    
    def obtenir_meteo(self, ville):
        """
        Récupère les données météo depuis OpenWeatherMap
        Principe de minimisation : on récupère uniquement les données nécessaires
        """
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': ville,
                'appid': self.weather_api_key,
                'units': 'metric',  # Celsius
                'lang': 'fr'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # Extraction des données pertinentes uniquement
            meteo = {
                'ville': data['name'],
                'temperature': round(data['main']['temp'], 1),
                'ressenti': round(data['main']['feels_like'], 1),
                'description': data['weather'][0]['description'],
                'humidite': data['main']['humidity'],
                'vent': round(data['wind']['speed'] * 3.6, 1)  # m/s -> km/h
            }
            
            return meteo
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None  # Ville non trouvée
            raise
        except Exception as e:
            print(f"Erreur API météo : {e}")
            raise
    
    def generer_reponse(self, meteo_data):
        """
        Utilise Mistral pour générer une réponse naturelle
        """
        try:
            prompt = f"""Génère une réponse courte et sympathique (2-3 phrases max) pour ces données météo :
            
Ville : {meteo_data['ville']}
Température : {meteo_data['temperature']}°C (ressenti {meteo_data['ressenti']}°C)
Conditions : {meteo_data['description']}
Humidité : {meteo_data['humidite']}%
Vent : {meteo_data['vent']} km/h

Conseils :
- Sois naturel et conversationnel
- Donne un conseil pratique (vêtements, parapluie, etc.)
- Reste concis"""

            response = self.mistral_client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erreur génération réponse : {e}")
            # Fallback sur une réponse simple si Mistral échoue
            return f"À {meteo_data['ville']}, il fait {meteo_data['temperature']}°C avec {meteo_data['description']}."
    
    def traiter_message(self, message_utilisateur):
        """
        Point d'entrée principal : traite le message de l'utilisateur
        """
        # Étape 1 : Extraire la ville avec Mistral
        resultat = self.extraire_ville(message_utilisateur)
        
        # Cas 1 : Mistral demande plus d'informations
        if resultat.get('action') == 'demander_ville':
            return {
                'success': False,
                'message': resultat['message']
            }
        
        # Cas 2 : Ville extraite
        if 'ville' in resultat:
            ville = resultat['ville']
            
            # Étape 2 : Récupérer la météo
            try:
                meteo_data = self.obtenir_meteo(ville)
                
                if meteo_data is None:
                    return {
                        'success': False,
                        'message': f"Désolé, je ne trouve pas la ville '{ville}'. Peux-tu vérifier l'orthographe ?"
                    }
                
                # Étape 3 : Générer une réponse naturelle avec Mistral
                reponse = self.generer_reponse(meteo_data)
                
                return {
                    'success': True,
                    'message': reponse,
                    'data': meteo_data
                }
                
            except Exception as e:
                return {
                    'success': False,
                    'message': "Désolé, je rencontre un problème technique. Réessaye dans un instant."
                }
        
        # Cas 3 : Erreur ou cas non géré
        return {
            'success': False,
            'message': "Je n'ai pas compris. Peux-tu me donner le nom d'une ville ?"
        }


# Test rapide
if __name__ == "__main__":
    agent = AgentMeteo()
    
    # Test 1
    print("Test 1 : Quel temps fait-il à Paris ?")
    resultat = agent.traiter_message("Quel temps fait-il à Paris ?")
    print(resultat)
    print()
    
    # Test 2
    print("Test 2 : Météo Lyon")
    resultat = agent.traiter_message("Météo Lyon")
    print(resultat)
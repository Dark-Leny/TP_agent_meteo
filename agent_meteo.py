import os
import requests
from mistralai import Mistral
from dotenv import load_dotenv
import json # Assurez-vous que json est importé

# Charger les variables d'environnement
load_dotenv()

class AgentMeteo:
    """
    Agent conversationnel météo conforme aux recommandations CNIL.
    """
    
    def __init__(self):
        self.mistral_client = Mistral(api_key=os.getenv('MISTRAL_API_KEY'))
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.model = "mistral-small-latest"
        
        # MODIFICATION : Demander la langue en plus de la ville
        self.system_prompt = """Tu es un assistant météo sympathique et concis.
        
IMPORTANT - Règles CNIL :
- Tu DOIS te présenter comme un agent conversationnel automatique
- Tu dois informer l'utilisateur que ses données ne sont pas stockées (sauf opt-in)
- Tu dois limiter la collecte de données au strict nécessaire (ville uniquement)

Ton rôle :
1. Extraire le nom de la ville de la question de l'utilisateur.
2. Si pas de ville mentionnée, demander poliment la ville.
3. Détecter la langue de l'utilisateur (BCP-47, ex: 'fr', 'en', 'es').
4. Répondre de manière naturelle et conversationnelle.
5. Ne jamais inventer de données météo.

Format de réponse :
- Si ville trouvée : réponds en JSON {"ville": "nom_ville", "langue": "fr"}
- Si pas de ville : réponds en JSON {"action": "demander_ville", "message": "ton message", "langue": "fr"}
"""
    
    # MODIFICATION : Ajout du paramètre historique
    def extraire_ville(self, message_utilisateur, historique=[]):
        """
        Utilise Mistral AI pour extraire le nom de la ville et la langue.
        Utilise l'historique pour maintenir le contexte.
        """
        try:
            # Construction des messages avec l'historique de session
            messages_a_envoyer = [{"role": "system", "content": self.system_prompt}]
            
            # Ajout de l'historique de session (pour le contexte)
            for msg in historique:
                # S'assurer que les messages de l'historique sont au bon format
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages_a_envoyer.append(msg)
                
            messages_a_envoyer.append({"role": "user", "content": message_utilisateur})
            
            response = self.mistral_client.chat.complete(
                model=self.model,
                messages=messages_a_envoyer, # Utilisation de l'historique
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            resultat = json.loads(response.choices[0].message.content)
            # S'assurer qu'une langue est toujours présente
            if 'langue' not in resultat:
                 resultat['langue'] = 'fr' 
            return resultat
            
        except Exception as e:
            print(f"Erreur Mistral AI : {e}")
            return {"action": "erreur", "message": "Désolé, je n'ai pas compris. Quelle ville vous intéresse ?", "langue": "fr"}
    
    # MODIFICATION : Ajout du paramètre langue
    def obtenir_meteo(self, ville, langue='fr'):
        """
        Récupère les données météo actuelles depuis OpenWeatherMap.
        """
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': ville,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': langue # Utilisation de la langue détectée
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            # ... (Extraction des données pertinentes inchangée) ...
            meteo = {
                'ville': data['name'],
                'temperature': round(data['main']['temp'], 1),
                'ressenti': round(data['main']['feels_like'], 1),
                'description': data['weather'][0]['description'],
                'humidite': data['main']['humidity'],
                'vent': round(data['wind']['speed'] * 3.6, 1) # m/s -> km/h
            }
            
            return meteo
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            print(f"Erreur API météo : {e}")
            raise
            
    # NOUVELLE MÉTHODE : Prévisions sur 5 jours
    def obtenir_previsions_5j(self, ville, langue='fr'):
        """
        Récupère les prévisions sur 5 jours (par jour) depuis OpenWeatherMap.
        """
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': ville,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': langue # Utilisation de la langue détectée
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            previsions = {}
            for item in data['list']:
                # On ne prend qu'une seule lecture par jour (autour de midi)
                date_txt = item['dt_txt'].split(' ')[0]
                heure = item['dt_txt'].split(' ')[1][:2]

                if heure in ['12', '13', '14'] and date_txt not in previsions:
                    previsions[date_txt] = {
                        'date': date_txt,
                        'temperature': round(item['main']['temp'], 1),
                        'description': item['weather'][0]['description'],
                        'icone': item['weather'][0]['icon']
                    }
            
            return sorted(list(previsions.values()), key=lambda x: x['date'])
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            print(f"Erreur API prévisions : {e}")
            return [] # Retourne une liste vide en cas d'erreur
            
    # MODIFICATION : Ajout du paramètre previsions_data
    def generer_reponse(self, meteo_data, previsions_data=None):
        """
        Utilise Mistral pour générer une réponse naturelle, incluant les prévisions.
        """
        forecast_str = ""
        if previsions_data:
            jours = [f"Le {p['date'][5:]}: {p['temperature']}°C avec {p['description']}" for p in previsions_data[:3]]
            forecast_str = "\nPrévisions (3 jours) : " + " | ".join(jours)

        prompt = f"""Génère une réponse courte et sympathique (2-3 phrases max) pour ces données météo. Utilise la langue française, quelle que soit la ville.
            
Ville : {meteo_data['ville']}
Température actuelle : {meteo_data['temperature']}°C (ressenti {meteo_data['ressenti']}°C)
Conditions : {meteo_data['description']}
Humidité : {meteo_data['humidite']}%
Vent : {meteo_data['vent']} km/h
{forecast_str}

Conseils :
- Sois naturel et conversationnel
- Donne un conseil pratique (vêtements, parapluie, etc.) en te basant sur la météo actuelle et les prévisions.
- Reste concis"""

        try:
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
            return f"À {meteo_data['ville']}, il fait {meteo_data['temperature']}°C avec {meteo_data['description']}."
    
    # MODIFICATION : Ajout des paramètres historique, consentement et langue
    def traiter_message(self, message_utilisateur, historique=[], consentement=False):
        """
        Point d'entrée principal : traite le message de l'utilisateur.
        """
        # Étape 1 : Extraire la ville et la langue avec Mistral
        resultat = self.extraire_ville(message_utilisateur, historique)
        langue = resultat.get('langue', 'fr')
        
        # Cas 1 : Mistral demande plus d'informations
        if resultat.get('action') == 'demander_ville':
            return {
                'success': False,
                'message': resultat['message'],
                'langue': langue # Retourne la langue pour l'UI
            }
        
        # Cas 2 : Ville extraite
        if 'ville' in resultat:
            ville = resultat['ville']
            
            # Étape 2 : Récupérer la météo et les prévisions
            try:
                meteo_data = self.obtenir_meteo(ville, langue) # Utilise la langue
                previsions_data = self.obtenir_previsions_5j(ville, langue) # Utilise la langue
                
                if meteo_data is None:
                    return {
                        'success': False,
                        'message': f"Désolé, je ne trouve pas la ville '{ville}'. Peux-tu vérifier l'orthographe ?",
                        'langue': langue
                    }
                
                # Étape 3 : Générer une réponse naturelle avec Mistral
                reponse = self.generer_reponse(meteo_data, previsions_data)
                
                return {
                    'success': True,
                    'message': reponse,
                    'data': meteo_data,
                    'forecast': previsions_data, # NOUVEAU
                    'langue': langue
                }
                
            except Exception as e:
                # Affichage de l'erreur dans la console pour le debug
                print(f"Erreur dans l'étape météo/prévisions: {e}")
                return {
                    'success': False,
                    'message': "Désolé, je rencontre un problème technique. Réessaye dans un instant.",
                    'langue': langue
                }
        
        # Cas 3 : Erreur ou cas non géré
        return {
            'success': False,
            'message': "Je n'ai pas compris. Peux-tu me donner le nom d'une ville ?",
            'langue': langue
        }
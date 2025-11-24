# TP_agent_meteo

# 📚 Documentation Technique du Projet : Agent Météo Intelligent

## 📝 Vue d'ensemble du Projet

Le projet **TP\_agent\_meteo** est une application web de type **chatbot** construite avec le framework **Flask** en Python. Son objectif est de fournir des informations météorologiques en utilisant un modèle d'Intelligence Artificielle (**Mistral AI**) pour le traitement du langage naturel (NLP) et l'API **OpenWeatherMap** pour les données météo.

Ce projet met l'accent sur la **conformité aux recommandations CNIL** (Commission Nationale de l'Informatique et des Libertés).

---

## 🚀 Installation et Configuration

### 1. Prérequis

* **Python 3.x**
* Clés API pour :
    * **Mistral AI** (à obtenir sur `https://console.mistral.ai/`)
    * **OpenWeatherMap** (à obtenir sur `https://openweathermap.org/api`)

### 2. Clés API et Variables d'Environnement

Le projet utilise le fichier **`.env`** (qui ne doit pas être versionné) pour stocker les clés secrètes.

Créez un fichier nommé `.env` à la racine de votre projet et ajoutez vos clés :

```
MISTRAL_API_KEY="VOTRE_CLE_MISTRAL_ICI"
OPENWEATHER_API_KEY="VOTRE_CLE_OPENWEATHER_ICI"
```

### 3. Installation des Dépendances

Il est fortement recommandé d'utiliser un environnement virtuel.

1) Créez et activez l'environnement virtuel (si ce n'est pas déjà fait) :

```
python -m venv venv
source venv/bin/activate  # Sur Linux/macOS
# ou venv\Scripts\activate  # Sur Windows
```

2) Installez les dépendances : Les modules requis sont Flask, requests, mistralai, et python-dotenv.

```
pip install Flask requests mistralai python-dotenv
```

Si jamais ça ne fonctionne pas, faites les une par une : 

```
pip install Flask
pip install requests
pip install mistralai
pip install python-dotenv
```

### 4. Démarrage de l'Application

Le serveur de développement Flask est démarré via le script app.py :

```
python app.py
```

Si la configuration est correcte, l'application démarre sur http://localhost:5000.
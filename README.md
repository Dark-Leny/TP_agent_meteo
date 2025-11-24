# TP_agent_meteo

# 📚 Documentation Technique du Projet : Agent Météo Intelligent

## 📝 Vue d'ensemble du Projet

Le projet **TP\_agent\_meteo** est une application web de type **chatbot** construite avec le framework **Flask** en Python. Son objectif est de fournir des informations météorologiques en utilisant un modèle d'Intelligence Artificielle (**Mistral AI**) pour le traitement du langage naturel (NLP) et l'API **OpenWeatherMap** pour les données météo.

Ce projet met l'accent sur la **conformité aux recommandations CNIL** (Commission Nationale de l'Informatique et des Libertés).

---

## 🚀 Installation et Configuration

### 1. Prérequis

* **Python 3.8 ou supérieur installé**
* Connaissances de base en Python
* Notions de requêtes HTTP (API REST)
* Clés API pour :
    * **Compte gratuit Mistral AI** (à obtenir sur `https://console.mistral.ai/`)
    * **Compte gratuit OpenWeatherMap** (à obtenir sur `https://openweathermap.org/api`)

Pour obtenir les clés API : 

### Clé Mistral AI (gratuite)
1. Créer un compte sur https://console.mistral.ai/
2. Aller dans "API Keys"
3. Créer une nouvelle clé
4. Crédit gratuit : 5€ offerts à l'inscription (suffisant pour le TP)

### Clé OpenWeatherMap (gratuite)
1. Créer un compte sur https://openweathermap.org/
2. Aller dans "API Keys"
3. Copier la clé par défaut
4. Plan gratuit : 1000 appels/jour


### Structure du projet
tp_meteo_mistral/
│
├── .env                    # Clés API (à ne JAMAIS commiter)
├── .gitignore              # Ignorer .env et autres fichiers sensibles
├── app.py                  # Application Flask
├── agent_meteo.py          # Logique de l'agent conversationnel
├── templates/
│ └── index.html            # Interface web
├── static/
│ └── style.css             # Style CSS
└── README.md               # Documentation



### 2. Clés API et Variables d'Environnement

Le projet utilise le fichier **`.env`** (qui ne doit pas être versionné) pour stocker les clés secrètes.

Créez un fichier nommé `.env` à la racine de votre projet et ajoutez vos clés :

```
MISTRAL_API_KEY="VOTRE_CLE_MISTRAL_ICI"
OPENWEATHER_API_KEY="VOTRE_CLE_OPENWEATHER_ICI"
```

Créez un fichier nommé `.gitignore` également à la racine de votre projet et ajouter ceci : 

```
# Environnement virtuel
venv/
env/
ENV/
.venv

# Variables d'environnement (IMPORTANT)
.env

# Cache Python
__pycache__/
*.pyc
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```


### 3. Installation des Dépendances

Il est fortement recommandé d'utiliser un environnement virtuel.

1) Créez et activez l'environnement virtuel (si ce n'est pas déjà fait) :

```
python -m venv venv
source venv/bin/activate  # Sur Linux/macOS
venv\Scripts\activate  # Sur Windows
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
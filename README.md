# 🤖 Refactoring Swarm (Equipe Refacta)

Un système multi-agents autonome capable d'analyser, de refactoriser et de valider du code legacy automatiquement.

## 🏗️ Architecture du Système

Ce projet respecte l'architecture en **Boucle de Self-Healing** :

1.  **👁️ Auditor Agent (L'Auditeur) :** Analyse le code source via Gemini pour détecter bugs et violations PEP8.
2.  **🛠️ Fixer Agent (Le Correcteur) :** Propose une correction et réécrit le fichier.
3.  **⚖️ Judge Agent (Le Juge) :** Compile le code (Analyse Statique).
    * ✅ **Succès :** Le code est validé.
    * ❌ **Échec :** Le code est renvoyé au *Fixer Agent* avec les logs d'erreur (Max 3 essais).
4.  **📊 Data Officer :** Enregistre chaque interaction dans `logs/experiment_data.json`.

## 🚀 Installation

1. Cloner le dépôt :
   ```bash
   git clone [https://github.com/ashrafkrk/Refactoring-Swarm-Equipe-Refacta.git](https://github.com/ashrafkrk/Refactoring-Swarm-Equipe-Refacta.git)
   cd Refactoring-Swarm-Equipe-Refacta

2. Créer l'environnement virtuel et installer les dépendances :
    python -m venv venv
    # Windows
    .\venv\Scripts\activate

    # Linux/Mac
    source venv/bin/activate
    pip install -r requirements.txt

3. Configurer l'API Key : Créez un fichier .env à la racine :   
    GOOGLE_API_KEY=votre_cle_gemini_ici

    
## 🚀 Utilisation
Pour lancer la refactorisation sur un dossier cible :

python main.py --target_dir ./sandbox/votre_dossier

## Structure du Projet
src/agents/ : Logique des agents.

src/tools/ : Outils système (Lecture fichiers, Analyse syntaxique).

src/utils/ : Logger centralisé.

logs/ : Historique des expériences (JSON).

sandbox/ : Zone de test sécurisée.

Projet réalisé dans le cadre du module IGL 2025-2026.
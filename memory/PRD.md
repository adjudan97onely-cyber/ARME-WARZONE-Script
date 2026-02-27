# ZEN HUB PRO - Product Requirements Document

## Original Problem Statement
Créer une application complète de génération de scripts Cronus Zen pour Warzone, inspirée des scripts de Gamertag B07, avec:
- Base de données d'armes complète (comme l'app Warzone Meta)
- Possibilité d'ajouter/mettre à jour les armes
- IA experte pour générer des scripts et suggérer des builds "méta cachés"
- Générateur de Master Script avec auto-détection ADT
- Support OLED pour Cronus Zen

## User Personas
- **Gamers Warzone**: Utilisateurs de Cronus Zen cherchant des scripts anti-recoil optimisés
- **Script Creators**: Personnes voulant créer leurs propres configurations d'armes
- **Meta Hunters**: Joueurs recherchant les builds "cachés" à haut DPS

## Core Requirements (Static)
1. Base de données d'armes MW3/BO6 avec statistiques de recul
2. CRUD complet sur les armes (ajouter, modifier, supprimer)
3. IA Experte intégrée (Gemini 3 Flash) pour génération de scripts
4. Master Script Generator avec ADT et support OLED
5. Coffre-Fort pour sauvegarder les scripts générés
6. Interface tactique/militaire sombre

## Architecture
- **Frontend**: React.js avec Tailwind CSS (thème tactique)
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI**: Gemini 3 Flash via emergentintegrations

## What's Been Implemented ✅ (2026-02-27)
- [x] Dashboard avec statistiques (armes, scripts, méta)
- [x] Meta Center avec 31+ armes pré-chargées (MW3/BO6)
- [x] Filtres par catégorie (AR, SMG, LMG, SNIPER, SHOTGUN, PISTOL) et jeu
- [x] Formulaire d'ajout/modification d'armes complet
- [x] Tags META et HIDDEN META pour les armes
- [x] Builds recommandés et notes par arme
- [x] IA Experte avec chat (Gemini 3 Flash)
- [x] Génération de scripts GPC personnalisés
- [x] Master Script Generator avec ADT auto-détection
- [x] Support OLED dans les scripts générés
- [x] Coffre-Fort (Scripts Vault) avec vue/copie/téléchargement
- [x] Interface style tactique/militaire (Orbitron, Rajdhani, JetBrains Mono)

## Test Results
- Backend: 100% (21/21 tests passed)
- Frontend: 95% (minor modal issue only)

## Prioritized Backlog
### P0 (Critical) - DONE
- [x] Core weapon database
- [x] Master Script generation
- [x] AI integration

### P1 (Important) - Future
- [ ] Import/Export de bases de données d'armes
- [ ] Synchronisation avec les mises à jour Warzone
- [ ] Profils utilisateur multiples

### P2 (Nice to have)
- [ ] Statistiques d'utilisation par arme
- [ ] Mode comparaison d'armes
- [ ] Intégration directe Cronus Zen Studio

## Next Tasks
1. Ajouter nouvelles armes au fur et à mesure des mises à jour Warzone
2. Améliorer l'IA avec des prompts plus spécifiques par catégorie d'arme
3. Ajouter un mode "Build Calculator" pour simuler le DPS

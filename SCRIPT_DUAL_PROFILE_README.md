# 🎮 ZEN HUB PRO - SCRIPT FINAL (AS VAL + WSP SWARM)

## ✅ **EXACTEMENT CE QUE VOUS VOULIEZ**

Script SIMPLE avec 2 profils fixes basés sur les recommandations de l'IA Experte :

### 🔫 **Profil Primaire : AS VAL**
- **V_Recoil** : 28
- **H_Recoil** : 18
- Valeurs optimisées par IA Experte

### 🔫 **Profil Secondaire : WSP SWARM**
- **V_Recoil** : 22
- **H_Recoil** : 20
- Valeurs optimisées par IA Experte

---

## 🎮 **CONTRÔLES**

### Changement de Profil
- **TRIANGLE** : Changer entre AS VAL et WSP SWARM
- **LED clignote** pour confirmer
- **OLED affiche** : Nom de l'arme + Valeurs

### Settings
- **PAD + DOWN** : Menu Settings (Normal/Tactique)

### Mods (Toujours Actifs)
- **Tirer sans viser** : Jump Shot
- **Sprint + Crouch** : Slide Cancel
- **Avancer** : Auto Sprint automatique

---

## 📋 **COMMENT UTILISER**

### 1. Avant de Jouer
**Sélectionnez votre loadout dans Warzone :**
- **Primaire** : AS VAL (construisez selon les recommandations IA)
- **Secondaire** : WSP SWARM (construisez selon les recommandations IA)

### 2. Pendant la Partie
**Profil par défaut :** AS VAL (Primaire)

**Quand vous utilisez AS VAL :**
- Ne faites rien, le script applique 28v/18h automatiquement
- Tirez → Anti-recul optimisé

**Quand vous passez à WSP SWARM :**
1. **Changez d'arme dans le jeu** (votre touche habituelle)
2. **Appuyez sur TRIANGLE** sur la manette
3. Le script passe à WSP (22v/20h)
4. LED clignote pour confirmer

**Quand vous repassez à AS VAL :**
1. **Changez d'arme dans le jeu**
2. **Appuyez sur TRIANGLE**
3. Le script passe à AS VAL (28v/18h)

---

## 💡 **AVANTAGES**

✅ **Simple** : Pas d'ADT compliqué  
✅ **2 profils fixes** : AS VAL + WSP SWARM  
✅ **TRIANGLE** : Facile à utiliser  
✅ **Valeurs optimisées** : Recommandations IA Experte  
✅ **Tous les mods** : Jump Shot + Slide Cancel + Auto Sprint  
✅ **Pas de LEFT/RIGHT** : Pas chiant à gérer  

---

## 📦 **GÉNÉRATION DU SCRIPT**

### Sur Zen Hub Pro

Il y a maintenant **3 options** :

1. **"Générer Master Script"** → Script v2 stable (anti-recul universel 10v)
2. **"Générer ULTIMATE Script"** → Master ADT v6.0 (20 armes, LEFT/RIGHT)
3. **"Générer AS VAL + WSP Script"** → 🆕 **CELUI-CI ! (2 profils, TRIANGLE)**

### Via API
```bash
curl -X POST https://projet-studio.preview.emergentagent.com/api/generate-dual-profile-script
```

---

## 🎯 **EN RÉSUMÉ**

**Votre workflow :**
1. **Loadout Warzone** : AS VAL (Primaire) + WSP SWARM (Secondaire)
2. **Script Zen** : Profil AS VAL par défaut
3. **En jeu** :
   - Jouez avec AS VAL → Rien à faire
   - Passez à WSP → TRIANGLE
   - Repassez à AS VAL → TRIANGLE

**C'est tout ! Simple et efficace.** 🚀

---

## ⚙️ **MODIFICATION MANUELLE (Si besoin)**

**Ouvrez le .gpc dans Zen Studio :**

**Ligne ~20-25 :**
```gpc
// Valeurs de recul optimisées (IA Experte)
int asval_v = 28;  // ← Changez si besoin
int asval_h = 18;  // ← Changez si besoin
int wsp_v = 22;    // ← Changez si besoin
int wsp_h = 20;    // ← Changez si besoin
```

---

## 🧪 **TESTEZ MAINTENANT !**

1. **Générez le script** sur Zen Hub Pro (option "AS VAL + WSP")
2. **Téléchargez** depuis le Coffre-Fort
3. **Compilez** dans Zen Studio
4. **Testez in-game** :
   - AS VAL → Recul 28v/18h
   - TRIANGLE → Passage à WSP → Recul 22v/20h
   - TRIANGLE → Retour à AS VAL → Recul 28v/18h

**Dites-moi si ça compile et si ça fonctionne bien ! 🎮**

# 🎮 ZEN HUB PRO - SCRIPT ULTIMATE (Master ADT v6.0)

## ✅ **CE QUI A ÉTÉ FAIT**

J'ai créé le **SCRIPT ULTIMATE** en fusionnant :
1. ✅ Votre script stable (Jump Shot + Slide Cancel + Auto Sprint)
2. ✅ Les recommandations de l'IA Experte (Master ADT v6.0 + valeurs optimisées)

---

## 🎯 **FONCTIONNALITÉS DU SCRIPT ULTIMATE**

### 🆕 **Master ADT v6.0 - Sélection Rapide d'Arme**

**Navigation avec LEFT/RIGHT :**
- **LEFT** : Arme précédente
- **RIGHT** : Arme suivante
- **Notification LED** quand vous changez d'arme
- **Affichage OLED** : Nom de l'arme + valeurs de recul

**20 Armes Pré-configurées :**
1. **AS VAL** → V:28 H:18
2. **WSP SWARM** → V:22 H:20
3. **SVA 546** → V:26 H:18
4. **M4** → V:24 H:18
5. **KILO 141** → V:26 H:18
6. **MK2B** → V:30 H:20
7. **TANTO 22** → V:16 H:18
8. **MCW LMG** → V:28 H:18
9. **JACKAL PDW** → V:20 H:18
10. **MCW AR** → V:24 H:18
11. **HOLGER 556** → V:20 H:7
12. **STRIKER** → V:16 H:18
13. **HRM-9** → V:20 H:12
14. **BAS-P** → V:20 H:16
15. **AMES 85** → V:26 H:18
16. **GROZA-MMAX** → V:26 H:18
17. **SAUG** → V:16 H:12
18. **ABR A1** → V:28 H:12
19. **MCB** → V:24 H:7
20. **STB44** → V:24 H:18

---

### ✅ **Mods de Combat (Conservés)**

1. **Jump Shot** (maintenu) - Saute en tirant sans viser
2. **Slide Cancel** (350ms) - Annule le slide avec un saut
3. **Auto Sprint** - Sprint automatique en avançant

---

### 🎯 **Master Recoil (Nouveau)**

**Fonction `smart_family()` :**
- Limite intelligente du recul (-102 à +102)
- Empêche les overcorrections

**Combo `MasterRecoil` :**
- Applique les valeurs optimisées de l'arme sélectionnée
- Utilise V_Recoil et H_Recoil de l'arme active

**Combo `SVA_Hyper` :**
- Compensation spéciale pour SVA 546 (index 3)
- Burst stabilisation

---

## 🎮 **CONTRÔLES**

### Navigation
- **LEFT** : Arme précédente (1-20)
- **RIGHT** : Arme suivante (1-20)
- **PAD + DOWN** : Menu Settings (Normal/Tactique)

### Mods
- **Tire sans viser (R2 seul)** : Jump Shot
- **Sprint + Crouch** : Slide Cancel
- **Avancer (joystick)** : Auto Sprint
- **Viser + Tirer** : Master Recoil actif

---

## 📝 **COMMENT UTILISER**

### 1. Générer le Script ULTIMATE

**Sur Zen Hub Pro :**
1. Allez sur l'application
2. **NOUVEAU** : Endpoint `/api/generate-ultimate-script`
3. Le script `ZEN_ULTIMATE_ADT_YYYYMMDD_HHMM.gpc` sera créé

**OU via API directement :**
```bash
curl -X POST https://projet-studio.preview.emergentagent.com/api/generate-ultimate-script
```

---

### 2. Utiliser en Jeu

**Avant la partie :**
1. **LEFT/RIGHT** pour sélectionner votre arme (ex: AS VAL = Index 1)
2. **OLED affiche** : "AS VAL" + "V:28 H:18"
3. **LED clignote** pour confirmer

**Pendant la partie :**
- **Tirez** : Master Recoil s'active automatiquement avec les valeurs optimisées
- **Jump Shot** : Tirez sans viser pour sauter
- **Slide Cancel** : Sprint + Crouch pour annuler le slide

**Changer d'arme en jeu :**
- **LEFT/RIGHT** pour naviguer vers une autre arme (ex: WSP SWARM = Index 2)
- Le recul s'adapte automatiquement !

---

## 🔧 **DIFFÉRENCES AVEC L'ANCIEN SCRIPT**

| Fonctionnalité | Ancien Script | Script ULTIMATE |
|----------------|---------------|-----------------|
| Sélection d'arme | Menu PAD+R2 (lent) | **LEFT/RIGHT (rapide)** ✅ |
| Valeurs de recul | Universelles (10v/0h) | **Optimisées par arme** ✅ |
| Armes préconfigurées | 0 | **20 armes META** ✅ |
| Master Recoil | Anti-recul basique | **smart_family() + combos** ✅ |
| SVA Hyper | Non | **Burst stabilisation** ✅ |
| Notification | Non | **LED + OLED** ✅ |

---

## ⚙️ **MODIFICATION MANUELLE**

Si vous voulez ajuster les valeurs dans Zen Studio :

**Ligne ~30-35 :**
```gpc
int Weapon_Index = 1;  // Arme au démarrage (1-20)
int V_Recoil = 28;     // Valeur par défaut
int H_Recoil = 18;
```

**Pour changer les valeurs d'une arme spécifique :**
Trouvez les lignes dans le `main` (environ ligne 150-170) :
```gpc
if(Weapon_Index == 1) { V_Recoil = 28; H_Recoil = 18; } // AS VAL
```
Modifiez les valeurs selon vos besoins.

---

## 🚀 **PROCHAINES ÉTAPES**

1. **Générez le script ULTIMATE** sur Zen Hub Pro
2. **Téléchargez-le** depuis le Coffre-Fort
3. **Compilez dans Zen Studio**
4. **Testez avec AS VAL ou WSP SWARM**
5. **Utilisez LEFT/RIGHT** pour changer d'arme rapidement

---

## ❓ **IMPORTANT**

**Ce script remplace-t-il l'ancien ?**
- NON ! Les deux co-existent
- Ancien endpoint : `/api/generate-master-script` (script stable v2)
- Nouveau endpoint : `/api/generate-ultimate-script` (Master ADT v6.0)

**Lequel utiliser ?**
- **Script v2** (stable) : Si vous voulez simple et fiable
- **Script ULTIMATE** : Si vous voulez AS VAL/WSP optimisés + sélection rapide

---

## ✅ **RÉSUMÉ**

**Vous avez maintenant le SCRIPT ULTIME qui combine :**
- ✅ Jump Shot + Slide Cancel + Auto Sprint
- ✅ Master ADT v6.0 (sélection LEFT/RIGHT)
- ✅ 20 armes avec valeurs optimisées par l'IA Experte
- ✅ AS VAL (28v/18h) et WSP SWARM (22v/20h) parfaitement calibrés
- ✅ Combo MasterRecoil + SVA_Hyper
- ✅ Notification LED + Affichage OLED

**COMPILEZ ET TESTEZ ! 🎯**

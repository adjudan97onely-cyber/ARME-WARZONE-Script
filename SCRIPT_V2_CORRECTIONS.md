# 🎮 ZEN HUB PRO - Script v2 (Corrections Utilisateur)

## ✅ Modifications Apportées

### 1. 🎯 Anti-Recul Réduit
**Avant** : 25 vertical → Trop fort, descendait aux pieds
**Maintenant** : **10 vertical** → Plus subtil et contrôlable

```gpc
int anti_recul_universel_v = 10;  // Réduit de 25 à 10
int anti_recul_universel_h = 0;
```

---

### 2. 🎯 Jump Shot Amélioré
**Avant** : Sautait dès qu'on appuyait sur R2 (event_press)
**Maintenant** : Saute SEULEMENT quand on **MAINTIENT R2** (get_val)

**Comment ça marche maintenant :**
1. Visez + Tirez (L2 + R2 maintenus)
2. **Arrêtez de viser** (relâchez L2)
3. **Continuez à tirer** (maintenez R2)
4. → Vous sautez !
5. **Reprenez la visée** (L2)
6. → Vous arrêtez de sauter

```gpc
// Avant
if(event_press(tire) && !get_val(vise)) {
    combo_run(JumpShot);
}

// Maintenant
if(get_val(tire) && !get_val(vise)) {
    combo_run(JumpShot);
}
```

---

### 3. 🆕 Auto Sprint Ajouté
**Nouveau mod** : Le personnage sprinte automatiquement quand vous poussez le joystick vers l'avant !

**Comment ça marche :**
- Poussez le joystick gauche vers l'avant (> 80%)
- → Le personnage sprinte automatiquement
- Plus besoin d'appuyer sur L3 !

```gpc
int autosprint_actif = TRUE;
int as_sprint_threshold = 80;  // Seuil de détection (80%)

// Logic
if(autosprint_actif) {
    if(abs(get_val(PS4_LY)) > as_sprint_threshold && get_val(PS4_LY) < 0) {
        set_val(sprint, 100);
    }
}
```

**Avantage :** Plus facile de faire un Slide Cancel !
- Poussez vers l'avant → Sprint auto
- Appuyez sur Crouch → Slide Cancel

---

### 4. ✅ Slide Cancel
**Status** : Fonctionne bien (aucun changement)

---

## 📋 Résumé du Script v2

**Nom** : `ZEN_COMPLETE_MODS_v2_...`

**Fonctionnalités** :
✅ **Jump Shot** (maintenu) - Saute quand on tire sans viser (R2 maintenu)
✅ **Slide Cancel** - Annule le slide avec un saut (350ms)
✅ **Auto Sprint** 🆕 - Sprint automatique en poussant le joystick
✅ **Anti-Recul Universel** - 10 vertical (réduit de 25)

**Armes** : 53

---

## 🧪 À Tester Maintenant

### 1. Anti-Recul
- Est-ce que **10 vertical** est mieux ?
- Trop fort / Trop faible / Parfait ?
- Si besoin, on peut ajuster à 8, 12, 15, etc.

### 2. Jump Shot (maintenu)
- Tirez en visant
- Arrêtez de viser (relâchez L2)
- Continuez à tirer (maintenez R2)
- → Vous devez sauter en boucle
- Reprenez la visée → Vous arrêtez de sauter

### 3. Auto Sprint
- Poussez le joystick vers l'avant
- → Le personnage doit sprinter automatiquement
- Plus facile pour faire Slide Cancel ?

---

## ⚙️ Réglages Ajustables

Si besoin d'ajuster après vos tests :

**Anti-Recul** (actuellement 10)
- Trop fort → Réduire à 8
- Trop faible → Augmenter à 12-15

**Auto Sprint Threshold** (actuellement 80%)
- Sprinte trop facilement → Augmenter à 90%
- Sprinte pas assez → Réduire à 70%

**Slide Cancel Delay** (actuellement 350ms)
- Trop lent → Réduire à 300ms
- Trop rapide → Augmenter à 400ms

---

## 🚀 Prochaines Étapes

**Après vos tests in-game :**

1. **Si tout fonctionne bien** ✅
   - Je lance l'import des **~200 armes** de wzstats.gg
   - Vous redéployez avec toutes les armes

2. **Si besoin d'ajustements** ⚙️
   - Dites-moi ce qui ne va pas
   - Je corrige immédiatement

---

## 📦 Comment Tester

1. **Générez le nouveau script** sur Zen Hub Pro
2. **Téléchargez** depuis le Coffre-Fort
3. **Compilez** dans Zen Studio
4. **Testez in-game** :
   - Anti-Recul (mieux ?)
   - Jump Shot (maintenu fonctionne ?)
   - Auto Sprint (sprinte automatiquement ?)
   - Slide Cancel (toujours bon ?)

**Bon test ! 🎮**

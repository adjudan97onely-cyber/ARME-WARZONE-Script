# 🎮 ZEN HUB PRO - Script Complet avec Tous les Mods

## ✅ Fonctionnalités Implémentées

### 🎯 1. Jump Shot (Mode Fire No ADS)
**Comment ça marche :**
- Saute automatiquement quand vous **tirez SANS viser**
- Parfait pour : Viser → Tirer → Arrêter de viser → Continuer à tirer → Il saute

**Variables :**
```gpc
int jumpshot_actif = TRUE;
```

---

### 🎯 2. Drop Shot (Mode Panic - ADS & Fire)
**Comment ça marche :**
- Se couche automatiquement quand vous **visez ET tirez en même temps** (dans les 120ms)
- Se relève automatiquement quand vous **arrêtez de tirer** (mode Sprint Fast)
- Parfait pour les engagements agressifs

**Variables :**
```gpc
int dropshot_actif = TRUE;
int ds_did_dropshot = FALSE;
int ds_press_variance_time = 120;
```

**Combos :**
```gpc
combo DropShot {
    set_val(accroupi, 100);
    wait(100);
    set_val(accroupi, 100);
    wait(100);
    set_val(accroupi, 100);
    wait(50);
}

combo StandUp {
    set_val(sprint, 100);
    wait(50);
    set_val(sprint, 0);
}
```

---

### 🎯 3. Slide Cancel (Mode Jump - MWIII/Warzone)
**Comment ça marche :**
- Annule automatiquement le slide après 350ms
- Saute immédiatement pour enchaîner l'action
- Active quand vous **sprintez + appuyez sur crouch**

**Variables :**
```gpc
int slidecancel_actif = TRUE;
int sc_cancel_delay_time = 350;
```

**Combo :**
```gpc
combo SlideCancel {
    wait(350);
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}
```

---

### 🎯 4. Anti-Recul Universel
**Comment ça marche :**
- Anti-recul baseline pour **TOUTES les armes** : **25 vertical, 0 horizontal**
- Si vous réglez manuellement une arme (PAD+L2), utilise votre réglage personnalisé
- Sinon, applique l'anti-recul universel

**Variables :**
```gpc
int anti_recul_actif = TRUE;
int anti_recul_universel_v = 25;
int anti_recul_universel_h = 0;
```

---

## 📋 Contrôles

### Menus
- **PAD + R2** : Sélection d'arme
- **PAD + L2** : Réglage anti-recul personnalisé
- **PAD + DOWN** : Settings (mode Normal/Tactique)
- **TRIANGLE** : Changer de profil (Primaire/Secondaire)

### Modes
- **Mode Normal** : Crouch sur ROND, Melee sur R3
- **Mode Tactique** : Crouch sur R3, Melee sur ROND

---

## 🎮 Comment Utiliser les Mods

### Jump Shot
1. **NE VISEZ PAS** (ne maintenez pas L2)
2. **Tirez** (R2)
3. → Le personnage saute automatiquement

### Drop Shot
1. **Visez** (L2) **ET** **Tirez** (R2) **en même temps** (< 120ms d'écart)
2. → Le personnage se couche automatiquement
3. Continuez à tirer couché
4. **Relâchez R2** → Le personnage se relève automatiquement

### Slide Cancel
1. **Sprintez** (maintenez L3)
2. **Appuyez sur Crouch** (ROND ou R3 selon votre mode)
3. → Le slide s'annule automatiquement après 350ms et vous sautez

---

## 📦 Nom du Script

**Format :** `ZEN_COMPLETE_MODS_YYYYMMDD_HHMM.gpc`

**Exemple :** `ZEN_COMPLETE_MODS_20260301_1805.gpc`

---

## 🧪 Test In-Game

**À tester :**

1. **Jump Shot** : Tirez sans viser → Vous devez sauter
2. **Drop Shot** : Visez + Tirez ensemble → Vous devez vous coucher puis vous relever en relâchant R2
3. **Slide Cancel** : Sprint + Crouch → Le slide doit s'annuler rapidement avec un saut
4. **Anti-Recul** : Testez avec n'importe quelle arme → Devrait être stable (baseline 25v/0h)

---

## ⚙️ Réglages Avancés

### Ajuster l'Anti-Recul par Arme
1. **PAD + R2** : Sélectionnez votre arme
2. **PAD + L2** : Ajustez l'anti-recul vertical/horizontal
3. → Vos réglages personnalisés seront sauvegardés et utilisés à la place de l'anti-recul universel

### Variables Modifiables (dans le code si besoin)

**Jump Shot :**
- `jumpshot_actif = TRUE/FALSE` : Activer/Désactiver

**Drop Shot :**
- `dropshot_actif = TRUE/FALSE` : Activer/Désactiver
- `ds_press_variance_time = 120` : Temps max (ms) entre ADS et Fire pour déclencher

**Slide Cancel :**
- `slidecancel_actif = TRUE/FALSE` : Activer/Désactiver
- `sc_cancel_delay_time = 350` : Délai (ms) avant annulation du slide

**Anti-Recul :**
- `anti_recul_universel_v = 25` : Valeur verticale (0-99)
- `anti_recul_universel_h = 0` : Valeur horizontale (-99 à 99)

---

## 🐛 Dépannage

### Jump Shot ne fonctionne pas
- Vérifiez que vous **NE visez PAS** (L2 relâché)
- Le mod est actif par défaut (`jumpshot_actif = TRUE`)

### Drop Shot ne se déclenche pas
- Visez et tirez **presque en même temps** (< 120ms d'écart)
- Si trop lent, essayez d'augmenter `ds_press_variance_time` dans le code

### Slide Cancel trop rapide/lent
- Ajustez `sc_cancel_delay_time` (350ms par défaut)
- Plus bas = plus rapide, plus haut = plus lent

### Anti-Recul trop fort/faible
- Ouvrez le menu avec **PAD + L2**
- Ajustez manuellement pour chaque arme
- Ou modifiez `anti_recul_universel_v` dans le code

---

## 📊 Statistiques

- **53 armes** dans la base de données
- **4 mods actifs** : Jump Shot, Drop Shot, Slide Cancel, Anti-Recul Universel
- **3 combos** : JumpShot, DropShot + StandUp, SlideCancel
- **Script size** : ~25,000 caractères
- **Compilation** : ✅ Confirmé fonctionnel

---

## 🚀 Prochaines Étapes

Après test in-game, si tout fonctionne bien :

**Option A** : Affiner les réglages (timings, valeurs)
**Option B** : Ajouter d'autres mods (Rapid Fire, Auto Sprint, etc.)
**Option C** : Améliorer l'interface (menu OLED pour activer/désactiver les mods)

**Dites-moi ce qui fonctionne et ce qui ne fonctionne pas après vos tests in-game ! 🎮**

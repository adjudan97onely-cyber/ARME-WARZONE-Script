# 🎮 ZEN HUB PRO - Script Jump Shot + Anti-Recul Universel

## ✅ Ce qui a été implémenté

### 1. 🎯 Jump Shot (Mode Fire No ADS)
**Fonctionnement :**
- Le personnage **saute automatiquement** quand vous **tirez SANS viser**
- Vous pouvez viser, tirer, puis arrêter de viser et continuer à tirer → le personnage sautera
- Vous gardez le contrôle total du timing du saut

**Activation dans le code :**
```gpc
// JUMP SHOT - Active quand on tire SANS viser
if(jumpshot_actif && !menu_selection_actif && !menu_ar_actif && !menu_settings_actif) {
    if(event_press(tire) && !get_val(vise)) {
        combo_run(JumpShot);
    }
}

combo JumpShot {
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}
```

**Variable :** `jumpshot_actif = TRUE` (activé par défaut)

---

### 2. 🎯 Anti-Recul Universel
**Fonctionnement :**
- Un réglage d'anti-recul qui fonctionne avec **TOUTES les armes**
- Valeur par défaut : **25 vertical, 0 horizontal**
- Si vous réglez manuellement l'anti-recul d'une arme (via PAD+L2), il utilisera votre réglage personnalisé
- Sinon, il utilise l'anti-recul universel

**Logique dans le code :**
```gpc
// Anti-recul personnalise (reglages manuels)
if(arv[index] != 0 || arh[index] != 0) {
    set_val(PS4_RY, get_val(PS4_RY) + (arv[index] * 2));
    set_val(PS4_RX, get_val(PS4_RX) + arh[index]);
}
// Anti-recul universel (si pas de reglages manuels)
else if(anti_recul_actif) {
    set_val(PS4_RY, get_val(PS4_RY) + (anti_recul_universel_v * 2));
    set_val(PS4_RX, get_val(PS4_RX) + anti_recul_universel_h);
}
```

**Variables :**
- `anti_recul_actif = TRUE` (activé par défaut)
- `anti_recul_universel_v = 25` (vertical)
- `anti_recul_universel_h = 0` (horizontal)

---

## 📋 Contrôles du Script

### Menu Principal
- **PAD + R2** : Menu sélection d'arme
- **PAD + L2** : Menu réglage anti-recul (personnalisé par arme)
- **PAD + DOWN** : Menu Settings (mode Normal/Tactique)
- **TRIANGLE** : Changer de profil (Primaire/Secondaire)

### Modes de Contrôle
- **Mode Normal** : Crouch sur ROND, Melee sur R3
- **Mode Tactique** : Crouch sur R3, Melee sur ROND

---

## 🔄 Prochaines Étapes

**Vous m'avez demandé d'implémenter ensuite :**
1. **Drop Shot** - Se coucher automatiquement en tirant
2. **Slide Cancel** - Annuler le slide rapidement

**Important :** Je vais implémenter UNE fonctionnalité à la fois, générer le script, et vous me confirmez qu'il compile avant de passer à la suivante.

---

## 📦 Comment tester ce script

1. Allez sur l'interface Zen Hub Pro
2. Cliquez sur "Générer Master Script"
3. Le script `ZEN_JUMPSHOT_ANTIRECUL_YYYYMMDD_HHMM.gpc` sera généré
4. Téléchargez-le depuis le "Coffre-Fort"
5. Importez-le dans Zen Studio
6. **COMPILEZ-LE et dites-moi si ça marche !**

---

## 🐛 Si ça ne compile pas

**Envoyez-moi l'erreur de compilation exacte** et je corrigerai immédiatement.

---

## ✅ Avantages de cette approche

✓ **Pas d'ADT compliqué** → moins de risques d'erreurs
✓ **Anti-recul universel** → fonctionne avec toutes les armes
✓ **Réglages personnalisés possibles** → si vous voulez ajuster une arme spécifique
✓ **Jump Shot simple** → mode "Fire No ADS" comme vous l'avez demandé
✓ **Structure stable** → basée sur le générateur qui compile déjà

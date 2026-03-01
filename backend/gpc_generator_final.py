"""
ZEN HUB PRO - Générateur GPC FINAL
Structure basée sur gamertag.gpc (PROUVÉ FONCTIONNEL)
Priorité : COMPILATION RÉUSSIE
"""

from typing import List, Dict
from datetime import datetime, timezone

def generate_master_script_advanced(weapons: List[Dict]) -> str:
    """
    Génère un script GPC basé sur la structure EXACTE de gamertag.gpc
    Version minimaliste d'abord : juste anti-recoil + navigation d'armes
    """
    
    weapon_count = len(weapons)
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # ============================================================
    # EN-TÊTE - Format identique à gamertag.gpc
    # ============================================================
    script = f'''// ===================================================================
// ZEN HUB PRO - MASTER SCRIPT WARZONE
// Generated: {generation_time}
// Total Weapons: {weapon_count}
// Platform: PlayStation 5
// ===================================================================
//
// CONTROLES:
// - PAD + R2 = Menu selection arme
// - PAD + L2 = Menu reglage anti-recul
// - TRIANGLE = Changer de profil (primaire/secondaire)
//
// ===================================================================

'''
    
    # ============================================================
    # DÉCLARATIONS DE VARIABLES - Format gamertag.gpc
    # ============================================================
    script += '''int vise = PS4_L2;
int tire = PS4_R2;
int accroupi = PS4_R3;
int saut = PS4_CROSS;
int recharge = PS4_SQUARE;
int sprint = PS4_L3;
int melee = PS4_CIRCLE;

// Settings - Mode de controle
int control_mode = 0;  // 0 = Normal, 1 = Tactique
int menu_settings_actif = FALSE;
int settings_index = 0;

// Mods de combat
int jumpshot_actif = TRUE;
int dropshot_actif = TRUE;
int slidecancel_actif = TRUE;
int anti_recul_actif = TRUE;
int anti_recul_universel_v = 25;
int anti_recul_universel_h = 0;

// Drop Shot settings
int ds_did_dropshot = FALSE;
int ds_press_variance_time = 120;

// Slide Cancel settings
int sc_cancel_delay_time = 350;

int current_profil = 0;
int arme_profil_prim = 0;
int arme_profil_sec = 0;
int index_selection = 0;
int menu_selection_actif = FALSE;
int menu_ar_actif = FALSE;
int mode_ar = 0;
int index = 0;
int update = TRUE;

'''
    
    # ============================================================
    # ARRAYS DE NOMS D'ARMES - Généré depuis la DB
    # ============================================================
    weapon_names = []
    weapon_name_lengths = []
    
    for w in weapons:
        name = w.get('name', 'Unknown')
        weapon_names.append(name)
        weapon_name_lengths.append(len(name))
    
    # Générer le tableau const string
    script += 'const string noms_armes[] = {\n'
    for i, name in enumerate(weapon_names):
        script += f'    "{name}"'
        if i < len(weapon_names) - 1:
            script += ','
        script += '\n'
    script += '};\n\n'
    
    # Générer le tableau des longueurs
    script += 'const int noms_armesVALEUR[] = {'
    script += ', '.join(str(length) for length in weapon_name_lengths)
    script += '};\n\n'
    
    # Labels fixes
    script += '''const string label_primaire[] = { "PRIMARY" };
const string label_secondaire[] = { "SECONDARY" };
const string label_choix_arme[] = { "LIST" };
const string vertical[] = { "VERTICAL" };
const string horizontal[] = { "HORIZONTAL" };
const string label_save[] = { "SAUVEGARDE" };
const string label_ok[] = { "OK" };
const string en[] = { "EN:" };
const string indic[] = { "PAD+L2 - PAD+R2" };
const string settings_title[] = { "SETTINGS" };
const string mode_normal[] = { "MODE: NORMAL" };
const string mode_tactique[] = { "MODE: TACTIQUE" };

'''
    
    # ============================================================
    # ARRAYS ANTI-RECOIL - Format compatible spvar
    # ============================================================
    script += f'''// Anti-recul vertical et horizontal pour chaque arme
int arv[{weapon_count}];
int arh[{weapon_count}];

'''
    
    # ============================================================
    # FONCTIONS D'AFFICHAGE OLED - Format gamertag.gpc
    # ============================================================
    script += '''// ===================================================================
// FONCTIONS D'AFFICHAGE OLED
// ===================================================================

function afficher_profils() {
    cls_oled(0);
    rect_oled(0, 0, 124, 64, OLED_BLACK, OLED_WHITE);
    rect_oled(0, 0, 124, 25, OLED_BLACK, OLED_WHITE);
    rect_oled(0, 0, 124, 48, OLED_BLACK, OLED_WHITE);
    if(current_profil == 0) {
        print(23, 4, OLED_FONT_MEDIUM, OLED_WHITE, label_primaire[0]);
        print(centre_x(noms_armesVALEUR[arme_profil_prim], OLED_FONT_SMALL_WIDTH), 32, 0, OLED_WHITE, noms_armes[arme_profil_prim]);
        print(10, 52, 0, OLED_WHITE, indic[0]);
    } else {
        print(13, 4, OLED_FONT_MEDIUM, OLED_WHITE, label_secondaire[0]);
        print(centre_x(noms_armesVALEUR[arme_profil_sec], OLED_FONT_SMALL_WIDTH), 32, 0, OLED_WHITE, noms_armes[arme_profil_sec]);
        print(10, 52, 0, OLED_WHITE, indic[0]);
    }
}

function afficher_menu_selection() {
    cls_oled(0);
    rect_oled(0, 0, 124, 64, OLED_BLACK, OLED_WHITE);
    rect_oled(0, 0, 124, 25, OLED_BLACK, OLED_WHITE);
    print(43, 4, OLED_FONT_MEDIUM, OLED_WHITE, label_choix_arme[0]);
    print(2, 32, OLED_FONT_SMALL, OLED_WHITE, en[0]);
    print(22, 32, OLED_FONT_SMALL, OLED_WHITE, noms_armes[index_selection]);
}

function afficher_menu_antirecul() {
    cls_oled(0);
    rect_oled(0, 0, 124, 64, OLED_BLACK, OLED_WHITE);
    rect_oled(0, 0, 124, 25, OLED_BLACK, OLED_WHITE);
    rect_oled(0, 0, 124, 43, OLED_BLACK, OLED_WHITE);
    
    if(current_profil == 0) index = arme_profil_prim;
    else index = arme_profil_sec;
    
    print(centre_x(noms_armesVALEUR[index], OLED_FONT_SMALL_WIDTH), 30, 0, OLED_WHITE, noms_armes[index]);
    
    if(mode_ar == 0) {
        print(21, 4, OLED_FONT_MEDIUM, OLED_WHITE, vertical[0]);
        print_number(arv[index], 2, centre_x(2, OLED_FONT_MEDIUM_WIDTH), 45, 1);
    } else {
        print(13, 4, OLED_FONT_MEDIUM, OLED_WHITE, horizontal[0]);
        print_number(arh[index], 2, centre_x(2, OLED_FONT_MEDIUM_WIDTH), 45, 1);
    }
}

function afficher_menu_settings() {
    cls_oled(0);
    rect_oled(0, 0, 124, 64, OLED_BLACK, OLED_WHITE);
    rect_oled(0, 0, 124, 25, OLED_BLACK, OLED_WHITE);
    
    print(10, 4, OLED_FONT_MEDIUM, OLED_WHITE, settings_title[0]);
    
    if(control_mode == 0) {
        print(5, 35, OLED_FONT_SMALL, OLED_WHITE, mode_normal[0]);
    } else {
        print(2, 35, OLED_FONT_SMALL, OLED_WHITE, mode_tactique[0]);
    }
}

function centre_x(int nb_caracteres, int largeur_caractere) {
    return (128 / 2) - ((nb_caracteres * largeur_caractere) / 2);
}

'''
    
    # ============================================================
    # BLOC INIT - Format gamertag.gpc
    # ============================================================
    script += '''// ===================================================================
// INITIALISATION
// ===================================================================

init {
    Load();
    
    // Appliquer le mapping des touches selon le mode
    if(control_mode == 1) {
        // Mode Tactique
        accroupi = PS4_R3;      // Crouch sur R3 (pour slide cancel)
        saut = PS4_CROSS;       // Jump sur X
        melee = PS4_CIRCLE;     // Melee sur Rond
    } else {
        // Mode Normal
        accroupi = PS4_CIRCLE;  // Crouch sur Rond
        saut = PS4_CROSS;       // Jump sur X
        melee = PS4_R3;         // Melee sur R3
    }
}

'''
    
    # ============================================================
    # BLOC MAIN - Structure gamertag.gpc
    # ============================================================
    script += f'''// ===================================================================
// BOUCLE PRINCIPALE
// ===================================================================

main {{
    if(update) {{
        afficher_profils();
        update = FALSE;
    }}
    
    // Changer de profil avec TRIANGLE
    if(event_press(PS4_TRIANGLE)) {{
        if(current_profil == 0) current_profil = 1;
        else current_profil = 0;
        update = TRUE;
    }}
    
    // BLOCAGE DES TOUCHES DANS LES MENUS
    if(menu_selection_actif || menu_ar_actif || menu_settings_actif) {{
        block_all_inputs();
    }}
    
    // JUMP SHOT - Active quand on tire SANS viser
    if(jumpshot_actif && !menu_selection_actif && !menu_ar_actif && !menu_settings_actif) {{
        if(event_press(tire) && !get_val(vise)) {{
            combo_run(JumpShot);
        }}
    }}
    
    // DROP SHOT - Se coucher en mode Panic (ADS & FIRE)
    if(dropshot_actif && !menu_selection_actif && !menu_ar_actif && !menu_settings_actif) {{
        if(get_val(vise) && get_val(tire) && !ds_did_dropshot) {{
            if(abs(get_ptime(vise) - get_ptime(tire)) < ds_press_variance_time) {{
                combo_run(DropShot);
                ds_did_dropshot = TRUE;
            }}
        }}
        // Se relever quand on arrete de tirer
        if(ds_did_dropshot && event_release(tire)) {{
            combo_run(StandUp);
            ds_did_dropshot = FALSE;
        }}
    }}
    
    // SLIDE CANCEL - Annulation rapide du slide avec saut
    if(slidecancel_actif && !menu_selection_actif && !menu_ar_actif && !menu_settings_actif) {{
        if(get_val(sprint) && event_press(accroupi)) {{
            combo_run(SlideCancel);
        }}
    }}
    
    // PAD + DOWN ouvre le menu Settings
    if(get_val(PS4_TOUCH) && event_press(PS4_DOWN)) {{
        menu_settings_actif = TRUE;
        afficher_menu_settings();
    }}
    
    if(menu_settings_actif) {{
        // LEFT/RIGHT pour changer de mode
        if(event_press(PS4_LEFT) || event_press(PS4_RIGHT)) {{
            if(control_mode == 0) {{
                control_mode = 1;  // Passer en Tactique
                accroupi = PS4_R3;
                melee = PS4_CIRCLE;
            }} else {{
                control_mode = 0;  // Passer en Normal
                accroupi = PS4_CIRCLE;
                melee = PS4_R3;
            }}
            afficher_menu_settings();
        }}
        
        // CROIX pour sauvegarder et sortir
        if(event_press(PS4_CROSS)) {{
            menu_settings_actif = FALSE;
            update = TRUE;
            Save();
            combo_run(screen_save);
        }}
        
        // ROND pour annuler
        if(event_press(PS4_CIRCLE)) {{
            menu_settings_actif = FALSE;
            update = TRUE;
        }}
    }}
    
    // PAD + R2 ouvre le menu de selection d'arme
    if(get_val(PS4_TOUCH) && event_press(PS4_R2)) {{
        menu_selection_actif = TRUE;
        if(current_profil == 0) {{
            index_selection = arme_profil_prim;
        }} else {{
            index_selection = arme_profil_sec;
        }}
        afficher_menu_selection();
    }}
    
    if(menu_selection_actif) {{
        if(event_press(PS4_RIGHT)) {{
            if(index_selection < {weapon_count - 1}) {{
                index_selection++;
            }}
            afficher_menu_selection();
        }}
        
        if(event_press(PS4_LEFT)) {{
            if(index_selection > 0) {{
                index_selection--;
            }}
            afficher_menu_selection();
        }}
        
        // Valider avec CROIX
        if(event_press(PS4_CROSS)) {{
            if(current_profil == 0) arme_profil_prim = index_selection;
            else arme_profil_sec = index_selection;
            menu_selection_actif = FALSE;
            update = TRUE;
            Save();
            combo_run(screen_save);
        }}
        
        // Annuler avec ROND
        if(event_press(PS4_CIRCLE)) {{
            menu_selection_actif = FALSE;
            update = TRUE;
        }}
    }}
    
    // PAD + L2 ouvre le menu de reglage anti-recul
    if(get_val(PS4_TOUCH) && event_press(PS4_L2)) {{
        if(current_profil == 0) index = arme_profil_prim;
        else index = arme_profil_sec;
        menu_ar_actif = TRUE;
        mode_ar = 0;
        afficher_menu_antirecul();
    }}
    
    if(menu_ar_actif) {{
        if(event_press(PS4_LEFT) || event_press(PS4_RIGHT)) {{
            if(mode_ar == 0) mode_ar = 1;
            else mode_ar = 0;
            afficher_menu_antirecul();
        }}
        
        if(event_press(PS4_UP)) {{
            if(mode_ar == 0 && arv[index] < 99) arv[index]++;
            if(mode_ar == 1 && arh[index] < 99) arh[index]++;
            afficher_menu_antirecul();
        }}
        
        if(event_press(PS4_DOWN)) {{
            if(mode_ar == 0 && arv[index] > -99) arv[index]--;
            if(mode_ar == 1 && arh[index] > -99) arh[index]--;
            afficher_menu_antirecul();
        }}
        
        if(event_press(PS4_CIRCLE)) {{
            menu_ar_actif = FALSE;
            update = TRUE;
            Save();
            combo_run(screen_save);
        }}
    }}
    
    // ANTI-RECOIL APPLICATION
    if(!menu_selection_actif && !menu_ar_actif) {{
        if(get_val(vise) && get_val(tire)) {{
            if(current_profil == 0) index = arme_profil_prim;
            else index = arme_profil_sec;
            
            // Anti-recul personnalise (reglages manuels)
            if(arv[index] != 0 || arh[index] != 0) {{
                set_val(PS4_RY, get_val(PS4_RY) + (arv[index] * 2));
                set_val(PS4_RX, get_val(PS4_RX) + arh[index]);
            }}
            // Anti-recul universel (si pas de reglages manuels)
            else if(anti_recul_actif) {{
                set_val(PS4_RY, get_val(PS4_RY) + (anti_recul_universel_v * 2));
                set_val(PS4_RX, get_val(PS4_RX) + anti_recul_universel_h);
            }}
        }}
    }}
}}

'''
    
    # ============================================================
    # COMBOS - Format gamertag.gpc
    # ============================================================
    script += '''// ===================================================================
// COMBOS
// ===================================================================

combo JumpShot {
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}

combo screen_save {
    cls_oled(0);
    print(10, 20, OLED_FONT_MEDIUM, OLED_WHITE, label_save[0]);
    print(52, 40, OLED_FONT_MEDIUM, OLED_WHITE, label_ok[0]);
    wait(600);
    cls_oled(0);
    update = TRUE;
}

'''
    
    # ============================================================
    # FONCTIONS UTILITAIRES - Format gamertag.gpc
    # ============================================================
    script += '''// ===================================================================
// FONCTIONS UTILITAIRES
// ===================================================================

int n_str_;
int c_val;
int c_c_c;
const int ASCII_NUM[] = {
    48, 49, 50, 51, 52, 53, 54, 55, 56, 57
};

function print_number(int f_val, int f_digits, int print_s_x, int print_s_y, int f_font) {
    n_str_ = 1;
    c_val = 10000;
    
    if (f_val < 0) {
        putc_oled(n_str_, 45);
        n_str_ += 1;
        f_val = abs(f_val);
    }
    
    for (c_c_c = 5; c_c_c >= 1; c_c_c--) {
        if (f_digits >= c_c_c) {
            putc_oled(n_str_, ASCII_NUM[f_val / c_val]);
            f_val = f_val % c_val;
            n_str_ += 1;
        }
        c_val /= 10;
    }
    
    puts_oled(print_s_x, print_s_y, f_font, n_str_ - 1, OLED_WHITE);
}

'''
    
    # ============================================================
    # FONCTIONS SAVE/LOAD - Format gamertag.gpc avec spvar
    # ============================================================
    script += f'''// ===================================================================
// PERSISTANCE (SAVE/LOAD)
// ===================================================================

function Save() {{
    reset_spvar();
    save_spvar(1, 0, 1);
    save_spvar(arme_profil_prim, 0, {weapon_count - 1});
    save_spvar(arme_profil_sec, 0, {weapon_count - 1});
    save_spvar(control_mode, 0, 1);  // Sauvegarder le mode de controle
    
'''
    
    # Save tous les arv et arh
    for i in range(weapon_count):
        script += f'    save_spvar(arv[{i}], -99, 99);\n'
    for i in range(weapon_count):
        script += f'    save_spvar(arh[{i}], -99, 99);\n'
    
    script += '''}

function Load() {
    reset_spvar();
    
    if (read_spvar(0, 1, 1)) {
'''
    
    script += f'''        arme_profil_prim = read_spvar(0, {weapon_count - 1}, 0);
        arme_profil_sec = read_spvar(0, {weapon_count - 1}, 0);
        control_mode = read_spvar(0, 1, 0);
        
'''
    
    for i in range(weapon_count):
        script += f'        arv[{i}] = read_spvar(-99, 99, 0);\n'
    for i in range(weapon_count):
        script += f'        arh[{i}] = read_spvar(-99, 99, 0);\n'
    
    script += '''    } else {
        arme_profil_prim = 0;
        arme_profil_sec = 0;
        control_mode = 0;
    }
}

'''
    
    # ============================================================
    # SYSTÈME SPVAR - Copié EXACTEMENT de gamertag.gpc
    # ============================================================
    script += '''// ===================================================================
// SYSTEME SPVAR (NE PAS MODIFIER)
// ===================================================================

int spvar_current_bit, spvar_current_slot, spvar_current_value, spvar_tmp, spvar_bits;

function reset_spvar() {
    spvar_current_slot = SPVAR_1;
    spvar_current_bit = 0;
    spvar_current_value = 0;
}

function get_bit_count(val) {
    spvar_tmp = 0;
    while (val) {
        spvar_tmp++;
        val = abs(val >> 1);
    }
    return spvar_tmp;
}

function get_bit_count2(val1, val2) {
    spvar_tmp = max(get_bit_count(val1), get_bit_count(val2));
    if (val1 < 0 || val2 < 0) spvar_tmp++;
    return spvar_tmp;
}

function is_signed2(val1, val2) { return val1 < 0 || val2 < 0; }
function make_sign(bits) { return 1 << clamp(bits - 1, 0, 31); }
function make_full_mask(bits) { if (bits == 32) return -1; return 0x7FFFFFFF >> (31 - bits); }
function make_sign_mask(bits) { return make_full_mask(bits - 1); }

function pack_i(val, bits) {
    if (val < 0) return (abs(val) & make_sign_mask(bits)) | make_sign(bits);
    return val & make_sign_mask(bits);
}

function unpack_i(val, bits) {
    if (val & make_sign(bits)) return 0 - (val & make_sign_mask(bits));
    return val & make_sign_mask(bits);
}

function read_spvar_slot(slot) { return get_pvar(slot, 0x80000000, 0x7FFFFFFF, 0); }

function save_spvar(val, min, max) {
    spvar_bits = get_bit_count2(min, max);
    val = clamp(val, min, max);
    if (is_signed2(min, max)) val = pack_i(val, spvar_bits);
    val = val & make_full_mask(spvar_bits);

    if (spvar_bits >= 32 - spvar_current_bit) {
        spvar_current_value = spvar_current_value | (val << spvar_current_bit);
        set_pvar(spvar_current_slot, spvar_current_value);
        spvar_current_slot++;
        spvar_bits -= (32 - spvar_current_bit);
        val = val >> (32 - spvar_current_bit);
        spvar_current_bit = 0;
        spvar_current_value = 0;
    }

    spvar_current_value = spvar_current_value | (val << spvar_current_bit);
    spvar_current_bit += spvar_bits;
    if (!spvar_current_bit) spvar_current_value = 0;

    set_pvar(spvar_current_slot, spvar_current_value);
}

function read_spvar(min, max, def) {
    spvar_bits = get_bit_count2(min, max);
    spvar_current_value = (read_spvar_slot(spvar_current_slot) >> spvar_current_bit) & make_full_mask(spvar_bits);

    if (spvar_bits >= 32 - spvar_current_bit) {
        spvar_current_value = (spvar_current_value & make_full_mask(32 - spvar_current_bit)) |
                              ((read_spvar_slot(spvar_current_slot + 1) & make_full_mask(spvar_bits - (32 - spvar_current_bit))) << (32 - spvar_current_bit));
    }

    spvar_current_bit += spvar_bits;
    spvar_current_value = spvar_current_value & make_full_mask(spvar_bits);
    if (spvar_current_bit >= 32) {
        spvar_current_slot++;
        spvar_current_bit -= 32;
    }

    if (is_signed2(min, max)) spvar_current_value = unpack_i(spvar_current_value, spvar_bits);
    if (spvar_current_value < min || spvar_current_value > max) return def;
    return spvar_current_value;
}
'''
    
    return script

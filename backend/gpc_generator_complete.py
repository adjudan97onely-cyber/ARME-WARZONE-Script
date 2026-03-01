"""
ZEN HUB PRO - Générateur GPC COMPLET v2.0
Structure basée sur gamertag.gpc + Features avancées
- ADT (Auto Detection Technology)
- 10 Mods Warzone
- Menu OLED complet
- 53 armes
"""

from typing import List, Dict
from datetime import datetime, timezone

def generate_master_script_advanced(weapons: List[Dict]) -> str:
    """
    Génère un script GPC COMPLET avec toutes les features
    Basé sur la structure prouvée de gamertag.gpc
    """
    
    weapon_count = len(weapons)
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # ============================================================
    # EN-TÊTE
    # ============================================================
    script = f'''// ===================================================================
// ZEN HUB PRO - MASTER SCRIPT WARZONE COMPLETE
// Generated: {generation_time}
// Total Weapons: {weapon_count}
// Platform: PlayStation 5
// ===================================================================
//
// CONTROLES:
// - PAD + R2 = Menu selection arme
// - PAD + L2 = Menu reglage anti-recul  
// - PAD + TRIANGLE = Menu activation mods
// - TRIANGLE = Changer de profil (primaire/secondaire)
//
// MODS INCLUS:
// - Anti-Recoil (toujours actif par defaut)
// - Rapid Fire (armes compatibles)
// - Aim Assist
// - Slide Cancel
// - Auto Sprint
// - Drop Shot
// - Bunny Hop
// - Jitter
// - Sniper Breath Hold
// - Quick Reload
//
// ADT: Detection automatique d'arme basee sur fire rate
//
// ===================================================================

'''
    
    # ============================================================
    # DÉCLARATIONS DE VARIABLES
    # ============================================================
    script += '''int vise = PS4_L2;
int tire = PS4_R2;
int accroupi = PS4_R3;
int saut = PS4_CROSS;
int recharge = PS4_SQUARE;
int sprint = PS4_L3;

int current_profil = 0;
int arme_profil_prim = 0;
int arme_profil_sec = 0;
int index_selection = 0;
int menu_selection_actif = FALSE;
int menu_ar_actif = FALSE;
int menu_mods_actif = FALSE;
int mode_ar = 0;
int index = 0;
int update = TRUE;

// ADT Variables
int adt_enabled = TRUE;
int last_shot_time = 0;
int shot_count = 0;
int total_delay = 0;
int detected_fire_rate = 0;
int is_sniper = FALSE;

// Mods States (10 mods)
int mod_antirecul = TRUE;
int mod_rapid_fire = FALSE;
int mod_aim_assist = FALSE;
int mod_slide_cancel = FALSE;
int mod_auto_sprint = FALSE;
int mod_drop_shot = FALSE;
int mod_bunny_hop = FALSE;
int mod_jitter = FALSE;
int mod_sniper_breath = FALSE;
int mod_quick_reload = FALSE;

int mod_menu_index = 0;
int reload_start_time = 0;

'''
    
    # ============================================================
    # ARRAYS DE NOMS D'ARMES
    # ============================================================
    weapon_names = []
    weapon_name_lengths = []
    weapon_fire_rates = []
    weapon_recoil_v = []
    weapon_recoil_h = []
    weapon_rapid_fire_flags = []
    
    for w in weapons:
        name = w.get('name', 'Unknown')
        weapon_names.append(name)
        weapon_name_lengths.append(len(name))
        weapon_fire_rates.append(str(w.get('fire_rate', 700)))
        weapon_recoil_v.append(str(w.get('vertical_recoil', 25)))
        weapon_recoil_h.append(str(w.get('horizontal_recoil', 10)))
        weapon_rapid_fire_flags.append('1' if w.get('rapid_fire', False) else '0')
    
    # Générer le tableau const string
    script += 'const string noms_armes[] = {\n'
    for i, name in enumerate(weapon_names):
        script += f'    "{name}"'
        if i < len(weapon_names) - 1:
            script += ','
        script += '\n'
    script += '};\n\n'
    
    # Tableau des longueurs
    script += 'const int noms_armesVALEUR[] = {'
    script += ', '.join(str(length) for length in weapon_name_lengths)
    script += '};\n\n'
    
    # Tableaux données armes pour ADT
    script += f'int weapon_fire_rate[{weapon_count}] = {{'
    script += ', '.join(weapon_fire_rates)
    script += '};\n\n'
    
    script += f'int weapon_recoil_v[{weapon_count}] = {{'
    script += ', '.join(weapon_recoil_v)
    script += '};\n\n'
    
    script += f'int weapon_recoil_h[{weapon_count}] = {{'
    script += ', '.join(weapon_recoil_h)
    script += '};\n\n'
    
    script += f'int weapon_rapid_fire[{weapon_count}] = {{'
    script += ', '.join(weapon_rapid_fire_flags)
    script += '};\n\n'
    
    # Labels
    script += '''const string label_primaire[] = { "PRIMARY" };
const string label_secondaire[] = { "SECONDARY" };
const string label_choix_arme[] = { "LIST" };
const string vertical[] = { "VERTICAL" };
const string horizontal[] = { "HORIZONTAL" };
const string label_save[] = { "SAUVEGARDE" };
const string label_ok[] = { "OK" };
const string en[] = { "EN:" };
const string indic[] = { "PAD+L2 - PAD+R2" };
const string mods_title[] = { "MODS" };
const string on_label[] = { "ON" };
const string off_label[] = { "OFF" };

const string mod_names[] = {
    "Anti-Recoil",
    "Rapid Fire",
    "Aim Assist",
    "Slide Cancel",
    "Auto Sprint",
    "Drop Shot",
    "Bunny Hop",
    "Jitter",
    "Sniper Breath",
    "Quick Reload"
};

const int mod_names_length[] = {11, 10, 11, 12, 11, 9, 9, 6, 13, 12};

'''
    
    # Arrays anti-recoil ajustables
    script += f'''// Anti-recul vertical et horizontal pour chaque arme (ajustables)
int arv[{weapon_count}];
int arh[{weapon_count}];

'''
    
    # ============================================================
    # FONCTIONS ADT
    # ============================================================
    script += '''// ===================================================================
// DETECTION AUTOMATIQUE D'ARME (ADT)
// ===================================================================

function detect_weapon_by_fire_rate(measured_rpm) {
    int closest_weapon;
    int min_difference;
    int i;
    int difference;
    
    closest_weapon = index;
    min_difference = 9999;
    
    for(i = 0; i < ''' + str(weapon_count) + '''; i = i + 1) {
        difference = abs(weapon_fire_rate[i] - measured_rpm);
        if(difference < min_difference) {
            min_difference = difference;
            closest_weapon = i;
        }
    }
    
    if(min_difference < 100) {
        return closest_weapon;
    }
    
    return index;
}

function check_if_sniper(weapon_idx) {
    if(weapon_fire_rate[weapon_idx] < 100) {
        return TRUE;
    }
    return FALSE;
}

'''
    
    # ============================================================
    # FONCTIONS D'AFFICHAGE OLED
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

function afficher_menu_mods() {
    int mod_state;
    
    cls_oled(0);
    rect_oled(0, 0, 124, 64, OLED_BLACK, OLED_WHITE);
    rect_oled(0, 0, 124, 25, OLED_BLACK, OLED_WHITE);
    
    print(centre_x(4, OLED_FONT_MEDIUM_WIDTH), 4, OLED_FONT_MEDIUM, OLED_WHITE, mods_title[0]);
    
    print(2, 32, OLED_FONT_SMALL, OLED_WHITE, mod_names[mod_menu_index]);
    
    mod_state = get_mod_state(mod_menu_index);
    if(mod_state) {
        print(90, 32, OLED_FONT_SMALL, OLED_WHITE, on_label[0]);
    } else {
        print(88, 32, OLED_FONT_SMALL, OLED_WHITE, off_label[0]);
    }
}

function get_mod_state(mod_idx) {
    if(mod_idx == 0) return mod_antirecul;
    if(mod_idx == 1) return mod_rapid_fire;
    if(mod_idx == 2) return mod_aim_assist;
    if(mod_idx == 3) return mod_slide_cancel;
    if(mod_idx == 4) return mod_auto_sprint;
    if(mod_idx == 5) return mod_drop_shot;
    if(mod_idx == 6) return mod_bunny_hop;
    if(mod_idx == 7) return mod_jitter;
    if(mod_idx == 8) return mod_sniper_breath;
    if(mod_idx == 9) return mod_quick_reload;
    return FALSE;
}

function toggle_mod(mod_idx) {
    if(mod_idx == 0) mod_antirecul = !mod_antirecul;
    if(mod_idx == 1) mod_rapid_fire = !mod_rapid_fire;
    if(mod_idx == 2) mod_aim_assist = !mod_aim_assist;
    if(mod_idx == 3) mod_slide_cancel = !mod_slide_cancel;
    if(mod_idx == 4) mod_auto_sprint = !mod_auto_sprint;
    if(mod_idx == 5) mod_drop_shot = !mod_drop_shot;
    if(mod_idx == 6) mod_bunny_hop = !mod_bunny_hop;
    if(mod_idx == 7) mod_jitter = !mod_jitter;
    if(mod_idx == 8) mod_sniper_breath = !mod_sniper_breath;
    if(mod_idx == 9) mod_quick_reload = !mod_quick_reload;
}

function centre_x(int nb_caracteres, int largeur_caractere) {
    return (128 / 2) - ((nb_caracteres * largeur_caractere) / 2);
}

'''
    
    # ============================================================
    # BLOC INIT
    # ============================================================
    script += '''// ===================================================================
// INITIALISATION
// ===================================================================

init {
    Load();
    if(current_profil == 0) index = arme_profil_prim;
    else index = arme_profil_sec;
    is_sniper = check_if_sniper(index);
}

'''
    
    # ============================================================
    # BLOC MAIN
    # ============================================================
    script += f'''// ===================================================================
// BOUCLE PRINCIPALE
// ===================================================================

main {{
    // ADT - DETECTION AUTOMATIQUE D'ARME (VERSION REACTIVE)
    if(adt_enabled && event_press(PS4_R2)) {{
        int current_time;
        int shot_delay;
        int detected_weapon;
        
        current_time = system_time();
        
        if(last_shot_time > 0) {{
            shot_delay = current_time - last_shot_time;
            
            // Detecter apres 2 tirs seulement
            if(shot_count >= 1 && shot_delay > 10 && shot_delay < 2000) {{
                total_delay = total_delay + shot_delay;
                shot_count = shot_count + 1;
                
                if(shot_count >= 2) {{
                    detected_fire_rate = 60000 / (total_delay / (shot_count - 1));
                    detected_weapon = detect_weapon_by_fire_rate(detected_fire_rate);
                    
                    if(detected_weapon != index) {{
                        if(current_profil == 0) {{
                            arme_profil_prim = detected_weapon;
                        }} else {{
                            arme_profil_sec = detected_weapon;
                        }}
                        index = detected_weapon;
                        is_sniper = check_if_sniper(index);
                        update = TRUE;
                    }}
                    
                    shot_count = 0;
                    total_delay = 0;
                }}
            }} else if(shot_delay < 10 || shot_delay > 2000) {{
                shot_count = 0;
                total_delay = 0;
            }} else {{
                shot_count = 1;
                total_delay = 0;
            }}
        }} else {{
            shot_count = 0;
            total_delay = 0;
        }}
        
        last_shot_time = current_time;
    }}
    
    if(get_val(PS4_R2) == 0 && (system_time() - last_shot_time) > 2000) {{
        shot_count = 0;
        total_delay = 0;
    }}
    
    if(update) {{
        afficher_profils();
        update = FALSE;
    }}
    
    // Changer de profil avec TRIANGLE
    if(event_press(PS4_TRIANGLE)) {{
        if(current_profil == 0) {{
            current_profil = 1;
            index = arme_profil_sec;
        }} else {{
            current_profil = 0;
            index = arme_profil_prim;
        }}
        is_sniper = check_if_sniper(index);
        update = TRUE;
    }}
    
    // BLOCAGE DES TOUCHES DANS LES MENUS
    if(menu_selection_actif || menu_ar_actif || menu_mods_actif) {{
        block_all_inputs();
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
        
        if(event_press(PS4_CROSS)) {{
            if(current_profil == 0) {{
                arme_profil_prim = index_selection;
                index = arme_profil_prim;
            }} else {{
                arme_profil_sec = index_selection;
                index = arme_profil_sec;
            }}
            is_sniper = check_if_sniper(index);
            menu_selection_actif = FALSE;
            update = TRUE;
            Save();
            combo_run(screen_save);
        }}
        
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
    
    // PAD + TRIANGLE ouvre le menu des mods
    if(get_val(PS4_TOUCH) && event_press(PS4_TRIANGLE)) {{
        menu_mods_actif = TRUE;
        mod_menu_index = 0;
        afficher_menu_mods();
    }}
    
    if(menu_mods_actif) {{
        if(event_press(PS4_UP)) {{
            if(mod_menu_index > 0) {{
                mod_menu_index--;
            }} else {{
                mod_menu_index = 9;
            }}
            afficher_menu_mods();
        }}
        
        if(event_press(PS4_DOWN)) {{
            if(mod_menu_index < 9) {{
                mod_menu_index++;
            }} else {{
                mod_menu_index = 0;
            }}
            afficher_menu_mods();
        }}
        
        if(event_press(PS4_CROSS)) {{
            toggle_mod(mod_menu_index);
            afficher_menu_mods();
        }}
        
        if(event_press(PS4_CIRCLE)) {{
            menu_mods_actif = FALSE;
            update = TRUE;
            Save();
            combo_run(screen_save);
        }}
    }}
    
    // ===================================================================
    // APPLICATION DES MODS
    // ===================================================================
    
    // ANTI-RECOIL
    if(!menu_selection_actif && !menu_ar_actif && !menu_mods_actif) {{
        if(mod_antirecul && get_val(vise) && get_val(tire)) {{
            set_val(PS4_RY, get_val(PS4_RY) + (arv[index] * 2));
            set_val(PS4_RX, get_val(PS4_RX) + arh[index]);
        }}
        
        // RAPID FIRE - AUTOMATIQUE pour armes compatibles
        if(weapon_rapid_fire[index] && get_val(tire) > 10) {{
            combo_run(rapid_fire_combo);
        }}
        
        // AIM ASSIST
        if(mod_aim_assist && get_val(vise) > 10) {{
            combo_run(aim_assist_combo);
            if(get_val(tire) > 10) {{
                combo_run(rotation_assist_combo);
            }}
        }}
        
        // AUTO SPRINT
        if(mod_auto_sprint) {{
            if(abs(get_val(PS4_LY)) > 80 && get_val(vise) < 10) {{
                combo_run(auto_sprint_combo);
            }}
        }}
        
        // SLIDE CANCEL
        if(mod_slide_cancel) {{
            if(event_press(PS4_CIRCLE)) {{
                combo_run(slide_cancel_combo);
            }}
        }}
        
        // BUNNY HOP
        if(mod_bunny_hop) {{
            if(get_val(saut)) {{
                combo_run(bunny_hop_combo);
            }}
        }}
        
        // DROP SHOT
        if(mod_drop_shot) {{
            if(get_val(vise) > 10 && event_press(tire)) {{
                combo_run(dropshot_combo);
            }}
        }}
        
        // JITTER
        if(mod_jitter && get_val(tire) > 10) {{
            combo_run(jitter_combo);
        }}
        
        // SNIPER BREATH
        if(mod_sniper_breath && is_sniper && get_val(vise) > 10) {{
            set_val(PS4_L3, 100);
        }}
        
        // QUICK RELOAD
        if(mod_quick_reload) {{
            if(event_press(recharge)) {{
                reload_start_time = system_time();
            }}
            if((system_time() - reload_start_time) > 800 && (system_time() - reload_start_time) < 1500) {{
                combo_run(reload_cancel_combo);
                reload_start_time = 0;
            }}
        }}
    }}
}}

'''
    
    # ============================================================
    # COMBOS
    # ============================================================
    script += '''// ===================================================================
// COMBOS
// ===================================================================

combo rapid_fire_combo {
    set_val(PS4_R2, 100);
    wait(30);
    set_val(PS4_R2, 0);
    wait(30);
}

combo aim_assist_combo {
    set_val(PS4_RX, get_val(PS4_RX) + 10);
    wait(10);
    set_val(PS4_RX, get_val(PS4_RX) - 10);
    wait(10);
}

combo rotation_assist_combo {
    int rx_val;
    int adjustment;
    
    if(abs(get_val(PS4_RX)) > 5) {
        rx_val = get_val(PS4_RX);
        adjustment = 15;
        if(rx_val < 0) {
            adjustment = -15;
        }
        set_val(PS4_RX, rx_val + adjustment);
    }
}

combo auto_sprint_combo {
    set_val(PS4_L3, 100);
    wait(100);
    set_val(PS4_L3, 0);
    wait(50);
    set_val(PS4_L3, 100);
    wait(100);
}

combo slide_cancel_combo {
    set_val(PS4_CIRCLE, 100);
    wait(180);
    set_val(PS4_CIRCLE, 0);
    wait(50);
    set_val(PS4_CROSS, 100);
    wait(50);
    set_val(PS4_CROSS, 0);
    wait(50);
    set_val(PS4_L3, 100);
    wait(50);
    set_val(PS4_L3, 0);
}

combo bunny_hop_combo {
    set_val(PS4_CROSS, 100);
    wait(40);
    set_val(PS4_CROSS, 0);
    wait(40);
}

combo dropshot_combo {
    set_val(PS4_R2, 100);
    wait(30);
    set_val(PS4_CIRCLE, 100);
    wait(100);
    wait(500);
    set_val(PS4_CIRCLE, 0);
}

combo jitter_combo {
    set_val(PS4_RX, 50);
    wait(20);
    set_val(PS4_RX, -50);
    wait(20);
}

combo reload_cancel_combo {
    set_val(PS4_L3, 100);
    wait(50);
    set_val(PS4_L3, 0);
    wait(30);
    set_val(PS4_TRIANGLE, 100);
    wait(50);
    set_val(PS4_TRIANGLE, 0);
    wait(50);
    set_val(PS4_TRIANGLE, 100);
    wait(50);
    set_val(PS4_TRIANGLE, 0);
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
    # FONCTIONS UTILITAIRES
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
    # FONCTIONS SAVE/LOAD
    # ============================================================
    script += f'''// ===================================================================
// PERSISTANCE (SAVE/LOAD)
// ===================================================================

function Save() {{
    reset_spvar();
    save_spvar(1, 0, 1);
    save_spvar(arme_profil_prim, 0, {weapon_count - 1});
    save_spvar(arme_profil_sec, 0, {weapon_count - 1});
    
    // Sauvegarder les mods
    save_spvar(mod_antirecul, 0, 1);
    save_spvar(mod_rapid_fire, 0, 1);
    save_spvar(mod_aim_assist, 0, 1);
    save_spvar(mod_slide_cancel, 0, 1);
    save_spvar(mod_auto_sprint, 0, 1);
    save_spvar(mod_drop_shot, 0, 1);
    save_spvar(mod_bunny_hop, 0, 1);
    save_spvar(mod_jitter, 0, 1);
    save_spvar(mod_sniper_breath, 0, 1);
    save_spvar(mod_quick_reload, 0, 1);
    
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
        
        // Charger les mods
        mod_antirecul = read_spvar(0, 1, 1);
        mod_rapid_fire = read_spvar(0, 1, 0);
        mod_aim_assist = read_spvar(0, 1, 0);
        mod_slide_cancel = read_spvar(0, 1, 0);
        mod_auto_sprint = read_spvar(0, 1, 0);
        mod_drop_shot = read_spvar(0, 1, 0);
        mod_bunny_hop = read_spvar(0, 1, 0);
        mod_jitter = read_spvar(0, 1, 0);
        mod_sniper_breath = read_spvar(0, 1, 0);
        mod_quick_reload = read_spvar(0, 1, 0);
        
'''
    
    for i in range(weapon_count):
        script += f'        arv[{i}] = read_spvar(-99, 99, 0);\n'
    for i in range(weapon_count):
        script += f'        arh[{i}] = read_spvar(-99, 99, 0);\n'
    
    script += '''    } else {
        arme_profil_prim = 0;
        arme_profil_sec = 0;
        mod_antirecul = TRUE;
        mod_rapid_fire = FALSE;
        mod_aim_assist = FALSE;
        mod_slide_cancel = FALSE;
        mod_auto_sprint = FALSE;
        mod_drop_shot = FALSE;
        mod_bunny_hop = FALSE;
        mod_jitter = FALSE;
        mod_sniper_breath = FALSE;
        mod_quick_reload = FALSE;
    }
}

'''
    
    # ============================================================
    # SYSTÈME SPVAR
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

"""
ZEN HUB PRO - Générateur GPC ULTIMATE (Master ADT v6.0 + Mods)
Intègre les recommandations de l'IA Experte
"""

from typing import List, Dict
from datetime import datetime, timezone

def generate_ultimate_script(weapons: List[Dict]) -> str:
    """
    Script ULTIME : Combine le script stable + recommandations IA Experte
    - Jump Shot + Slide Cancel + Auto Sprint
    - Master ADT avec sélection rapide LEFT/RIGHT
    - Valeurs optimisées pour AS VAL, WSP Swarm, etc.
    """
    
    weapon_count = len(weapons)
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # ============================================================
    # EN-TÊTE
    # ============================================================
    script = f'''// ===================================================================
// ZEN HUB PRO - ULTIMATE MASTER SCRIPT
// ARCHITECTE BALISTIQUE SUPRÊME - MASTER ADT v6.0
// Generated: {generation_time}
// Total Weapons: {weapon_count}
// ===================================================================
//
// CONTROLES:
// - LEFT/RIGHT : Sélection rapide d'arme (Index 1-20)
// - TRIANGLE : Changer de slot (Primaire/Secondaire)
// - PAD + DOWN : Menu Settings
//
// MODS ACTIFS:
// - Jump Shot (tire sans viser)
// - Slide Cancel (350ms)
// - Auto Sprint
// - Master Recoil (valeurs optimisées par arme)
//
// ===================================================================

'''
    
    # ============================================================
    # VARIABLES
    # ============================================================
    script += '''int vise = PS4_L2;
int tire = PS4_R2;
int accroupi = PS4_R3;
int saut = PS4_CROSS;
int recharge = PS4_SQUARE;
int sprint = PS4_L3;
int melee = PS4_CIRCLE;

// Master ADT - Système de navigation
int Weapon_Index = 1;
int V_Recoil = 28;
int H_Recoil = 18;

// Mods de combat
int jumpshot_actif = TRUE;
int slidecancel_actif = TRUE;
int autosprint_actif = TRUE;
int sc_cancel_delay_time = 350;
int as_sprint_threshold = 80;

// Settings
int control_mode = 0;
int menu_settings_actif = FALSE;
int settings_index = 0;
int update = TRUE;

'''
    
    # ============================================================
    # DÉCLARATION DES LABELS OLED
    # ============================================================
    script += '''// Labels OLED
const int8 label_armes[][21] = {
    "AS VAL",
    "WSP SWARM",
    "SVA 546",
    "M4",
    "KILO 141",
    "MK2B",
    "TANTO 22",
    "MCW LMG",
    "JACKAL PDW",
    "MCW AR",
    "HOLGER 556",
    "STRIKER",
    "HRM-9",
    "BAS-P",
    "AMES 85",
    "GROZA-MMAX",
    "SAUG",
    "ABR A1",
    "MCB",
    "STB44"
};

const int label_armesVALEUR[] = {7, 10, 7, 2, 8, 4, 8, 7, 10, 6, 10, 7, 5, 5, 7, 10, 4, 6, 3, 5};

const int8 label_settings[][21] = {
    "MODE CONTROLE",
    "NORMAL",
    "TACTIQUE"
};

const int8 label_save[][21] = {
    "SAVED !"
};

const int8 label_ok[][21] = {
    "OK"
};

'''
    
    # ============================================================
    # FONCTIONS
    # ============================================================
    script += '''// ===================================================================
// FONCTIONS
// ===================================================================

function afficher_arme() {
    cls_oled(0);
    print(10, 20, OLED_FONT_MEDIUM, OLED_WHITE, "ARME ACTUELLE:");
    print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_armes[Weapon_Index - 1]);
    
    // Afficher les valeurs de recul
    printf(10, 60, OLED_FONT_SMALL, OLED_CYAN, "V:%d H:%d", V_Recoil, H_Recoil);
}

function smart_family() {
    if(v > 100) return 102;
    if(v < -100) return -102;
    return v;
}

function block_all_inputs() {
    set_val(PS4_UP, 0);
    set_val(PS4_DOWN, 0);
    set_val(PS4_LEFT, 0);
    set_val(PS4_RIGHT, 0);
    set_val(PS4_TRIANGLE, 0);
    set_val(PS4_CIRCLE, 0);
    set_val(PS4_CROSS, 0);
    set_val(PS4_SQUARE, 0);
    set_val(PS4_L1, 0);
    set_val(PS4_R1, 0);
    set_val(PS4_L2, 0);
    set_val(PS4_R2, 0);
}

'''
    
    # ============================================================
    # INIT BLOCK
    # ============================================================
    script += '''// ===================================================================
// INIT
// ===================================================================

init {
    V_Recoil = 28;
    H_Recoil = 18;
    Weapon_Index = 1;
    afficher_arme();
}

'''
    
    # ============================================================
    # MAIN BLOCK
    # ============================================================
    script += '''// ===================================================================
// MAIN
// ===================================================================

main {
    // ═══════════════════════════════════════════════════════════
    // SYSTÈME DE SÉLECTION RAPIDE (LEFT/RIGHT)
    // ═══════════════════════════════════════════════════════════
    
    if(event_press(PS4_LEFT)) {
        if(Weapon_Index > 1) Weapon_Index--;
        else Weapon_Index = 20;
        
        // Mise à jour des valeurs de recul
        if(Weapon_Index == 1) { V_Recoil = 28; H_Recoil = 18; } // AS VAL
        if(Weapon_Index == 2) { V_Recoil = 22; H_Recoil = 20; } // WSP SWARM
        if(Weapon_Index == 3) { V_Recoil = 26; H_Recoil = 18; } // SVA 546
        if(Weapon_Index == 4) { V_Recoil = 24; H_Recoil = 18; } // M4
        if(Weapon_Index == 5) { V_Recoil = 26; H_Recoil = 18; } // KILO 141
        if(Weapon_Index == 6) { V_Recoil = 30; H_Recoil = 20; } // MK2B
        if(Weapon_Index == 7) { V_Recoil = 16; H_Recoil = 18; } // TANTO 22
        if(Weapon_Index == 8) { V_Recoil = 28; H_Recoil = 18; } // MCW LMG
        if(Weapon_Index == 9) { V_Recoil = 20; H_Recoil = 18; } // JACKAL PDW
        if(Weapon_Index == 10) { V_Recoil = 24; H_Recoil = 18; } // MCW AR
        if(Weapon_Index == 11) { V_Recoil = 20; H_Recoil = 7; } // HOLGER 556
        if(Weapon_Index == 12) { V_Recoil = 16; H_Recoil = 18; } // STRIKER
        if(Weapon_Index == 13) { V_Recoil = 20; H_Recoil = 12; } // HRM-9
        if(Weapon_Index == 14) { V_Recoil = 20; H_Recoil = 16; } // BAS-P
        if(Weapon_Index == 15) { V_Recoil = 26; H_Recoil = 18; } // AMES 85
        if(Weapon_Index == 16) { V_Recoil = 26; H_Recoil = 18; } // GROZA-MMAX
        if(Weapon_Index == 17) { V_Recoil = 16; H_Recoil = 12; } // SAUG
        if(Weapon_Index == 18) { V_Recoil = 28; H_Recoil = 12; } // ABR A1
        if(Weapon_Index == 19) { V_Recoil = 24; H_Recoil = 7; } // MCB
        if(Weapon_Index == 20) { V_Recoil = 24; H_Recoil = 18; } // STB44
        
        afficher_arme();
        combo_run(Notify);
        set_val(PS4_LEFT, 0);
    }
    
    if(event_press(PS4_RIGHT)) {
        if(Weapon_Index < 20) Weapon_Index++;
        else Weapon_Index = 1;
        
        // Mise à jour des valeurs de recul
        if(Weapon_Index == 1) { V_Recoil = 28; H_Recoil = 18; } // AS VAL
        if(Weapon_Index == 2) { V_Recoil = 22; H_Recoil = 20; } // WSP SWARM
        if(Weapon_Index == 3) { V_Recoil = 26; H_Recoil = 18; } // SVA 546
        if(Weapon_Index == 4) { V_Recoil = 24; H_Recoil = 18; } // M4
        if(Weapon_Index == 5) { V_Recoil = 26; H_Recoil = 18; } // KILO 141
        if(Weapon_Index == 6) { V_Recoil = 30; H_Recoil = 20; } // MK2B
        if(Weapon_Index == 7) { V_Recoil = 16; H_Recoil = 18; } // TANTO 22
        if(Weapon_Index == 8) { V_Recoil = 28; H_Recoil = 18; } // MCW LMG
        if(Weapon_Index == 9) { V_Recoil = 20; H_Recoil = 18; } // JACKAL PDW
        if(Weapon_Index == 10) { V_Recoil = 24; H_Recoil = 18; } // MCW AR
        if(Weapon_Index == 11) { V_Recoil = 20; H_Recoil = 7; } // HOLGER 556
        if(Weapon_Index == 12) { V_Recoil = 16; H_Recoil = 18; } // STRIKER
        if(Weapon_Index == 13) { V_Recoil = 20; H_Recoil = 12; } // HRM-9
        if(Weapon_Index == 14) { V_Recoil = 20; H_Recoil = 16; } // BAS-P
        if(Weapon_Index == 15) { V_Recoil = 26; H_Recoil = 18; } // AMES 85
        if(Weapon_Index == 16) { V_Recoil = 26; H_Recoil = 18; } // GROZA-MMAX
        if(Weapon_Index == 17) { V_Recoil = 16; H_Recoil = 12; } // SAUG
        if(Weapon_Index == 18) { V_Recoil = 28; H_Recoil = 12; } // ABR A1
        if(Weapon_Index == 19) { V_Recoil = 24; H_Recoil = 7; } // MCB
        if(Weapon_Index == 20) { V_Recoil = 24; H_Recoil = 18; } // STB44
        
        afficher_arme();
        combo_run(Notify);
        set_val(PS4_RIGHT, 0);
    }
    
    // ═══════════════════════════════════════════════════════════
    // MENU SETTINGS (PAD + DOWN)
    // ═══════════════════════════════════════════════════════════
    
    if(get_val(PS4_TOUCH) && event_press(PS4_DOWN)) {
        menu_settings_actif = TRUE;
        cls_oled(0);
        print(10, 10, OLED_FONT_MEDIUM, OLED_WHITE, label_settings[0]);
        if(control_mode == 0) {
            print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[1]);
        } else {
            print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[2]);
        }
    }
    
    if(menu_settings_actif) {
        block_all_inputs();
        
        if(event_press(PS4_CROSS)) {
            if(control_mode == 0) {
                control_mode = 1;
                accroupi = PS4_R3;
                melee = PS4_CIRCLE;
            } else {
                control_mode = 0;
                accroupi = PS4_CIRCLE;
                melee = PS4_R3;
            }
            
            cls_oled(0);
            print(10, 10, OLED_FONT_MEDIUM, OLED_WHITE, label_settings[0]);
            if(control_mode == 0) {
                print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[1]);
            } else {
                print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[2]);
            }
        }
        
        if(event_press(PS4_CIRCLE)) {
            menu_settings_actif = FALSE;
            combo_run(screen_save);
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // BLOCAGE INPUTS DANS MENU
    // ═══════════════════════════════════════════════════════════
    
    if(menu_settings_actif) {
        block_all_inputs();
    }
    
    // ═══════════════════════════════════════════════════════════
    // AUTO SPRINT
    // ═══════════════════════════════════════════════════════════
    
    if(autosprint_actif && !menu_settings_actif) {
        if(abs(get_val(PS4_LY)) > as_sprint_threshold && get_val(PS4_LY) < 0) {
            set_val(sprint, 100);
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // JUMP SHOT (maintenu)
    // ═══════════════════════════════════════════════════════════
    
    if(jumpshot_actif && !menu_settings_actif) {
        if(get_val(tire) && !get_val(vise)) {
            combo_run(JumpShot);
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // SLIDE CANCEL
    // ═══════════════════════════════════════════════════════════
    
    if(slidecancel_actif && !menu_settings_actif) {
        if(get_val(sprint) && event_press(accroupi)) {
            combo_run(SlideCancel);
        }
    }
    
    // ═══════════════════════════════════════════════════════════
    // MASTER RECOIL (avec valeurs optimisées)
    // ═══════════════════════════════════════════════════════════
    
    if(!menu_settings_actif) {
        if(get_val(vise) && get_val(tire)) {
            combo_run(MasterRecoil);
            
            // Burst spécial pour SVA si besoin
            if(Weapon_Index == 3) {
                combo_run(SVA_Hyper);
            }
        }
    }
}

'''
    
    # ============================================================
    # COMBOS
    # ============================================================
    script += '''// ===================================================================
// COMBOS
// ===================================================================

combo JumpShot {
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}

combo SlideCancel {
    wait(350);
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}

combo MasterRecoil {
    set_val(PS4_RY, smart_family(get_val(PS4_RY) + V_Recoil));
    set_val(PS4_RX, smart_family(get_val(PS4_RX) + H_Recoil));
    wait(20);
}

combo SVA_Hyper {
    set_val(PS4_RY, 100);
    wait(20);
    set_val(PS4_RY, 0);
    wait(20);
}

combo Notify {
    set_led(LED_1, 0);
    wait(100);
    set_led(LED_1, 1);
}

combo screen_save {
    cls_oled(0);
    print(10, 20, OLED_FONT_MEDIUM, OLED_WHITE, label_save[0]);
    print(52, 40, OLED_FONT_MEDIUM, OLED_WHITE, label_ok[0]);
    wait(600);
    cls_oled(0);
    afficher_arme();
}

'''
    
    return script

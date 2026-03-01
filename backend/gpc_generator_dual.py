"""
ZEN HUB PRO - Générateur GPC SIMPLE (2 Profils Fixes)
AS VAL (Primaire) + WSP SWARM (Secondaire)
"""

from typing import List, Dict
from datetime import datetime, timezone

def generate_dual_profile_script(weapons: List[Dict]) -> str:
    """
    Script SIMPLE avec 2 profils fixes :
    - Profil 0 (Primaire) : AS VAL (28v/18h)
    - Profil 1 (Secondaire) : WSP SWARM (22v/20h)
    - TRIANGLE pour changer
    - Jump Shot + Slide Cancel + Auto Sprint
    """
    
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    script = f'''// ===================================================================
// ZEN HUB PRO - DUAL PROFILE SCRIPT
// AS VAL (Primaire) + WSP SWARM (Secondaire)
// Generated: {generation_time}
// Valeurs optimisées par IA Experte
// ===================================================================
//
// CONTROLES:
// - TRIANGLE : Changer de profil (AS VAL <-> WSP SWARM)
// - PAD + DOWN : Menu Settings (Normal/Tactique)
//
// PROFILS:
// - Profil 0 (Primaire) : AS VAL → V:28 H:18
// - Profil 1 (Secondaire) : WSP SWARM → V:22 H:20
//
// MODS ACTIFS:
// - Jump Shot (tire sans viser)
// - Slide Cancel (350ms)
// - Auto Sprint
//
// ===================================================================

int vise = PS4_L2;
int tire = PS4_R2;
int accroupi = PS4_R3;
int saut = PS4_CROSS;
int recharge = PS4_SQUARE;
int sprint = PS4_L3;
int melee = PS4_CIRCLE;

// Profils AS VAL + WSP SWARM
int current_profil = 0;  // 0 = AS VAL, 1 = WSP SWARM

// Valeurs de recul optimisées (IA Experte)
int asval_v = 28;
int asval_h = 18;
int wsp_v = 22;
int wsp_h = 20;

// Valeurs actives
int active_v = 28;
int active_h = 18;

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

// Labels OLED
const int8 label_profils[][21] = {{
    "AS VAL",
    "WSP SWARM"
}};

const int8 label_settings[][21] = {{
    "MODE CONTROLE",
    "NORMAL",
    "TACTIQUE"
}};

const int8 label_save[][21] = {{
    "SAVED !"
}};

const int8 label_ok[][21] = {{
    "OK"
}};

// ===================================================================
// FONCTIONS
// ===================================================================

function afficher_profil() {{
    cls_oled(0);
    
    if(current_profil == 0) {{
        print(10, 10, OLED_FONT_MEDIUM, OLED_WHITE, "PROFIL PRIMAIRE:");
        print(10, 30, OLED_FONT_LARGE, OLED_GREEN, "AS VAL");
        printf(10, 55, OLED_FONT_SMALL, OLED_CYAN, "V:%d H:%d", asval_v, asval_h);
    }} else {{
        print(10, 10, OLED_FONT_MEDIUM, OLED_WHITE, "PROFIL SECONDAIRE:");
        print(10, 30, OLED_FONT_LARGE, OLED_GREEN, "WSP SWARM");
        printf(10, 55, OLED_FONT_SMALL, OLED_CYAN, "V:%d H:%d", wsp_v, wsp_h);
    }}
}}

function block_all_inputs() {{
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
}}

// ===================================================================
// INIT
// ===================================================================

init {{
    current_profil = 0;
    active_v = asval_v;
    active_h = asval_h;
    afficher_profil();
}}

// ===================================================================
// MAIN
// ===================================================================

main {{
    // ═══════════════════════════════════════════════════════════
    // CHANGEMENT DE PROFIL (TRIANGLE)
    // ═══════════════════════════════════════════════════════════
    
    if(event_press(PS4_TRIANGLE)) {{
        if(current_profil == 0) {{
            current_profil = 1;
            active_v = wsp_v;
            active_h = wsp_h;
        }} else {{
            current_profil = 0;
            active_v = asval_v;
            active_h = asval_h;
        }}
        afficher_profil();
        combo_run(Notify);
    }}
    
    // ═══════════════════════════════════════════════════════════
    // MENU SETTINGS (PAD + DOWN)
    // ═══════════════════════════════════════════════════════════
    
    if(get_val(PS4_TOUCH) && event_press(PS4_DOWN)) {{
        menu_settings_actif = TRUE;
        cls_oled(0);
        print(10, 10, OLED_FONT_MEDIUM, OLED_WHITE, label_settings[0]);
        if(control_mode == 0) {{
            print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[1]);
        }} else {{
            print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[2]);
        }}
    }}
    
    if(menu_settings_actif) {{
        block_all_inputs();
        
        if(event_press(PS4_CROSS)) {{
            if(control_mode == 0) {{
                control_mode = 1;
                accroupi = PS4_R3;
                melee = PS4_CIRCLE;
            }} else {{
                control_mode = 0;
                accroupi = PS4_CIRCLE;
                melee = PS4_R3;
            }}
            
            cls_oled(0);
            print(10, 10, OLED_FONT_MEDIUM, OLED_WHITE, label_settings[0]);
            if(control_mode == 0) {{
                print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[1]);
            }} else {{
                print(10, 40, OLED_FONT_LARGE, OLED_GREEN, label_settings[2]);
            }}
        }}
        
        if(event_press(PS4_CIRCLE)) {{
            menu_settings_actif = FALSE;
            combo_run(screen_save);
        }}
    }}
    
    // ═══════════════════════════════════════════════════════════
    // BLOCAGE INPUTS DANS MENU
    // ═══════════════════════════════════════════════════════════
    
    if(menu_settings_actif) {{
        block_all_inputs();
    }}
    
    // ═══════════════════════════════════════════════════════════
    // AUTO SPRINT
    // ═══════════════════════════════════════════════════════════
    
    if(autosprint_actif && !menu_settings_actif) {{
        if(abs(get_val(PS4_LY)) > as_sprint_threshold && get_val(PS4_LY) < 0) {{
            set_val(sprint, 100);
        }}
    }}
    
    // ═══════════════════════════════════════════════════════════
    // JUMP SHOT (maintenu)
    // ═══════════════════════════════════════════════════════════
    
    if(jumpshot_actif && !menu_settings_actif) {{
        if(get_val(tire) && !get_val(vise)) {{
            combo_run(JumpShot);
        }}
    }}
    
    // ═══════════════════════════════════════════════════════════
    // SLIDE CANCEL
    // ═══════════════════════════════════════════════════════════
    
    if(slidecancel_actif && !menu_settings_actif) {{
        if(get_val(sprint) && event_press(accroupi)) {{
            combo_run(SlideCancel);
        }}
    }}
    
    // ═══════════════════════════════════════════════════════════
    // ANTI-RECUL (valeurs optimisées selon profil)
    // ═══════════════════════════════════════════════════════════
    
    if(!menu_settings_actif) {{
        if(get_val(vise) && get_val(tire)) {{
            set_val(PS4_RY, get_val(PS4_RY) + (active_v * 2));
            set_val(PS4_RX, get_val(PS4_RX) + active_h);
        }}
    }}
}}

// ===================================================================
// COMBOS
// ===================================================================

combo JumpShot {{
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}}

combo SlideCancel {{
    wait(350);
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}}

combo Notify {{
    set_led(LED_1, 0);
    wait(100);
    set_led(LED_1, 1);
}}

combo screen_save {{
    cls_oled(0);
    print(10, 20, OLED_FONT_MEDIUM, OLED_WHITE, label_save[0]);
    print(52, 40, OLED_FONT_MEDIUM, OLED_WHITE, label_ok[0]);
    wait(600);
    cls_oled(0);
    afficher_profil();
}}

'''
    
    return script

"""
ZEN HUB PRO - Générateur GPC SIMPLE (2 Profils Fixes)
AS VAL (Primaire) + WSP SWARM (Secondaire)
"""

from typing import List, Dict
from datetime import datetime, timezone

def generate_dual_profile_script(weapons: List[Dict]) -> str:
    """
    Script SIMPLE avec 2 profils dynamiques.
    Les 2 armes sont injectees depuis la base pour eviter les presets
    non adaptes au duo de l'utilisateur.
    - TRIANGLE pour changer
    - Jump Shot + Slide Cancel + Auto Sprint
    """
    
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    primary = weapons[0] if weapons else {}
    secondary = weapons[1] if len(weapons) > 1 else primary

    primary_name = str(primary.get("name", "PRIMARY")).upper()
    secondary_name = str(secondary.get("name", "SECONDARY")).upper()

    primary_v = int(primary.get("script_vertical", primary.get("vertical_recoil", 24)))
    primary_h = int(primary.get("script_horizontal", primary.get("horizontal_recoil", 10)))
    secondary_v = int(secondary.get("script_vertical", secondary.get("vertical_recoil", 20)))
    secondary_h = int(secondary.get("script_horizontal", secondary.get("horizontal_recoil", 8)))

    primary_boost = int(primary.get("script_burst_boost", 3))
    secondary_boost = int(secondary.get("script_burst_boost", 3))
    
    script = f'''// ===================================================================
// ZEN HUB PRO - DUAL PROFILE SCRIPT
// {primary_name} (Primaire) + {secondary_name} (Secondaire)
// Generated: {generation_time}
// Valeurs optimisees par IA Experte
// ===================================================================
//
// CONTROLES:
// - TRIANGLE : Changer de profil (Primaire <-> Secondaire)
// - PAD + DOWN : Menu Settings (Normal/Tactique)
//
// PROFILS:
// - Profil 0 (Primaire) : {primary_name} -> V:{primary_v} H:{primary_h}
// - Profil 1 (Secondaire) : {secondary_name} -> V:{secondary_v} H:{secondary_h}
//
// MODS ACTIFS:
// - Jump Shot (tire sans viser)
// - Slide Cancel (350ms)
// - Auto Sprint
// - Anti-recul adaptatif (boost sur tir soutenu)
//
// ===================================================================

int vise = PS4_L2;
int tire = PS4_R2;
int accroupi = PS4_R3;
int saut = PS4_CROSS;
int recharge = PS4_SQUARE;
int sprint = PS4_L3;
int melee = PS4_CIRCLE;

// Profils dynamiques
int current_profil = 0;  // 0 = primaire, 1 = secondaire

// Valeurs de recul optimisees (IA Experte)
int primary_v = {primary_v};
int primary_h = {primary_h};
int secondary_v = {secondary_v};
int secondary_h = {secondary_h};
int primary_boost = {primary_boost};
int secondary_boost = {secondary_boost};

// Valeurs actives
int active_v = {primary_v};
int active_h = {primary_h};
int active_boost = {primary_boost};
int recoil_hold_ticks = 0;

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
    "PRIMARY",
    "SECONDARY"
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
        print(10, 30, OLED_FONT_LARGE, OLED_GREEN, "{primary_name}");
        printf(10, 55, OLED_FONT_SMALL, OLED_CYAN, "V:%d H:%d", primary_v, primary_h);
    }} else {{
        print(10, 10, OLED_FONT_MEDIUM, OLED_WHITE, "PROFIL SECONDAIRE:");
        print(10, 30, OLED_FONT_LARGE, OLED_GREEN, "{secondary_name}");
        printf(10, 55, OLED_FONT_SMALL, OLED_CYAN, "V:%d H:%d", secondary_v, secondary_h);
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
    active_v = primary_v;
    active_h = primary_h;
    active_boost = primary_boost;
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
            active_v = secondary_v;
            active_h = secondary_h;
            active_boost = secondary_boost;
        }} else {{
            current_profil = 0;
            active_v = primary_v;
            active_h = primary_h;
            active_boost = primary_boost;
        }}
        recoil_hold_ticks = 0;
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
            recoil_hold_ticks = recoil_hold_ticks + 1;
            if(recoil_hold_ticks > 8) {{
                set_val(PS4_RY, get_val(PS4_RY) + ((active_v + active_boost) * 2));
            }} else {{
                set_val(PS4_RY, get_val(PS4_RY) + (active_v * 2));
            }}
            set_val(PS4_RX, get_val(PS4_RX) + active_h);
        }} else {{
            recoil_hold_ticks = 0;
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

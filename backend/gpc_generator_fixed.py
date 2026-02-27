"""
ZEN HUB PRO - Advanced GPC Generator FIXED
All features kept: ADT, 10 mods, spvar persistence, 53 weapons
Syntax corrected for Zen Studio compilation
"""

from typing import List, Dict
from datetime import datetime, timezone

def generate_master_script_advanced(weapons: List[Dict]) -> str:
    """Generate COMPLETE advanced script with ALL features - SYNTAX FIXED"""
    
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    weapon_count = len(weapons)
    
    # NO #include - causes issues
    script = f'''// ===================================================================
// ZEN HUB PRO - MASTER SCRIPT ULTIMATE v2.0
// Generated: {generation_time}
// Total Weapons: {weapon_count}
// Platform: PlayStation 5
// ===================================================================
// 
// AUTO-DETECTION TECHNOLOGY (ADT)
// TIRE AVEC N IMPORTE QUELLE ARME -> DETECTION AUTO
// ANTI-RECOIL AJUSTE AUTOMATIQUEMENT
// 10 MODS INCLUS
// PERSISTANCE FLASH (spvar)
// 
// ===================================================================

// GLOBAL VARIABLES
int current_weapon;
int menu_mode;
int menu_selection;
int mod_states[10];
int ar_active;
int last_shot_time;
int shot_count;
int total_delay;
int detected_fire_rate;
int adt_enabled;
int is_sniper;
int reload_start_time;

// WEAPON COUNT
#define WEAPON_COUNT {weapon_count}

// MOD INDICES
#define MOD_ANTI_RECOIL 0
#define MOD_RAPID_FIRE 1
#define MOD_AIM_ASSIST 2
#define MOD_SLIDE_CANCEL 3
#define MOD_AUTO_SPRINT 4
#define MOD_DROP_SHOT 5
#define MOD_BUNNY_HOP 6
#define MOD_JITTER 7
#define MOD_SNIPER_BREATH 8
#define MOD_QUICK_RELOAD 9

// SPVAR ADDRESSES
#define SPVAR_CURRENT_WEAPON 0
#define SPVAR_MOD_STATES_START 1

// MENU MODES
#define MENU_WEAPON_SELECT 0
#define MENU_MOD_TOGGLE 1

// WEAPON DATA ARRAYS
'''

    # Generate weapon arrays
    recoil_v = []
    recoil_h = []
    fire_rates = []
    rapid_fire = []
    
    for w in weapons:
        recoil_v.append(str(w.get('vertical_recoil', 25)))
        recoil_h.append(str(w.get('horizontal_recoil', 10)))
        fire_rates.append(str(w.get('fire_rate', 700)))
        rapid_fire.append('1' if w.get('rapid_fire', False) else '0')
    
    script += 'int weapon_recoil_v[WEAPON_COUNT] = {\n'
    script += '    ' + ', '.join(recoil_v) + '\n};\n\n'
    
    script += 'int weapon_recoil_h[WEAPON_COUNT] = {\n'
    script += '    ' + ', '.join(recoil_h) + '\n};\n\n'
    
    script += 'int weapon_fire_rate[WEAPON_COUNT] = {\n'
    script += '    ' + ', '.join(fire_rates) + '\n};\n\n'
    
    script += 'int weapon_rapid_fire[WEAPON_COUNT] = {\n'
    script += '    ' + ', '.join(rapid_fire) + '\n};\n\n'
    
    # Init block
    script += '''// ===================================================================
// AUTO-DETECTION FUNCTIONS
// ===================================================================

function detect_weapon_by_fire_rate(measured_rpm) {
    int closest_weapon;
    int min_difference;
    int i;
    int difference;
    
    closest_weapon = current_weapon;
    min_difference = 9999;
    
    for(i = 0; i < WEAPON_COUNT; i = i + 1) {
        difference = abs(weapon_fire_rate[i] - measured_rpm);
        if(difference < min_difference) {
            min_difference = difference;
            closest_weapon = i;
        }
    }
    
    if(min_difference < 100) {
        return closest_weapon;
    }
    
    return current_weapon;
}

function check_if_sniper(weapon_idx) {
    if(weapon_fire_rate[weapon_idx] < 100) {
        return 1;
    }
    return 0;
}

// ===================================================================
// INITIALIZATION
// ===================================================================

init {
    int i;
    
    current_weapon = get_pvar(SPVAR_CURRENT_WEAPON, 0, WEAPON_COUNT - 1, 0);
    
    is_sniper = check_if_sniper(current_weapon);
    
    for(i = 0; i < 10; i = i + 1) {
        mod_states[i] = get_pvar(SPVAR_MOD_STATES_START + i, 0, 1, 0);
        if(mod_states[i] != 1 && mod_states[i] != 0) {
            if(i == MOD_ANTI_RECOIL || i == MOD_AIM_ASSIST || 
               i == MOD_AUTO_SPRINT || i == MOD_SLIDE_CANCEL) {
                mod_states[i] = 1;
            } else {
                mod_states[i] = 0;
            }
        }
    }
    
    menu_mode = 0;
    menu_selection = 0;
    ar_active = 0;
    last_shot_time = 0;
    shot_count = 0;
    total_delay = 0;
    detected_fire_rate = 0;
    adt_enabled = 1;
    reload_start_time = 0;
}

// ===================================================================
// MAIN LOOP
// ===================================================================

main {
    // AUTO-DETECTION SYSTEM (ADT)
    if(adt_enabled && event_press(PS4_R2)) {
        int current_time;
        int shot_delay;
        int avg_delay;
        int detected_weapon;
        
        current_time = system_time();
        
        if(last_shot_time > 0 && shot_count < 5) {
            shot_delay = current_time - last_shot_time;
            
            if(shot_count > 0) {
                total_delay = total_delay + shot_delay;
                shot_count = shot_count + 1;
                
                if(shot_count >= 3) {
                    avg_delay = total_delay / (shot_count - 1);
                    detected_fire_rate = 60000 / avg_delay;
                    
                    detected_weapon = detect_weapon_by_fire_rate(detected_fire_rate);
                    
                    if(detected_weapon != current_weapon) {
                        current_weapon = detected_weapon;
                        is_sniper = check_if_sniper(current_weapon);
                        set_pvar(SPVAR_CURRENT_WEAPON, current_weapon);
                    }
                    
                    shot_count = 0;
                    total_delay = 0;
                }
            } else {
                shot_count = 1;
            }
        } else {
            shot_count = 0;
            total_delay = 0;
        }
        
        last_shot_time = current_time;
    }
    
    if(get_val(PS4_R2) == 0 && (system_time() - last_shot_time) > 2000) {
        shot_count = 0;
        total_delay = 0;
    }
    
    // MENU NAVIGATION
    if(get_val(PS4_L1) && event_press(PS4_TRIANGLE)) {
        menu_mode = !menu_mode;
        menu_selection = 0;
    }
    
    if(get_val(PS4_L1) && event_press(PS4_UP)) {
        if(menu_mode == MENU_WEAPON_SELECT) {
            menu_selection = menu_selection - 1;
            if(menu_selection < 0) menu_selection = WEAPON_COUNT - 1;
        } else {
            menu_selection = menu_selection - 1;
            if(menu_selection < 0) menu_selection = 9;
        }
    }
    
    if(get_val(PS4_L1) && event_press(PS4_DOWN)) {
        if(menu_mode == MENU_WEAPON_SELECT) {
            menu_selection = menu_selection + 1;
            if(menu_selection >= WEAPON_COUNT) menu_selection = 0;
        } else {
            menu_selection = menu_selection + 1;
            if(menu_selection >= 10) menu_selection = 0;
        }
    }
    
    if(get_val(PS4_L1) && event_press(PS4_CROSS)) {
        if(menu_mode == MENU_WEAPON_SELECT) {
            current_weapon = menu_selection;
            set_pvar(SPVAR_CURRENT_WEAPON, current_weapon);
        } else {
            mod_states[menu_selection] = !mod_states[menu_selection];
            set_pvar(SPVAR_MOD_STATES_START + menu_selection, mod_states[menu_selection]);
        }
    }
    
    if(get_val(PS4_L2)) {
        if(event_press(PS4_LEFT)) {
            current_weapon = current_weapon - 1;
            if(current_weapon < 0) current_weapon = WEAPON_COUNT - 1;
            set_pvar(SPVAR_CURRENT_WEAPON, current_weapon);
        }
        if(event_press(PS4_RIGHT)) {
            current_weapon = current_weapon + 1;
            if(current_weapon >= WEAPON_COUNT) current_weapon = 0;
            set_pvar(SPVAR_CURRENT_WEAPON, current_weapon);
        }
    }
    
    // ANTI-RECOIL
    if(mod_states[MOD_ANTI_RECOIL] && get_val(PS4_R2) > 10) {
        int v_comp;
        int h_comp;
        
        v_comp = weapon_recoil_v[current_weapon];
        h_comp = weapon_recoil_h[current_weapon];
        
        set_val(PS4_RY, get_val(PS4_RY) + v_comp);
        set_val(PS4_RX, get_val(PS4_RX) - h_comp);
    }
    
    // RAPID FIRE
    if(mod_states[MOD_RAPID_FIRE] && weapon_rapid_fire[current_weapon]) {
        if(get_val(PS4_R2) > 10) {
            combo_run(rapid_fire_combo);
        }
    }
    
    // AIM ASSIST
    if(mod_states[MOD_AIM_ASSIST] && get_val(PS4_L2) > 10) {
        combo_run(aim_assist_combo);
        
        if(get_val(PS4_R2) > 10) {
            combo_run(rotation_assist_combo);
        }
    }
    
    // AUTO SPRINT
    if(mod_states[MOD_AUTO_SPRINT]) {
        if(abs(get_val(PS4_LY)) > 80 && get_val(PS4_L2) < 10) {
            combo_run(auto_sprint_combo);
        }
    }
    
    // SLIDE CANCEL
    if(mod_states[MOD_SLIDE_CANCEL]) {
        if(event_press(PS4_CIRCLE)) {
            combo_run(slide_cancel_combo);
        }
    }
    
    // BUNNY HOP
    if(mod_states[MOD_BUNNY_HOP]) {
        if(get_val(PS4_CROSS)) {
            combo_run(bunny_hop_combo);
        }
    }
    
    // DROP SHOT
    if(mod_states[MOD_DROP_SHOT]) {
        if(get_val(PS4_L2) > 10 && event_press(PS4_R2)) {
            combo_run(dropshot_combo);
        }
    }
    
    // JITTER
    if(mod_states[MOD_JITTER] && get_val(PS4_R2) > 10) {
        combo_run(jitter_combo);
    }
    
    // SNIPER BREATH
    if(mod_states[MOD_SNIPER_BREATH] && is_sniper && get_val(PS4_L2) > 10) {
        set_val(PS4_L3, 100);
    }
    
    // RELOAD CANCEL
    if(mod_states[MOD_QUICK_RELOAD]) {
        if(event_press(PS4_SQUARE)) {
            reload_start_time = system_time();
        }
        if((system_time() - reload_start_time) > 800 && (system_time() - reload_start_time) < 1500) {
            combo_run(reload_cancel_combo);
            reload_start_time = 0;
        }
    }
}

// ===================================================================
// COMBO DEFINITIONS
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
'''
    
    return script

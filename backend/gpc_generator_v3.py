"""
GPC Generator v3 - Based on WORKING BO7 structure
NO #include, pure GPC compatible with Zen Studio
"""

from typing import List, Dict
from datetime import datetime, timezone

def generate_working_gpc(weapons: List[Dict]) -> str:
    """Generate GPC script with PROVEN working structure (no #include)"""
    
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    weapon_count = len(weapons)
    
    # Header - NO #include, just comments and variables
    script = f'''// ZEN HUB PRO - MASTER SCRIPT v2.0
// Generated: {generation_time}
// Total Weapons: {weapon_count}
// Platform: PlayStation 5

// GLOBAL VARIABLES
int current_weapon;
int mod_states[10];
int menu_mode;
int menu_selection;

// WEAPON COUNT
#define WEAPON_COUNT {weapon_count}

// MOD DEFINITIONS
#define MOD_ANTI_RECOIL 0
#define MOD_RAPID_FIRE 1
#define MOD_AIM_ASSIST 2
#define MOD_SLIDE_CANCEL 3
#define MOD_AUTO_SPRINT 4
#define MOD_DROP_SHOT 5
#define MOD_BUNNY_HOP 6
#define MOD_JITTER 7
#define MOD_SNIPER_BREATH 8
#define MOD_RELOAD_CANCEL 9

// WEAPON DATA ARRAYS
int weapon_recoil_v[WEAPON_COUNT] = {{
'''
    
    # Add weapon data
    recoil_v_values = [str(w.get('vertical_recoil', 25)) for w in weapons]
    script += '    ' + ', '.join(recoil_v_values) + '\n};\n\n'
    
    script += 'int weapon_recoil_h[WEAPON_COUNT] = {\n'
    recoil_h_values = [str(w.get('horizontal_recoil', 10)) for w in weapons]
    script += '    ' + ', '.join(recoil_h_values) + '\n};\n\n'
    
    script += 'int weapon_fire_rate[WEAPON_COUNT] = {\n'
    fire_rate_values = [str(w.get('fire_rate', 700)) for w in weapons]
    script += '    ' + ', '.join(fire_rate_values) + '\n};\n\n'
    
    # Init block
    script += '''init {
    current_weapon = 0;
    menu_mode = 0;
    menu_selection = 0;
    
    int i;
    for(i = 0; i < 10; i++) {
        mod_states[i] = 1;
    }
}

main {
    // ANTI-RECOIL MOD
    if(mod_states[MOD_ANTI_RECOIL] && get_val(PS4_R2) > 10) {
        int v_comp = weapon_recoil_v[current_weapon];
        int h_comp = weapon_recoil_h[current_weapon];
        
        set_val(PS4_RY, get_val(PS4_RY) + v_comp);
        set_val(PS4_RX, get_val(PS4_RX) - h_comp);
    }
    
    // RAPID FIRE MOD
    if(mod_states[MOD_RAPID_FIRE] && get_val(PS4_R2) > 10) {
        combo_run(cRapidFire);
    }
    
    // AIM ASSIST MOD
    if(mod_states[MOD_AIM_ASSIST] && get_val(PS4_L2) > 10) {
        combo_run(cAimAssist);
    }
    
    // SLIDE CANCEL MOD
    if(mod_states[MOD_SLIDE_CANCEL] && event_press(PS4_CIRCLE)) {
        combo_run(cSlideCancel);
    }
    
    // AUTO SPRINT MOD
    if(mod_states[MOD_AUTO_SPRINT] && abs(get_val(PS4_LY)) > 80) {
        set_val(PS4_L3, 100);
    }
}

combo cRapidFire {
    set_val(PS4_R2, 100);
    wait(30);
    set_val(PS4_R2, 0);
    wait(30);
}

combo cAimAssist {
    set_val(PS4_RX, get_val(PS4_RX) + 5);
    wait(10);
}

combo cSlideCancel {
    set_val(PS4_CIRCLE, 100);
    wait(150);
    set_val(PS4_CIRCLE, 0);
    wait(50);
    set_val(PS4_CROSS, 100);
    wait(50);
}
'''
    
    return script

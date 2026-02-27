"""
ZEN HUB PRO - Advanced GPC Script Generator
Generates professional Cronus Zen scripts with OLED menu, spvar persistence, and modular architecture
"""

from typing import List, Dict
from datetime import datetime, timezone

def calculate_ttk(damage: int, fire_rate: int, hp: int = 250) -> int:
    """Calculate Time To Kill in milliseconds"""
    if not damage or not fire_rate:
        return 999
    shots_to_kill = (hp + damage - 1) // damage  # Ceiling division
    ttk_ms = int((60000 / fire_rate) * (shots_to_kill - 1))
    return ttk_ms

def generate_gpc_header(weapon_count: int, generation_time: str) -> str:
    """Generate GPC file header with ASCII art and info"""
    return f'''/*
 * ═══════════════════════════════════════════════════════════════
 * ZEN HUB PRO - MASTER SCRIPT ULTIMATE v2.0
 * Generated: {generation_time}
 * Total Weapons: {weapon_count}
 * ═══════════════════════════════════════════════════════════════
 * 
 * ██╗    ██╗ █████╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗███████╗
 * ██║    ██║██╔══██╗██╔══██╗╚══███╔╝██╔═══██╗████╗  ██║██╔════╝
 * ██║ █╗ ██║███████║██████╔╝  ███╔╝ ██║   ██║██╔██╗ ██║█████╗  
 * ██║███╗██║██╔══██║██╔══██╗ ███╔╝  ██║   ██║██║╚██╗██║██╔══╝  
 * ╚███╔███╔╝██║  ██║██║  ██║███████╗╚██████╔╝██║ ╚████║███████╗
 *  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
 *
 * ═══════════════════════════════════════════════════════════════
 * INTERACTIVE OLED MENU - NAVIGATE WITH CONTROLLER
 * ═══════════════════════════════════════════════════════════════
 * 
 * L1 + D-PAD UP/DOWN      : Navigate Menu
 * L1 + CROSS              : Toggle Selected Mod
 * L2 + D-PAD LEFT/RIGHT   : Change Weapon Profile
 * L1 + OPTIONS            : Save Settings to Flash
 * 
 * ═══════════════════════════════════════════════════════════════
 * MODS INCLUDED:
 * ═══════════════════════════════════════════════════════════════
 * 
 * 🎯 ANTI-RECOIL         : Custom per weapon (V + H)
 * 🔥 RAPID FIRE          : Semi-auto -> Full auto
 * 🎮 AIM ASSIST          : Sticky + Rotational Aim
 * ⚡ JITTER MOD          : Bypass fire rate cap
 * 🏃 AUTO TAC-SPRINT     : Automatic sprint
 * 🛝 SLIDE CANCEL V3     : Sprint -> Slide -> Jump
 * 🐰 BUNNY HOP           : Chain jumping
 * 💀 DROP SHOT           : Auto prone while shooting
 * 🫁 SNIPER BREATH       : Auto breath hold
 * 🔄 RELOAD CANCEL       : Cancel reload animation
 * 🎯 QUICK SCOPE         : Instant scope + fire
 * 
 * ═══════════════════════════════════════════════════════════════
 */

#pragma METAINFO("Zen Hub Pro Master", 2, 0, "ZenHub Pro")

#include <ps4.gph>
'''

def generate_gpc_defines(weapons: List[Dict]) -> str:
    """Generate all #define statements"""
    code = '''
// ═══════════════════════════════════════════════════════════════
// WEAPON DEFINITIONS
// ═══════════════════════════════════════════════════════════════

'''
    
    # Weapon count
    code += f'#define WEAPON_COUNT {len(weapons)}\n\n'
    
    # Weapon indices
    for idx, weapon in enumerate(weapons):
        safe_name = weapon['name'].upper().replace(' ', '_').replace('-', '_').replace('.', '')
        code += f'#define WPN_{safe_name} {idx}\n'
    
    code += '''

// ═══════════════════════════════════════════════════════════════
// MOD INDICES FOR MENU
// ═══════════════════════════════════════════════════════════════

#define MOD_ANTI_RECOIL     0
#define MOD_RAPID_FIRE      1
#define MOD_AIM_ASSIST      2
#define MOD_SLIDE_CANCEL    3
#define MOD_AUTO_SPRINT     4
#define MOD_DROP_SHOT       5
#define MOD_BUNNY_HOP       6
#define MOD_JITTER          7
#define MOD_SNIPER_BREATH   8
#define MOD_QUICK_RELOAD    9
#define MOD_COUNT           10

// ═══════════════════════════════════════════════════════════════
// SPVAR ADDRESSES (Persistent Storage)
// ═══════════════════════════════════════════════════════════════

#define SPVAR_CURRENT_WEAPON    0
#define SPVAR_MOD_STATES_START  1  // Mods 0-9 stored at SPVAR 1-10

// ═══════════════════════════════════════════════════════════════
// MENU SYSTEM
// ═══════════════════════════════════════════════════════════════

#define MENU_WEAPON_SELECT  0
#define MENU_MOD_TOGGLE     1

'''
    return code

def generate_gpc_data_arrays(weapons: List[Dict]) -> str:
    """Generate data arrays for weapons"""
    code = '''
// ═══════════════════════════════════════════════════════════════
// WEAPON DATA ARRAYS
// ═══════════════════════════════════════════════════════════════

'''
    
    # Vertical recoil array
    code += 'int weapon_recoil_v[WEAPON_COUNT] = {\n'
    code += '    ' + ', '.join([str(w.get('vertical_recoil', 25)) for w in weapons]) + '\n'
    code += '};\n\n'
    
    # Horizontal recoil array
    code += 'int weapon_recoil_h[WEAPON_COUNT] = {\n'
    code += '    ' + ', '.join([str(w.get('horizontal_recoil', 10)) for w in weapons]) + '\n'
    code += '};\n\n'
    
    # Fire rate array
    code += 'int weapon_fire_rate[WEAPON_COUNT] = {\n'
    code += '    ' + ', '.join([str(w.get('fire_rate', 700)) for w in weapons]) + '\n'
    code += '};\n\n'
    
    # Rapid fire enable
    code += 'int weapon_rapid_fire[WEAPON_COUNT] = {\n'
    code += '    ' + ', '.join(['TRUE' if w.get('rapid_fire', False) else 'FALSE' for w in weapons]) + '\n'
    code += '};\n\n'
    
    return code

def generate_gpc_variables() -> str:
    """Generate global variables"""
    return '''
// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════

int current_weapon = 0;
int menu_mode = MENU_WEAPON_SELECT;
int menu_selection = 0;
int oled_refresh_timer = 0;

// Mod states (loaded from SPVAR)
int mod_states[MOD_COUNT];

// Anti-recoil
int ar_release_time = 20;
int ar_active = FALSE;

// Timers
int last_shot_time = 0;
int reload_start_time = 0;

'''

def generate_gpc_init() -> str:
    """Generate init{} block"""
    return '''
// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════

init {
    // Load saved weapon from flash
    current_weapon = get_spvar(SPVAR_CURRENT_WEAPON);
    if(current_weapon < 0 || current_weapon >= WEAPON_COUNT) {
        current_weapon = 0;
    }
    
    // Load mod states from flash
    int i;
    for(i = 0; i < MOD_COUNT; i++) {
        mod_states[i] = get_spvar(SPVAR_MOD_STATES_START + i);
        if(mod_states[i] != TRUE && mod_states[i] != FALSE) {
            // Default: enable core mods
            if(i == MOD_ANTI_RECOIL || i == MOD_AIM_ASSIST || 
               i == MOD_AUTO_SPRINT || i == MOD_SLIDE_CANCEL) {
                mod_states[i] = TRUE;
            } else {
                mod_states[i] = FALSE;
            }
        }
    }
    
    // Force refresh OLED
    oled_refresh_timer = 999;
}

'''

def generate_gpc_main(weapon_count: int) -> str:
    """Generate main{} block with menu logic"""
    return f'''
// ═══════════════════════════════════════════════════════════════
// MAIN LOOP
// ═══════════════════════════════════════════════════════════════

main {{
    // ───────────────────────────────────────────────────────────
    // OLED MENU NAVIGATION
    // ───────────────────────────────────────────────────────────
    
    // Switch menu mode: L1 + Triangle
    if(get_val(PS4_L1) && event_press(PS4_TRIANGLE)) {{
        menu_mode = !menu_mode;
        menu_selection = 0;
        oled_refresh_timer = 999;
    }}
    
    // Navigate UP: L1 + D-PAD UP
    if(get_val(PS4_L1) && event_press(PS4_UP)) {{
        if(menu_mode == MENU_WEAPON_SELECT) {{
            menu_selection--;
            if(menu_selection < 0) menu_selection = {weapon_count - 1};
        }} else {{
            menu_selection--;
            if(menu_selection < 0) menu_selection = MOD_COUNT - 1;
        }}
        oled_refresh_timer = 999;
    }}
    
    // Navigate DOWN: L1 + D-PAD DOWN
    if(get_val(PS4_L1) && event_press(PS4_DOWN)) {{
        if(menu_mode == MENU_WEAPON_SELECT) {{
            menu_selection++;
            if(menu_selection >= {weapon_count}) menu_selection = 0;
        }} else {{
            menu_selection++;
            if(menu_selection >= MOD_COUNT) menu_selection = 0;
        }}
        oled_refresh_timer = 999;
    }}
    
    // SELECT: L1 + X (Cross)
    if(get_val(PS4_L1) && event_press(PS4_CROSS)) {{
        if(menu_mode == MENU_WEAPON_SELECT) {{
            current_weapon = menu_selection;
            set_spvar(SPVAR_CURRENT_WEAPON, current_weapon);
        }} else {{
            // Toggle mod
            mod_states[menu_selection] = !mod_states[menu_selection];
            set_spvar(SPVAR_MOD_STATES_START + menu_selection, mod_states[menu_selection]);
        }}
        oled_refresh_timer = 999;
    }}
    
    // Quick weapon change: L2 + D-PAD LEFT/RIGHT
    if(get_val(PS4_L2)) {{
        if(event_press(PS4_LEFT)) {{
            current_weapon--;
            if(current_weapon < 0) current_weapon = {weapon_count - 1};
            set_spvar(SPVAR_CURRENT_WEAPON, current_weapon);
            oled_refresh_timer = 999;
        }}
        if(event_press(PS4_RIGHT)) {{
            current_weapon++;
            if(current_weapon >= {weapon_count}) current_weapon = 0;
            set_spvar(SPVAR_CURRENT_WEAPON, current_weapon);
            oled_refresh_timer = 999;
        }}
    }}
    
    // ───────────────────────────────────────────────────────────
    // OLED DISPLAY UPDATE
    // ───────────────────────────────────────────────────────────
    
    oled_refresh_timer++;
    if(oled_refresh_timer > 100) {{  // Refresh every 100ms
        update_oled_display();
        oled_refresh_timer = 0;
    }}
    
    // ───────────────────────────────────────────────────────────
    // ANTI-RECOIL COMPENSATION
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_ANTI_RECOIL] && get_val(PS4_R2) > 10) {{
        if(!ar_active) {{
            ar_active = TRUE;
            wait(ar_release_time);
        }}
        
        // Apply recoil compensation
        int v_comp = weapon_recoil_v[current_weapon];
        int h_comp = weapon_recoil_h[current_weapon];
        
        set_val(PS4_RY, get_val(PS4_RY) + v_comp);
        set_val(PS4_RX, get_val(PS4_RX) - h_comp);
    }} else {{
        ar_active = FALSE;
    }}
    
    // ───────────────────────────────────────────────────────────
    // RAPID FIRE MOD
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_RAPID_FIRE] && weapon_rapid_fire[current_weapon]) {{
        if(get_val(PS4_R2) > 10) {{
            combo_run(rapid_fire_combo);
        }}
    }}
    
    // ───────────────────────────────────────────────────────────
    // AIM ASSIST (Sticky + Rotational)
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_AIM_ASSIST] && get_val(PS4_L2) > 10) {{
        combo_run(aim_assist_combo);
        
        if(get_val(PS4_R2) > 10) {{
            combo_run(rotation_assist_combo);
        }}
    }}
    
    // ───────────────────────────────────────────────────────────
    // AUTO TAC-SPRINT
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_AUTO_SPRINT]) {{
        if(abs(get_val(PS4_LY)) > 80 && get_val(PS4_L2) < 10) {{
            combo_run(auto_sprint_combo);
        }}
    }}
    
    // ───────────────────────────────────────────────────────────
    // SLIDE CANCEL
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_SLIDE_CANCEL]) {{
        if(event_press(PS4_CIRCLE)) {{
            combo_run(slide_cancel_combo);
        }}
    }}
    
    // ───────────────────────────────────────────────────────────
    // BUNNY HOP
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_BUNNY_HOP]) {{
        if(get_val(PS4_CROSS)) {{
            combo_run(bunny_hop_combo);
        }}
    }}
    
    // ───────────────────────────────────────────────────────────
    // DROP SHOT
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_DROP_SHOT]) {{
        if(get_val(PS4_L2) > 10 && event_press(PS4_R2)) {{
            combo_run(dropshot_combo);
        }}
    }}
    
    // ───────────────────────────────────────────────────────────
    // JITTER MOD (Use with caution)
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_JITTER] && get_val(PS4_R2) > 10) {{
        combo_run(jitter_combo);
    }}
    
    // ───────────────────────────────────────────────────────────
    // SNIPER BREATH HOLD
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_SNIPER_BREATH] && get_val(PS4_L2) > 10) {{
        set_val(PS4_L3, 100);
    }}
    
    // ───────────────────────────────────────────────────────────
    // QUICK RELOAD CANCEL
    // ───────────────────────────────────────────────────────────
    
    if(mod_states[MOD_QUICK_RELOAD]) {{
        if(event_press(PS4_SQUARE)) {{
            reload_start_time = system_time();
        }}
        if((system_time() - reload_start_time) > 800 && (system_time() - reload_start_time) < 1500) {{
            combo_run(reload_cancel_combo);
            reload_start_time = 0;
        }}
    }}
}}

'''

def generate_oled_functions(weapons: List[Dict]) -> str:
    """Generate OLED display functions"""
    
    # Create weapon names array
    weapon_names = []
    for w in weapons[:20]:  # Limit to 20 for display
        name = w['name'][:16]  # Max 16 chars for OLED
        weapon_names.append(f'    "{name}"')
    
    weapon_names_str = ',\n'.join(weapon_names)
    
    # Mod names
    mod_names = [
        'Anti-Recoil',
        'Rapid Fire',
        'Aim Assist',
        'Slide Cancel',
        'Auto Sprint',
        'Drop Shot',
        'Bunny Hop',
        'Jitter Mod',
        'Sniper Breath',
        'Quick Reload'
    ]
    
    mod_names_str = ',\n'.join([f'    "{name}"' for name in mod_names])
    
    code = f'''
// ═══════════════════════════════════════════════════════════════
// OLED DISPLAY FUNCTIONS
// ═══════════════════════════════════════════════════════════════

char weapon_names[{min(len(weapons), 20)}][17] = {{
{weapon_names_str}
}};

char mod_names[MOD_COUNT][17] = {{
{mod_names_str}
}};

function update_oled_display() {{
    cls_oled();
    
    if(menu_mode == MENU_WEAPON_SELECT) {{
        // Weapon selection menu
        printf_oled(0, 0, "== WEAPON SELECT ==");
        
        int start_idx = menu_selection - 2;
        if(start_idx < 0) start_idx = 0;
        
        int i;
        for(i = 0; i < 5 && (start_idx + i) < WEAPON_COUNT; i++) {{
            int weapon_idx = start_idx + i;
            int line = i + 1;
            
            if(weapon_idx == current_weapon) {{
                printf_oled(line, 0, "> [%s]", weapon_names[weapon_idx]);
            }} else if(weapon_idx == menu_selection) {{
                printf_oled(line, 0, "  %s <-", weapon_names[weapon_idx]);
            }} else {{
                printf_oled(line, 0, "  %s", weapon_names[weapon_idx]);
            }}
        }}
        
        printf_oled(6, 0, "L1+Y: Mods Menu");
    }} else {{
        // Mod toggle menu
        printf_oled(0, 0, "===== MODS =====");
        
        int start_idx = menu_selection - 2;
        if(start_idx < 0) start_idx = 0;
        
        int i;
        for(i = 0; i < 5 && (start_idx + i) < MOD_COUNT; i++) {{
            int mod_idx = start_idx + i;
            int line = i + 1;
            
            char status = mod_states[mod_idx] ? 'ON' : 'OFF';
            
            if(mod_idx == menu_selection) {{
                printf_oled(line, 0, "> %s [%s]", mod_names[mod_idx], (mod_states[mod_idx] ? "ON" : "OFF"));
            }} else {{
                printf_oled(line, 0, "  %s [%s]", mod_names[mod_idx], (mod_states[mod_idx] ? "ON" : "OFF"));
            }}
        }}
        
        printf_oled(6, 0, "L1+Y: Weapons");
    }}
}}

'''
    return code

def generate_gpc_combos() -> str:
    """Generate combo definitions"""
    return '''
// ═══════════════════════════════════════════════════════════════
// COMBO DEFINITIONS
// ═══════════════════════════════════════════════════════════════

combo rapid_fire_combo {
    set_val(XB1_RT, 100);
    wait(30);
    set_val(XB1_RT, 0);
    wait(30);
}

combo aim_assist_combo {
    set_val(XB1_RX, get_val(XB1_RX) + 10);
    wait(10);
    set_val(XB1_RX, get_val(XB1_RX) - 10);
    wait(10);
}

combo rotation_assist_combo {
    if(abs(get_val(XB1_RX)) > 5) {
        set_val(XB1_RX, get_val(XB1_RX) + (get_val(XB1_RX) > 0 ? 15 : -15));
    }
}

combo auto_sprint_combo {
    set_val(XB1_LS, 100);
    wait(100);
    set_val(XB1_LS, 0);
    wait(50);
    set_val(XB1_LS, 100);
    wait(100);
}

combo slide_cancel_combo {
    set_val(XB1_B, 100);
    wait(180);
    set_val(XB1_B, 0);
    wait(50);
    set_val(XB1_A, 100);
    wait(50);
    set_val(XB1_A, 0);
    wait(50);
    set_val(XB1_LS, 100);
    wait(50);
    set_val(XB1_LS, 0);
}

combo bunny_hop_combo {
    set_val(XB1_A, 100);
    wait(40);
    set_val(XB1_A, 0);
    wait(40);
}

combo dropshot_combo {
    set_val(XB1_RT, 100);
    wait(30);
    set_val(XB1_B, 100);
    wait(100);
    wait(500);
    set_val(XB1_B, 0);
}

combo jitter_combo {
    set_val(XB1_RX, 50);
    wait(20);
    set_val(XB1_RX, -50);
    wait(20);
}

combo reload_cancel_combo {
    set_val(XB1_LS, 100);
    wait(50);
    set_val(XB1_LS, 0);
    wait(30);
    set_val(XB1_Y, 100);
    wait(50);
    set_val(XB1_Y, 0);
    wait(50);
    set_val(XB1_Y, 100);
    wait(50);
    set_val(XB1_Y, 0);
}

'''

def generate_master_script_advanced(weapons: List[Dict]) -> str:
    """
    Generate a complete advanced GPC script with OLED menu
    """
    generation_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    script_parts = [
        generate_gpc_header(len(weapons), generation_time),
        generate_gpc_defines(weapons),
        generate_gpc_data_arrays(weapons),
        generate_gpc_variables(),
        generate_gpc_init(),
        generate_gpc_main(len(weapons)),
        generate_oled_functions(weapons),
        generate_gpc_combos()
    ]
    
    return '\n'.join(script_parts)

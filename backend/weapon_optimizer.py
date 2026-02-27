"""
Weapon Build Optimizer for Cronus Zen
Calculates optimal builds with max damage/fire rate
"""

from typing import Dict, Tuple

# Accessoire impacts (basé sur meta COD Warzone)
ACCESSORY_IMPACTS = {
    # Barrels
    "short_barrel": {
        "fire_rate_mult": 1.12,
        "recoil_v_mult": 1.25,
        "recoil_h_mult": 1.15,
        "damage_mult": 1.0,
    },
    "long_barrel": {
        "fire_rate_mult": 0.95,
        "recoil_v_mult": 1.10,
        "recoil_h_mult": 1.15,
        "damage_mult": 1.10,
        "range_mult": 1.25,
    },
    "rapid_fire_barrel": {
        "fire_rate_mult": 1.15,
        "recoil_v_mult": 1.30,
        "recoil_h_mult": 1.20,
        "damage_mult": 0.95,
    },
    
    # Ammo
    "hollow_point": {
        "damage_mult": 1.20,
        "recoil_v_mult": 1.15,
        "recoil_h_mult": 1.15,
    },
    "high_velocity": {
        "recoil_v_mult": 1.10,
        "range_mult": 1.20,
    },
    "high_grain": {
        "damage_mult": 1.15,
        "recoil_v_mult": 1.20,
        "recoil_h_mult": 1.10,
    },
    
    # Stocks
    "no_stock": {
        "recoil_v_mult": 1.40,
        "recoil_h_mult": 1.35,
        "ads_mult": 1.20,
    },
    "lightweight_stock": {
        "recoil_v_mult": 1.20,
        "recoil_h_mult": 1.15,
        "ads_mult": 1.15,
    },
    
    # Underbarrel
    "laser": {
        "hip_fire_mult": 1.30,
    },
    
    # Mags
    "extended_mag": {},
    "drum_mag": {},
}

def calculate_optimized_stats(
    base_damage: int,
    base_fire_rate: int,
    base_recoil_v: int,
    base_recoil_h: int,
    weapon_category: str
) -> Dict:
    """
    Calculate optimized weapon stats with max damage/fire rate build
    
    Returns optimized stats and recommended build
    """
    
    # Build strategy based on category
    if weapon_category in ["SMG", "PISTOL"]:
        # SMG/Pistol: Prioritize FIRE RATE
        build = {
            "barrel": "rapid_fire_barrel",
            "ammo": "high_grain",
            "stock": "no_stock",
            "underbarrel": "laser",
            "mag": "extended_mag"
        }
    elif weapon_category in ["AR"]:
        # AR: Balance DAMAGE + FIRE RATE
        build = {
            "barrel": "short_barrel",
            "ammo": "hollow_point",
            "stock": "no_stock",
            "underbarrel": "laser",
            "mag": "extended_mag"
        }
    elif weapon_category in ["LMG"]:
        # LMG: Max DAMAGE
        build = {
            "barrel": "long_barrel",
            "ammo": "hollow_point",
            "stock": "lightweight_stock",
            "underbarrel": "laser",
            "mag": "drum_mag"
        }
    elif weapon_category in ["SNIPER"]:
        # Sniper: Max DAMAGE + RANGE
        build = {
            "barrel": "long_barrel",
            "ammo": "high_velocity",
            "stock": "lightweight_stock",
            "underbarrel": None,
            "mag": "extended_mag"
        }
    else:
        # Default
        build = {
            "barrel": "short_barrel",
            "ammo": "hollow_point",
            "stock": "no_stock",
            "underbarrel": "laser",
            "mag": "extended_mag"
        }
    
    # Calculate multipliers
    fire_rate_mult = 1.0
    damage_mult = 1.0
    recoil_v_mult = 1.0
    recoil_h_mult = 1.0
    range_mult = 1.0
    
    for accessory_type, accessory_name in build.items():
        if accessory_name and accessory_name in ACCESSORY_IMPACTS:
            impact = ACCESSORY_IMPACTS[accessory_name]
            fire_rate_mult *= impact.get("fire_rate_mult", 1.0)
            damage_mult *= impact.get("damage_mult", 1.0)
            recoil_v_mult *= impact.get("recoil_v_mult", 1.0)
            recoil_h_mult *= impact.get("recoil_h_mult", 1.0)
            range_mult *= impact.get("range_mult", 1.0)
    
    # Apply multipliers
    optimized_fire_rate = int(base_fire_rate * fire_rate_mult)
    optimized_damage = int(base_damage * damage_mult)
    optimized_recoil_v = int(base_recoil_v * recoil_v_mult)
    optimized_recoil_h = int(base_recoil_h * recoil_h_mult)
    
    # Calculate TTK (assuming 250 HP)
    shots_to_kill = max(1, (250 + optimized_damage - 1) // optimized_damage)
    ttk_ms = int((60000 / optimized_fire_rate) * (shots_to_kill - 1))
    
    # Base TTK for comparison
    base_shots_to_kill = max(1, (250 + base_damage - 1) // base_damage)
    base_ttk_ms = int((60000 / base_fire_rate) * (base_shots_to_kill - 1))
    
    return {
        "build": build,
        "optimized_fire_rate": optimized_fire_rate,
        "optimized_damage": optimized_damage,
        "optimized_recoil_v": optimized_recoil_v,
        "optimized_recoil_h": optimized_recoil_h,
        "optimized_ttk": ttk_ms,
        "base_ttk": base_ttk_ms,
        "ttk_improvement": base_ttk_ms - ttk_ms,
        "ttk_improvement_percent": int(((base_ttk_ms - ttk_ms) / base_ttk_ms) * 100) if base_ttk_ms > 0 else 0
    }

def format_build_string(build: Dict) -> str:
    """Format build dict to readable string in FRENCH"""
    accessory_names = {
        "rapid_fire_barrel": "Canon Cadence Rapide",
        "short_barrel": "Canon Court",
        "long_barrel": "Canon Long",
        "hollow_point": "Munitions Pointe Creuse",
        "high_grain": "Munitions Haute Grain",
        "high_velocity": "Munitions Haute Vélocité",
        "no_stock": "Pas de Crosse",
        "lightweight_stock": "Crosse Légère",
        "laser": "Viseur Laser",
        "extended_mag": "Chargeur Étendu",
        "drum_mag": "Chargeur Tambour",
    }
    
    parts = []
    for accessory_type, accessory_name in build.items():
        if accessory_name:
            parts.append(accessory_names.get(accessory_name, accessory_name))
    
    return " + ".join(parts)

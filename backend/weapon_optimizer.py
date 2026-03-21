"""
Weapon Build Optimizer for Cronus Zen
Calculates Cronus-aware builds with high TTK and controllable recoil
"""

from typing import Dict, List

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

BUILD_CANDIDATES = {
    "SMG": [
        {
            "name": "ttk_agressif",
            "parts": {
                "barrel": "rapid_fire_barrel",
                "ammo": "high_grain",
                "stock": "lightweight_stock",
                "underbarrel": "laser",
                "mag": "extended_mag",
            },
        },
        {
            "name": "equilibre_cronus",
            "parts": {
                "barrel": "short_barrel",
                "ammo": "high_grain",
                "stock": "lightweight_stock",
                "underbarrel": "laser",
                "mag": "extended_mag",
            },
        },
    ],
    "PISTOL": [
        {
            "name": "equilibre_cronus",
            "parts": {
                "barrel": "short_barrel",
                "ammo": "high_grain",
                "stock": "lightweight_stock",
                "underbarrel": "laser",
                "mag": "extended_mag",
            },
        }
    ],
    "AR": [
        {
            "name": "equilibre_cronus",
            "parts": {
                "barrel": "short_barrel",
                "ammo": "hollow_point",
                "stock": "lightweight_stock",
                "underbarrel": "laser",
                "mag": "extended_mag",
            },
        },
        {
            "name": "stabilite_dps",
            "parts": {
                "barrel": "long_barrel",
                "ammo": "hollow_point",
                "stock": "lightweight_stock",
                "underbarrel": "laser",
                "mag": "extended_mag",
            },
        },
    ],
    "LMG": [
        {
            "name": "stabilite_dps",
            "parts": {
                "barrel": "long_barrel",
                "ammo": "hollow_point",
                "stock": "lightweight_stock",
                "underbarrel": "laser",
                "mag": "drum_mag",
            },
        }
    ],
    "SNIPER": [
        {
            "name": "stabilite_dps",
            "parts": {
                "barrel": "long_barrel",
                "ammo": "high_velocity",
                "stock": "lightweight_stock",
                "underbarrel": None,
                "mag": "extended_mag",
            },
        }
    ],
}


def _calc_ttk_ms(damage: int, fire_rate: int) -> int:
    shots_to_kill = max(1, (250 + damage - 1) // damage)
    return int((60000 / max(1, fire_rate)) * max(0, shots_to_kill - 1))


def _score_build(base_ttk: int, optimized_ttk: int, recoil_v: int, recoil_h: int) -> int:
    ttk_gain = max(0, base_ttk - optimized_ttk)
    recoil_penalty = int((recoil_v * 1.2) + (recoil_h * 0.9))
    return (ttk_gain * 2) - recoil_penalty


def _pick_candidates(category: str) -> List[Dict]:
    normalized = (category or "").upper()
    if normalized in BUILD_CANDIDATES:
        return BUILD_CANDIDATES[normalized]
    return BUILD_CANDIDATES["AR"]


def _compute_script_compensation(optimized_recoil_v: int, optimized_recoil_h: int) -> Dict:
    script_vertical = max(8, min(60, int(round(optimized_recoil_v * 0.90))))
    script_horizontal = max(-35, min(35, int(round(optimized_recoil_h * 0.80))))
    burst_boost = max(2, min(8, int(round(script_vertical * 0.12))))
    return {
        "script_vertical": script_vertical,
        "script_horizontal": script_horizontal,
        "script_burst_boost": burst_boost,
    }

def calculate_optimized_stats(
    base_damage: int,
    base_fire_rate: int,
    base_recoil_v: int,
    base_recoil_h: int,
    weapon_category: str
) -> Dict:
    """
    Calculate optimized weapon stats for Cronus:
    - Keeps strong TTK
    - Avoids unstable recoil spikes
    
    Returns optimized stats and recommended build
    """
    base_ttk_ms = _calc_ttk_ms(base_damage, base_fire_rate)

    best_result = None
    for candidate in _pick_candidates(weapon_category):
        build = candidate["parts"]

        fire_rate_mult = 1.0
        damage_mult = 1.0
        recoil_v_mult = 1.0
        recoil_h_mult = 1.0

        for _, accessory_name in build.items():
            if accessory_name and accessory_name in ACCESSORY_IMPACTS:
                impact = ACCESSORY_IMPACTS[accessory_name]
                fire_rate_mult *= impact.get("fire_rate_mult", 1.0)
                damage_mult *= impact.get("damage_mult", 1.0)
                recoil_v_mult *= impact.get("recoil_v_mult", 1.0)
                recoil_h_mult *= impact.get("recoil_h_mult", 1.0)

        optimized_fire_rate = int(base_fire_rate * fire_rate_mult)
        optimized_damage = int(base_damage * damage_mult)
        optimized_recoil_v = int(base_recoil_v * recoil_v_mult)
        optimized_recoil_h = int(base_recoil_h * recoil_h_mult)
        optimized_ttk = _calc_ttk_ms(optimized_damage, optimized_fire_rate)
        score = _score_build(base_ttk_ms, optimized_ttk, optimized_recoil_v, optimized_recoil_h)

        result = {
            "build_name": candidate["name"],
            "build": build,
            "optimized_fire_rate": optimized_fire_rate,
            "optimized_damage": optimized_damage,
            "optimized_recoil_v": optimized_recoil_v,
            "optimized_recoil_h": optimized_recoil_h,
            "optimized_ttk": optimized_ttk,
            "score": score,
        }

        if best_result is None or result["score"] > best_result["score"]:
            best_result = result

    compensation = _compute_script_compensation(
        best_result["optimized_recoil_v"],
        best_result["optimized_recoil_h"],
    )

    stability_index = max(
        0,
        100 - int((best_result["optimized_recoil_v"] * 1.1) + (best_result["optimized_recoil_h"] * 0.8)),
    )

    return {
        "build_name": best_result["build_name"],
        "build": best_result["build"],
        "optimized_fire_rate": best_result["optimized_fire_rate"],
        "optimized_damage": best_result["optimized_damage"],
        "optimized_recoil_v": best_result["optimized_recoil_v"],
        "optimized_recoil_h": best_result["optimized_recoil_h"],
        "optimized_ttk": best_result["optimized_ttk"],
        "base_ttk": base_ttk_ms,
        "ttk_improvement": base_ttk_ms - best_result["optimized_ttk"],
        "ttk_improvement_percent": int(((base_ttk_ms - best_result["optimized_ttk"]) / base_ttk_ms) * 100) if base_ttk_ms > 0 else 0,
        "stability_index": stability_index,
        "score": best_result["score"],
        **compensation,
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

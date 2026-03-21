"""
🔥 EN-HANCED WEAPON OPTIMIZER PRO - 3 PROFILS DE COMBAT
Système avancé de calcul d'optimisation avec awareness contexte
"""

from typing import Dict, List, Optional

# Accessoire impacts (amélioré avec accuracy + reload)
ACCESSORY_IMPACTS = {
    # Barrels
    "short_barrel": {
        "fire_rate_mult": 1.12,
        "recoil_v_mult": 1.25,
        "recoil_h_mult": 1.15,
        "damage_mult": 1.0,
        "accuracy_mult": 0.95,
        "reload_mult": 0.98,
    },
    "long_barrel": {
        "fire_rate_mult": 0.95,
        "recoil_v_mult": 1.10,
        "recoil_h_mult": 1.15,
        "damage_mult": 1.10,
        "range_mult": 1.25,
        "accuracy_mult": 1.15,
        "reload_mult": 1.05,
    },
    "rapid_fire_barrel": {
        "fire_rate_mult": 1.15,
        "recoil_v_mult": 1.30,
        "recoil_h_mult": 1.20,
        "damage_mult": 0.95,
        "accuracy_mult": 0.88,
        "reload_mult": 0.95,
    },
    
    # Ammo
    "hollow_point": {
        "damage_mult": 1.20,
        "recoil_v_mult": 1.15,
        "recoil_h_mult": 1.15,
        "accuracy_mult": 0.98,
    },
    "high_velocity": {
        "recoil_v_mult": 1.10,
        "range_mult": 1.20,
        "accuracy_mult": 1.08,
    },
    "high_grain": {
        "damage_mult": 1.15,
        "recoil_v_mult": 1.20,
        "recoil_h_mult": 1.10,
        "accuracy_mult": 1.05,
    },
    
    # Stocks
    "no_stock": {
        "recoil_v_mult": 1.40,
        "recoil_h_mult": 1.35,
        "ads_mult": 1.20,
        "accuracy_mult": 0.75,
        "reload_mult": 1.15,
    },
    "lightweight_stock": {
        "recoil_v_mult": 1.20,
        "recoil_h_mult": 1.15,
        "ads_mult": 1.15,
        "accuracy_mult": 0.92,
        "reload_mult": 1.08,
    },
    
    # Underbarrel
    "laser": {
        "hip_fire_mult": 1.30,
        "accuracy_mult": 1.12,
    },
    
    # Mags
    "extended_mag": {
        "reload_mult": 1.10,
    },
    "drum_mag": {
        "reload_mult": 1.20,
    },
}

# ✅ 3 PROFILS DE COMBAT
BUILD_CANDIDATES = {
    "AGRESSIF": {
        "description": "Rusheur - Max TTK, Accuracy sacrifiée",
        "ttk_weight": 3.0,
        "recoil_penalty": 0.5,  # Moins pénalisant sur recoil
        "accuracy_bonus": 0.3,
        "candidates": {
            "SMG": {
                "name": "rush_ttk",
                "parts": {
                    "barrel": "rapid_fire_barrel",
                    "ammo": "high_grain",
                    "stock": "no_stock",
                    "underbarrel": "laser",
                    "mag": "extended_mag",
                },
            },
            "AR": {
                "name": "rush_ttk",
                "parts": {
                    "barrel": "short_barrel",
                    "ammo": "hollow_point",
                    "stock": "no_stock",
                    "underbarrel": "laser",
                    "mag": "extended_mag",
                },
            },
            "PISTOL": {
                "name": "rush_ttk",
                "parts": {
                    "barrel": "short_barrel",
                    "ammo": "high_grain",
                    "stock": "no_stock",
                    "underbarrel": "laser",
                    "mag": "extended_mag",
                },
            },
        },
    },
    "EQUILIBRE": {
        "description": "Polyvalent - TTK + Stabilité",
        "ttk_weight": 2.0,
        "recoil_penalty": 1.2,
        "accuracy_bonus": 1.0,
        "candidates": {
            "SMG": {
                "name": "balanced",
                "parts": {
                    "barrel": "short_barrel",
                    "ammo": "high_grain",
                    "stock": "lightweight_stock",
                    "underbarrel": "laser",
                    "mag": "extended_mag",
                },
            },
            "AR": {
                "name": "balanced",
                "parts": {
                    "barrel": "short_barrel",
                    "ammo": "hollow_point",
                    "stock": "lightweight_stock",
                    "underbarrel": "laser",
                    "mag": "extended_mag",
                },
            },
            "PISTOL": {
                "name": "balanced",
                "parts": {
                    "barrel": "short_barrel",
                    "ammo": "hollow_point",
                    "stock": "lightweight_stock",
                    "underbarrel": "laser",
                    "mag": "extended_mag",
                },
            },
        },
    },
    "SNIPER": {
        "description": "Longue distance - Stabilité + Accuracy",
        "ttk_weight": 1.0,
        "recoil_penalty": 2.5,
        "accuracy_bonus": 2.0,
        "candidates": {
            "SNIPER": {
                "name": "precision",
                "parts": {
                    "barrel": "long_barrel",
                    "ammo": "high_velocity",
                    "stock": "lightweight_stock",
                    "underbarrel": None,
                    "mag": "extended_mag",
                },
            },
            "AR": {
                "name": "precision",
                "parts": {
                    "barrel": "long_barrel",
                    "ammo": "high_velocity",
                    "stock": "lightweight_stock",
                    "underbarrel": None,
                    "mag": "extended_mag",
                },
            },
            "MARKSMAN": {
                "name": "precision",
                "parts": {
                    "barrel": "long_barrel",
                    "ammo": "high_velocity",
                    "stock": "lightweight_stock",
                    "underbarrel": None,
                    "mag": "extended_mag",
                },
            },
        },
    },
}


def _calc_ttk_ms(damage: int, fire_rate: int) -> int:
    """Calcul TTK en millisecondes"""
    shots_to_kill = max(1, (250 + damage - 1) // damage)
    return int((60000 / max(1, fire_rate)) * max(0, shots_to_kill - 1))


def _score_build_advanced(
    base_ttk: int,
    optimized_ttk: int,
    recoil_v: int,
    recoil_h: int,
    accuracy: int,
    profile_config: Dict,
) -> int:
    """
    Scoring avancé avec profils
    """
    ttk_gain = max(0, base_ttk - optimized_ttk)
    recoil_penalty = int((recoil_v * 1.2) + (recoil_h * 0.9))
    
    # Scoring multi-dimensionnel
    score = (
        (ttk_gain * profile_config["ttk_weight"]) -
        (recoil_penalty * profile_config["recoil_penalty"]) +
        (accuracy * profile_config["accuracy_bonus"])
    )
    
    return int(score)


def _compute_script_compensation_adaptive(
    optimized_recoil_v: int,
    optimized_recoil_h: int,
    profile_mode: str,
) -> Dict:
    """
    Compensation adaptative selon le profil
    AGRESSIF = moins de compensation (réactivité)
    SNIPER = plus de compensation (précision)
    """
    if profile_mode == "AGRESSIF":
        script_vertical = max(6, min(50, int(round(optimized_recoil_v * 0.75))))
        script_horizontal = max(-30, min(30, int(round(optimized_recoil_h * 0.70))))
        burst_boost = max(3, min(10, int(round(script_vertical * 0.15))))
    elif profile_mode == "SNIPER":
        script_vertical = max(12, min(70, int(round(optimized_recoil_v * 1.10))))
        script_horizontal = max(-40, min(40, int(round(optimized_recoil_h * 0.95))))
        burst_boost = max(1, min(4, int(round(script_vertical * 0.08))))
    else:  # EQUILIBRE
        script_vertical = max(8, min(60, int(round(optimized_recoil_v * 0.90))))
        script_horizontal = max(-35, min(35, int(round(optimized_recoil_h * 0.80))))
        burst_boost = max(2, min(8, int(round(script_vertical * 0.12))))
    
    return {
        "script_vertical": script_vertical,
        "script_horizontal": script_horizontal,
        "script_burst_boost": burst_boost,
    }


def calculate_optimized_stats_pro(
    base_damage: int,
    base_fire_rate: int,
    base_recoil_v: int,
    base_recoil_h: int,
    weapon_category: str,
    profile_mode: str = "EQUILIBRE",
) -> Dict:
    """
    Calcul d'optimisation PRO avec 3 profils
    - AGRESSIF: Rusheur, max TTK
    - EQUILIBRE: Polyvalent, balance
    - SNIPER: Longue distance, stabilité
    """
    
    if profile_mode not in BUILD_CANDIDATES:
        profile_mode = "EQUILIBRE"
    
    profile_config = BUILD_CANDIDATES[profile_mode]
    base_ttk_ms = _calc_ttk_ms(base_damage, base_fire_rate)
    
    # Récupérer les candidats pour cette arme
    normalized_cat = (weapon_category or "").upper()
    candidate_build = profile_config["candidates"].get(
        normalized_cat,
        profile_config["candidates"]["AR"]
    )
    
    build = candidate_build["parts"]
    
    # Appliquer les multiplicateurs
    fire_rate_mult = 1.0
    damage_mult = 1.0
    recoil_v_mult = 1.0
    recoil_h_mult = 1.0
    accuracy_mult = 1.0
    reload_mult = 1.0
    
    for _, accessory_name in build.items():
        if accessory_name and accessory_name in ACCESSORY_IMPACTS:
            impact = ACCESSORY_IMPACTS[accessory_name]
            fire_rate_mult *= impact.get("fire_rate_mult", 1.0)
            damage_mult *= impact.get("damage_mult", 1.0)
            recoil_v_mult *= impact.get("recoil_v_mult", 1.0)
            recoil_h_mult *= impact.get("recoil_h_mult", 1.0)
            accuracy_mult *= impact.get("accuracy_mult", 1.0)
            reload_mult *= impact.get("reload_mult", 1.0)
    
    optimized_fire_rate = int(base_fire_rate * fire_rate_mult)
    optimized_damage = int(base_damage * damage_mult)
    optimized_recoil_v = int(base_recoil_v * recoil_v_mult)
    optimized_recoil_h = int(base_recoil_h * recoil_h_mult)
    optimized_accuracy = int(100 * accuracy_mult)
    optimized_reload = int(2500 * reload_mult)  # Reload time en ms
    optimized_ttk = _calc_ttk_ms(optimized_damage, optimized_fire_rate)
    
    score = _score_build_advanced(
        base_ttk_ms, optimized_ttk, optimized_recoil_v, optimized_recoil_h,
        optimized_accuracy, profile_config
    )
    
    # Compensation adaptative  
    compensation = _compute_script_compensation_adaptive(
        optimized_recoil_v, optimized_recoil_h, profile_mode
    )
    
    # Index de stabilité amélioré
    stability_index = max(
        0,
        100 - int((optimized_recoil_v * 1.1) + (optimized_recoil_h * 0.8)),
    )
    
    return {
        "profile_mode": profile_mode,
        "profile_description": profile_config["description"],
        "build_name": candidate_build["name"],
        "build": build,
        "optimized_fire_rate": optimized_fire_rate,
        "optimized_damage": optimized_damage,
        "optimized_recoil_v": optimized_recoil_v,
        "optimized_recoil_h": optimized_recoil_h,
        "optimized_accuracy": optimized_accuracy,
        "optimized_reload": optimized_reload,
        "optimized_ttk": optimized_ttk,
        "base_ttk": base_ttk_ms,
        "ttk_improvement": base_ttk_ms - optimized_ttk,
        "ttk_improvement_percent": int(((base_ttk_ms - optimized_ttk) / base_ttk_ms) * 100) if base_ttk_ms > 0 else 0,
        "stability_index": stability_index,
        "accuracy_score": optimized_accuracy,
        "reload_ms": optimized_reload,
        "score": score,
        **compensation,
    }


def compare_all_profiles(
    base_damage: int,
    base_fire_rate: int,
    base_recoil_v: int,
    base_recoil_h: int,
    weapon_category: str,
) -> Dict[str, Dict]:
    """
    Compare tous les profils pour une arme
    Retourne les 3 optimisations possible
    """
    results = {}
    for profile in ["AGRESSIF", "EQUILIBRE", "SNIPER"]:
        results[profile] = calculate_optimized_stats_pro(
            base_damage, base_fire_rate, base_recoil_v, base_recoil_h,
            weapon_category, profile
        )
    return results


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

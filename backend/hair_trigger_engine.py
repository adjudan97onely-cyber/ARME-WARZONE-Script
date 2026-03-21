"""
🎯 ADVANCED HAIR TRIGGER SYSTEM
Micro-patterns de réactivité spécifiques par arme
Optimisation Cronus Zen avec variables adaptatives
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class WeaponClass(Enum):
    """Classifications d'armes pour micro-patterns"""
    SNIPER = "sniper"
    MARKSMAN = "marksman"
    AR = "ar"
    SMG = "smg"
    LMG = "lmg"
    SHOTGUN = "shotgun"
    PISTOL = "pistol"


@dataclass
class HairTriggerProfile:
    """Profil de Hair Trigger pour une arme"""
    weapon_name: str
    weapon_class: WeaponClass
    ramp_time_ms: int  # Temps de montée en charge (ms)
    sensitivity_threshold: float  # % de pression avant trigger
    micro_adjust_delay: int  # Délai micro-ajustement (ms)
    sustained_fire_boost: bool  # Boost auto sur tirs soutenus
    boost_delay_ticks: int  # Nombre de ticks avant boost (8ms par tick)
    stabilizer_strength: int  # Force du stabiliseur (0-100)
    aa_sync: bool  # Sync avec Aim Assist


@dataclass  
class HairTriggerGPCCode:
    """Code GPC généré pour Hair Trigger avancé"""
    init_vars: str
    main_loop: str
    combo_section: str


class AdvancedHairTriggerEngine:
    """
    Moteur de Hair Trigger optimisé Cronus Zen
    Génère code GPC spécifique avec micro-patterns
    """
    
    # Profils par classe d'arme
    BASE_PROFILES = {
        WeaponClass.SNIPER: {
            "ramp_time_ms": 450,
            "sensitivity_threshold": 0.92,
            "micro_adjust_delay": 120,
            "sustained_fire_boost": False,
            "boost_delay_ticks": 0,
            "stabilizer_strength": 85,
            "aa_sync": False,
        },
        WeaponClass.MARKSMAN: {
            "ramp_time_ms": 350,
            "sensitivity_threshold": 0.88,
            "micro_adjust_delay": 100,
            "sustained_fire_boost": True,
            "boost_delay_ticks": 3,
            "stabilizer_strength": 75,
            "aa_sync": True,
        },
        WeaponClass.AR: {
            "ramp_time_ms": 280,
            "sensitivity_threshold": 0.80,
            "micro_adjust_delay": 80,
            "sustained_fire_boost": True,
            "boost_delay_ticks": 5,
            "stabilizer_strength": 60,
            "aa_sync": True,
        },
        WeaponClass.SMG: {
            "ramp_time_ms": 200,
            "sensitivity_threshold": 0.75,
            "micro_adjust_delay": 60,
            "sustained_fire_boost": True,
            "boost_delay_ticks": 4,
            "stabilizer_strength": 50,
            "aa_sync": True,
        },
        WeaponClass.LMG: {
            "ramp_time_ms": 320,
            "sensitivity_threshold": 0.85,
            "micro_adjust_delay": 90,
            "sustained_fire_boost": True,
            "boost_delay_ticks": 6,
            "stabilizer_strength": 70,
            "aa_sync": False,
        },
        WeaponClass.SHOTGUN: {
            "ramp_time_ms": 150,
            "sensitivity_threshold": 0.70,
            "micro_adjust_delay": 40,
            "sustained_fire_boost": False,
            "boost_delay_ticks": 0,
            "stabilizer_strength": 30,
            "aa_sync": True,
        },
        WeaponClass.PISTOL: {
            "ramp_time_ms": 180,
            "sensitivity_threshold": 0.78,
            "micro_adjust_delay": 50,
            "sustained_fire_boost": True,
            "boost_delay_ticks": 3,
            "stabilizer_strength": 45,
            "aa_sync": True,
        },
    }
    
    def __init__(self):
        self.profiles_cache = {}
    
    def create_profile(
        self,
        weapon_name: str,
        weapon_class: WeaponClass,
        custom_adjustments: Optional[Dict] = None
    ) -> HairTriggerProfile:
        """
        Crée un profil Hair Trigger pour une arme
        """
        base = self.BASE_PROFILES.get(weapon_class, self.BASE_PROFILES[WeaponClass.AR])
        
        profile = HairTriggerProfile(
            weapon_name=weapon_name,
            weapon_class=weapon_class,
            ramp_time_ms=base["ramp_time_ms"],
            sensitivity_threshold=base["sensitivity_threshold"],
            micro_adjust_delay=base["micro_adjust_delay"],
            sustained_fire_boost=base["sustained_fire_boost"],
            boost_delay_ticks=base["boost_delay_ticks"],
            stabilizer_strength=base["stabilizer_strength"],
            aa_sync=base["aa_sync"],
        )
        
        # Appliquer customisations si fournies
        if custom_adjustments:
            for attr, value in custom_adjustments.items():
                if hasattr(profile, attr):
                    setattr(profile, attr, value)
        
        return profile
    
    def generate_gpc_code(self, profile: HairTriggerProfile) -> HairTriggerGPCCode:
        """
        Génère le code GPC pour ce profil Hair Trigger
        """
        
        # SECTION INIT
        init_vars = "// Hair Trigger Profile: " + profile.weapon_name + " (" + profile.weapon_class.value + ")\n"
        init_vars += "int hair_trigger_enabled = TRUE;\n"
        init_vars += "int hair_trigger_ramp = 0;\n"
        init_vars += "int hair_trigger_ramp_max = " + str(profile.ramp_time_ms // 8) + ";\n"
        init_vars += "int hair_trigger_threshold = " + str(int(profile.sensitivity_threshold * 100)) + ";\n"
        init_vars += "int micro_adjust_timer = 0;\n"
        init_vars += "int micro_adjust_delay = " + str(profile.micro_adjust_delay // 8) + ";\n"
        init_vars += "int sustained_fire_counter = 0;\n"
        init_vars += "int stabilizer_active = FALSE;\n"
        init_vars += "int stabilizer_strength = " + str(profile.stabilizer_strength) + ";\n"
        
        # SECTION MAIN LOOP (pas de f-strings)
        if profile.sustained_fire_boost:
            main_loop = """
        // Hair Trigger avec boost
        if(get_val(tire) && hair_trigger_enabled) {
            if(hair_trigger_ramp < hair_trigger_ramp_max) {
                hair_trigger_ramp = hair_trigger_ramp + 1;
            }
            if(hair_trigger_ramp >= (hair_trigger_ramp_max * hair_trigger_threshold / 100)) {
                set_val(tire, 100);
                sustained_fire_counter = sustained_fire_counter + 1;
                if(sustained_fire_counter > 5) {
                    set_val(tire, 120);
                }
            } else {
                set_val(tire, 0);
            }
        } else {
            hair_trigger_ramp = 0;
            sustained_fire_counter = 0;
        }
"""
        else:
            main_loop = """
        // Hair Trigger simple
        if(get_val(tire) && hair_trigger_enabled) {
            if(hair_trigger_ramp < hair_trigger_ramp_max) {
                hair_trigger_ramp = hair_trigger_ramp + 1;
            }
            if(hair_trigger_ramp >= (hair_trigger_ramp_max * hair_trigger_threshold / 100)) {
                set_val(tire, 100);
            } else {
                set_val(tire, 0);
            }
        } else {
            hair_trigger_ramp = 0;
        }
"""
        
        # SECTION COMBO
        combo_section = """
        // Hair Trigger Combo
        combo(hair_trigger_toggle, {
            set_val(tire, 100);
            wait(50);
            set_val(tire, 0);
        });
        event_press(PS4_SHARE) => {
            call(hair_trigger_toggle);
        };
"""
        
        return HairTriggerGPCCode(
            init_vars=init_vars,
            main_loop=main_loop,
            combo_section=combo_section
        )
    
    def get_profile_for_weapon(self, weapon_dict: Dict) -> HairTriggerProfile:
        """
        Détermine le profil Hair Trigger pour une arme
        """
        weapon_name = weapon_dict.get("name", "UNKNOWN")
        weapon_cat = (weapon_dict.get("category", "") or "").upper()
        
        # Map category to WeaponClass
        category_map = {
            "SNIPER": WeaponClass.SNIPER,
            "MARKSMAN": WeaponClass.MARKSMAN,
            "AR": WeaponClass.AR,
            "SMG": WeaponClass.SMG,
            "LMG": WeaponClass.LMG,
            "SHOTGUN": WeaponClass.SHOTGUN,
            "PISTOL": WeaponClass.PISTOL,
        }
        
        weapon_class = category_map.get(weapon_cat, WeaponClass.AR)
        
        # Ajustements custom si meta
        custom_adj = {}
        if weapon_dict.get("is_meta"):
            custom_adj["stabilizer_strength"] = 65  # Boost stabilité pour meta
        
        cache_key = f"{weapon_name}_{weapon_class.value}"
        if cache_key not in self.profiles_cache:
            self.profiles_cache[cache_key] = self.create_profile(
                weapon_name, weapon_class, custom_adj
            )
        
        return self.profiles_cache[cache_key]
    
    def bulk_generate_profiles(self, weapons: List[Dict]) -> Dict[str, HairTriggerProfile]:
        """
        Génère des profils pour une liste d'armes
        """
        profiles = {}
        for weapon in weapons:
            weapon_id = weapon.get("id") or weapon.get("name")
            profiles[weapon_id] = self.get_profile_for_weapon(weapon)
        return profiles

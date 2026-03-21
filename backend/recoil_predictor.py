"""
🎯 ADAPTIVE RECOIL PREDICTOR
Prédiction du comportement du recul sur tirs soutenus
Système d'apprentissage qui adapte la compensation
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class RecoilPhase(Enum):
    """Phases du recul au cours d'une rafale"""
    INITIAL = "initial"  # 0-2 shots
    RAMPING = "ramping"  # 3-8 shots  
    PEAK = "peak"  # 9-20 shots
    DRIFT = "drift"  # 20+ shots


@dataclass
class RecoilBehavior:
    """Comportement du recul d'une arme"""
    weapon_name: str
    vertical_initial: int  # Recul vertical initial (0-2 shots)
    vertical_peak: int  # Recul vertical max (9-20 shots)
    vertical_drift: int  # Drift vertical après 20 shots
    horizontal_pattern: str  # "left", "right", "alternating", "stable"
    horizontal_intensity: int  # Intensité 0-100
    controllability: int  # 0-100 (100 = très contrôlable)
    weapon_class: str


@dataclass
class RecoilCompensationStrategy:
    """Stratégie de compensation adaptative"""
    phase: RecoilPhase
    vertical_compensation: int
    horizontal_compensation: int
    burst_duration: int  # Durée burst avant reset
    reset_delay: int  # Délai avant reset (ms)


class AdaptiveRecoilPredictor:
    """
    Prédicteur de recul adaptatif Cronus Zen
    Apprend et s'adapte aux patterns de recul
    """
    
    # Database de comportements de recul connus
    RECOIL_DATABASE = {
        "AK-27": RecoilBehavior(
            weapon_name="AK-27",
            vertical_initial=26,
            vertical_peak=42,
            vertical_drift=45,
            horizontal_pattern="alternating",
            horizontal_intensity=12,
            controllability=65,
            weapon_class="AR",
        ),
        "TANTO .22": RecoilBehavior(
            weapon_name="TANTO .22",
            vertical_initial=18,
            vertical_peak=28,
            vertical_drift=32,
            horizontal_pattern="slight_right",
            horizontal_intensity=8,
            controllability=82,
            weapon_class="SMG",
        ),
        "GPMG-7": RecoilBehavior(
            weapon_name="GPMG-7",
            vertical_initial=35,
            vertical_peak=58,
            vertical_drift=65,
            horizontal_pattern="alternating",
            horizontal_intensity=15,
            controllability=55,
            weapon_class="LMG",
        ),
        "LW3A1": RecoilBehavior(
            weapon_name="LW3A1",
            vertical_initial=40,
            vertical_peak=40,
            vertical_drift=40,
            horizontal_pattern="stable",
            horizontal_intensity=3,
            controllability=90,
            weapon_class="SNIPER",
        ),
        "XM4": RecoilBehavior(
            weapon_name="XM4",
            vertical_initial=24,
            vertical_peak=36,
            vertical_drift=40,
            horizontal_pattern="left_drift",
            horizontal_intensity=10,
            controllability=72,
            weapon_class="AR",
        ),
    }
    
    def __init__(self):
        self.active_predictions = {}
        self.learning_history = {}
    
    def predict_recoil(self, weapon_dict: Dict) -> RecoilBehavior:
        """
        Prédit le comportement de recul pour une arme
        """
        weapon_name = weapon_dict.get("name", "UNKNOWN")
        
        # Vérifier DB
        if weapon_name in self.RECOIL_DATABASE:
            return self.RECOIL_DATABASE[weapon_name]
        
        # Sinon, extrapoler depuis les stats brutes
        vertical = weapon_dict.get("vertical_recoil", 25)
        horizontal = weapon_dict.get("horizontal_recoil", 10)
        category = weapon_dict.get("category", "AR").upper()
        
        # Estimation du comportement
        return RecoilBehavior(
            weapon_name=weapon_name,
            vertical_initial=vertical,
            vertical_peak=int(vertical * 1.6),  # Estime pic à 160% de base
            vertical_drift=int(vertical * 1.8),  # Estime drift à 180% de base
            horizontal_pattern="alternating" if horizontal > 12 else "stable",
            horizontal_intensity=min(100, horizontal * 2),
            controllability=max(40, 100 - (vertical + horizontal) // 2),
            weapon_class=category,
        )
    
    def calculate_compensation_strategy(
        self,
        recoil_behavior: RecoilBehavior,
        profile_mode: str = "EQUILIBRE"
    ) -> Dict[RecoilPhase, RecoilCompensationStrategy]:
        """
        Calcule la stratégie de compensation pour chaque phase de recul
        """
        strategies = {}
        
        # Profiler poids pour compensation
        if profile_mode == "AGRESSIF":
            initial_comp_mult = 0.60  # Moins de compensation (réactivité)
            peak_comp_mult = 0.80
            drift_comp_mult = 0.90
        elif profile_mode == "SNIPER":
            initial_comp_mult = 1.20  # Plus de compensation (précision)
            peak_comp_mult = 1.40
            drift_comp_mult = 1.50
        else:  # EQUILIBRE
            initial_comp_mult = 1.0
            peak_comp_mult = 1.1
            drift_comp_mult = 1.2
        
        # INITIAL (0-2 shots)
        strategies[RecoilPhase.INITIAL] = RecoilCompensationStrategy(
            phase=RecoilPhase.INITIAL,
            vertical_compensation=max(5, int(recoil_behavior.vertical_initial * 0.40 * initial_comp_mult)),
            horizontal_compensation=self._compensate_horizontal(recoil_behavior, 0.30),
            burst_duration=100,  # ms
            reset_delay=50,
        )
        
        # RAMPING (3-8 shots) - recul qui monte
        strategies[RecoilPhase.RAMPING] = RecoilCompensationStrategy(
            phase=RecoilPhase.RAMPING,
            vertical_compensation=max(10, int(recoil_behavior.vertical_peak * 0.50 * peak_comp_mult)),
            horizontal_compensation=self._compensate_horizontal(recoil_behavior, 0.60),
            burst_duration=300,
            reset_delay=100,
        )
        
        # PEAK (9-20 shots) - recul maximal
        strategies[RecoilPhase.PEAK] = RecoilCompensationStrategy(
            phase=RecoilPhase.PEAK,
            vertical_compensation=max(15, int(recoil_behavior.vertical_peak * 0.80 * peak_comp_mult)),
            horizontal_compensation=self._compensate_horizontal(recoil_behavior, 0.90),
            burst_duration=600,
            reset_delay=150,
        )
        
        # DRIFT (20+ shots) - contrôle du drift
        strategies[RecoilPhase.DRIFT] = RecoilCompensationStrategy(
            phase=RecoilPhase.DRIFT,
            vertical_compensation=max(20, int(recoil_behavior.vertical_drift * 0.75 * drift_comp_mult)),
            horizontal_compensation=self._compensate_horizontal(recoil_behavior, 1.0),
            burst_duration=1000,
            reset_delay=200,
        )
        
        return strategies
    
    def _compensate_horizontal(self, behavior: RecoilBehavior, intensity_mult: float) -> int:
        """
        Compense le recul horizontal basé sur le pattern
        """
        base_comp = int(behavior.horizontal_intensity * intensity_mult)
        
        if behavior.horizontal_pattern == "stable":
            return 0  # Pas de compensation nécessaire
        elif behavior.horizontal_pattern == "left_drift":
            return min(40, base_comp)  # Compenser à droite
        elif behavior.horizontal_pattern == "right_drift":
            return max(-40, -base_comp)  # Compenser à gauche
        else:  # alternating
            # Alternance de compensation (complexe, réserve à expert)
            return 0
    
    def generate_prediction_gpc_code(
        self,
        recoil_behavior: RecoilBehavior,
        strategies: Dict[RecoilPhase, RecoilCompensationStrategy],
        profile_mode: str = "EQUILIBRE"
    ) -> str:
        """
        Génère le code GPC pour la prédiction de recul adaptative
        """
        
        code = f"""
// Adaptive Recoil Prediction: {recoil_behavior.weapon_name}
// Profile: {profile_mode} | Controllability: {recoil_behavior.controllability}/100

int recoil_phase = 0;  // 0=initial, 1=ramping, 2=peak, 3=drift
int recoil_shot_counter = 0;
int recoil_compensation_vertical = 0;
int recoil_compensation_horizontal = 0;

// Seuils de phase
int PHASE_RAMPING_THRESHOLD = 3;  // shots
int PHASE_PEAK_THRESHOLD = 9;
int PHASE_DRIFT_THRESHOLD = 20;

void update_recoil_phase() {{
    if(recoil_shot_counter >= PHASE_DRIFT_THRESHOLD) {{
        recoil_phase = 3;  // DRIFT
        recoil_compensation_vertical = {strategies[RecoilPhase.DRIFT].vertical_compensation};
        recoil_compensation_horizontal = {strategies[RecoilPhase.DRIFT].horizontal_compensation};
    }} else if(recoil_shot_counter >= PHASE_PEAK_THRESHOLD) {{
        recoil_phase = 2;  // PEAK
        recoil_compensation_vertical = {strategies[RecoilPhase.PEAK].vertical_compensation};
        recoil_compensation_horizontal = {strategies[RecoilPhase.PEAK].horizontal_compensation};
    }} else if(recoil_shot_counter >= PHASE_RAMPING_THRESHOLD) {{
        recoil_phase = 1;  // RAMPING
        recoil_compensation_vertical = {strategies[RecoilPhase.RAMPING].vertical_compensation};
        recoil_compensation_horizontal = {strategies[RecoilPhase.RAMPING].horizontal_compensation};
    }} else {{
        recoil_phase = 0;  // INITIAL
        recoil_compensation_vertical = {strategies[RecoilPhase.INITIAL].vertical_compensation};
        recoil_compensation_horizontal = {strategies[RecoilPhase.INITIAL].horizontal_compensation};
    }}
}}

// Appliquer compensation dans la main loop
if(get_val(vise) && get_val(tire)) {{
    recoil_shot_counter = recoil_shot_counter + 1;
    update_recoil_phase();
    
    // Appliquer compensation (x2 pour Cronus vertical)
    set_val(PS4_RY, get_val(PS4_RY) + (recoil_compensation_vertical * 2));
    set_val(PS4_RX, get_val(PS4_RX) + recoil_compensation_horizontal);
}} else {{
    recoil_shot_counter = 0;  // Reset au relâchement
}}
"""
        
        return code
    
    def get_learning_suggestion(
        self,
        weapon_name: str,
        observed_vertical_peak: int,
        observed_controllability: int
    ) -> Dict:
        """
        Suggestion d'apprentissage basée sur observation réelle
        """
        if weapon_name not in self.RECOIL_DATABASE:
            return {
                "new_weapon": True,
                "suggestion": f"Arme nouvelle - profil créé"
            }
        
        current = self.RECOIL_DATABASE[weapon_name]
        
        # Comparer avec observation
        vertical_variance = abs(observed_vertical_peak - current.vertical_peak)
        controllability_variance = abs(observed_controllability - current.controllability)
        
        suggestions = []
        
        if vertical_variance > 5:
            suggestions.append(f"Recul vertical actual: {observed_vertical_peak} vs {current.vertical_peak}")
        if controllability_variance > 10:
            suggestions.append(f"Contrôlabilité actual: {observed_controllability} vs {current.controllability}")
        
        return {
            "weapon": weapon_name,
            "significant_variance": vertical_variance > 5 or controllability_variance > 10,
            "suggestions": suggestions,
            "recommendation": "Recalibrer le profil" if suggestions else "Profil correct"
        }

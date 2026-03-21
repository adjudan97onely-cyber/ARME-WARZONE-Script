"""
🎯 DUO WEAPON PRE-CALCULATOR
Pré-calcule et cache les meilleures paires d'armes
Évite les calculs répétés, optimise les recherches
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import json

class DuoWeaponPreCalculator:
    """
    Pré-calcule les paires de duo par catégories
    Stratégie: Primaire fort + Secondaire complémentaire
    """
    
    def __init__(self):
        self.cache = {}
        self.pair_scores = defaultdict(list)
        self.weapon_pool = []
        self.categories = [
            "AR", "SMG", "LMG", "SNIPER", "MARKSMAN",
            "SHOTGUN", "PISTOL", "LAUNCHER"
        ]
    
    def load_weapons(self, weapons: List[Dict]):
        """Charge les armes dans le calculator"""
        self.weapon_pool = weapons
        self._build_category_index()
    
    def _build_category_index(self):
        """Index armes par catégorie"""
        self.by_category = defaultdict(list)
        for weapon in self.weapon_pool:
            cat = (weapon.get("category") or "").upper()
            self.by_category[cat].append(weapon)
    
    def _score_duo_pair(
        self,
        primary: Dict,
        secondary: Dict,
        profile_mode: str = "EQUILIBRE"
    ) -> float:
        """
        Score une paire d'armes (primaire + secondaire)
        Critères:
        - Couverture de distances différentes
        - Complémentarité de TTK
        - Synergy de recoil
        """
        primary_cat = (primary.get("category") or "").upper()
        secondary_cat = (secondary.get("category") or "").upper()
        
        # Pénalité si même catégorie (moins intéressant)
        category_diversity_penalty = 0
        if primary_cat == secondary_cat:
            category_diversity_penalty = -50
        
        # Bonus de complémentarité
        complementary_bonus = 0
        
        # AR primaire + SMG secondaire = excellent
        if primary_cat == "AR" and secondary_cat == "SMG":
            complementary_bonus = 100
        # SMG primaire + SNIPER secondaire = bon
        elif primary_cat == "SMG" and secondary_cat in ["SNIPER", "MARKSMAN"]:
            complementary_bonus = 80
        # LMG primaire + PISTOL/SMG secondaire = bon
        elif primary_cat == "LMG" and secondary_cat in ["PISTOL", "SMG"]:
            complementary_bonus = 70
        # SNIPER primaire + PISTOL secondaire = minimum cover
        elif primary_cat == "SNIPER" and secondary_cat == "PISTOL":
            complementary_bonus = 60
        
        # TTK synergy (primaire fast + secondaire backup)
        primary_ttk = primary.get("ttk_ms", 500)
        secondary_ttk = secondary.get("ttk_ms", 600)
        
        ttk_diversity = abs(primary_ttk - secondary_ttk)
        ttk_bonus = min(30, ttk_diversity // 20)  # Plus différent = mieux
        
        # Recoil synergy (si primaire recul élevé, secondaire doit être bas)
        primary_recoil = primary.get("vertical_recoil", 25) + primary.get("horizontal_recoil", 10)
        secondary_recoil = secondary.get("vertical_recoil", 25) + secondary.get("horizontal_recoil", 10)
        
        recoil_delta = abs(primary_recoil - secondary_recoil)
        recoil_bonus = min(20, recoil_delta // 5)  # Plus différent = mieux
        
        # Meta boost (si ce sont des armes meta)
        meta_bonus = 0
        if primary.get("is_meta"):
            meta_bonus += 30
        if secondary.get("is_meta"):
            meta_bonus += 20
        
        # Total score
        total_score = (
            complementary_bonus +
            ttk_bonus +
            recoil_bonus +
            meta_bonus +
            category_diversity_penalty
        )
        
        return total_score
    
    def get_best_duo_pair(
        self,
        profile_mode: str = "EQUILIBRE",
        max_results: int = 5
    ) -> List[Dict]:
        """
        Retourne les meilleures paires de duo
        """
        cache_key = f"best_duo_{profile_mode}_{max_results}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        pairs = []
        
        # Stratégie: iterate primaires, pour chaque primaire trouver le meilleur secondaire
        primary_categories = ["AR", "LMG", "SMG", "SNIPER", "MARKSMAN"]
        
        for primary_cat in primary_categories:
            primaries = self.by_category[primary_cat]
            if not primaries:
                continue
            
            # Prendre les 3 meilleures armes de cette catégorie
            top_primaries = sorted(
                primaries,
                key=lambda w: (w.get("is_meta", False), w.get("damage", 0) * w.get("fire_rate", 0)),
                reverse=True
            )[:3]
            
            for primary in top_primaries:
                # Chercher le meilleur secondaire pour ce primaire
                best_secondary = None
                best_score = -999
                
                # Catégories candidates pour secondaire
                secondary_candidates = [
                    "SMG", "PISTOL", "SHOTGUN"
                    if primary_cat != "SMG" else
                    ["SNIPER", "MARKSMAN", "PISTOL"]
                ]
                
                for sec_cat in secondary_candidates[0]:  # Parcourir String
                    pass
                
                for sec_cat_list in [secondary_candidates]:
                    for sec_cat in sec_cat_list:
                        secondaries = self.by_category[sec_cat]
                        if not secondaries:
                            continue
                        
                        # Prendre les 2 meilleures du categorie
                        top_secondaries = sorted(
                            secondaries,
                            key=lambda w: (w.get("is_meta", False), w.get("fire_rate", 0)),
                            reverse=True
                        )[:2]
                        
                        for secondary in top_secondaries:
                            score = self._score_duo_pair(primary, secondary, profile_mode)
                            if score > best_score:
                                best_score = score
                                best_secondary = secondary
                
                if best_secondary:
                    pairs.append({
                        "primary": primary,
                        "secondary": best_secondary,
                        "score": best_score,
                        "compatibility": "EXCELLENTE" if best_score > 150 else "BONNE" if best_score > 80 else "ACCEPTABLE",
                    })
        
        # Trier par score et limiter
        pairs = sorted(pairs, key=lambda p: p["score"], reverse=True)[:max_results]
        
        # Cache
        self.cache[cache_key] = pairs
        return pairs
    
    def get_duo_for_primary(
        self,
        primary_weapon: Dict,
        profile_mode: str = "EQUILIBRE"
    ) -> Dict:
        """
        Recommande le secondaire idéal pour une arme primaire donnée
        """
        best_secondary = None
        best_score = -999
        
        # Catégories candidates pour secondaire
        primary_cat = (primary_weapon.get("category") or "").upper()
        
        if primary_cat in ["AR", "LMG", "SNIPER", "MARKSMAN"]:
            secondary_candidates = ["SMG", "PISTOL", "SHOTGUN"]
        elif primary_cat == "SMG":
            secondary_candidates = ["SNIPER", "MARKSMAN", "PISTOL"]
        else:
            secondary_candidates = ["PISTOL", "SMG"]
        
        for sec_cat in secondary_candidates:
            secondaries = self.by_category[sec_cat]
            if not secondaries:
                continue
            
            # Prendre les 3 meilleures
            top_secs = sorted(
                secondaries,
                key=lambda w: (w.get("is_meta", False), w.get("fire_rate", 0)),
                reverse=True
            )[:3]
            
            for secondary in top_secs:
                score = self._score_duo_pair(primary_weapon, secondary, profile_mode)
                if score > best_score:
                    best_score = score
                    best_secondary = secondary
        
        return {
            "primary": primary_weapon,
            "secondary": best_secondary,
            "score": best_score,
            "reason": self._explain_pairing(primary_weapon, best_secondary),
        }
    
    def _explain_pairing(self, primary: Dict, secondary: Dict) -> str:
        """Explique pourquoi cette paire marche bien"""
        primary_cat = primary.get("category", "?")
        secondary_cat = secondary.get("category", "?")
        primary_ttk = primary.get("ttk_ms", 500)
        secondary_ttk = secondary.get("ttk_ms", 600)
        
        reasons = []
        
        if primary_cat == "AR" and secondary_cat == "SMG":
            reasons.append("AR pour distance moyenne + SMG pour CQC")
        if abs(primary_ttk - secondary_ttk) > 100:
            reasons.append(f"TTK complémentaire ({primary_ttk}ms vs {secondary_ttk}ms)")
        if primary.get("is_meta") and secondary.get("is_meta"):
            reasons.append("Deux armes meta combinées")
        
        return " / ".join(reasons) if reasons else "Bonne complémentarité"
    
    def get_all_best_pairs(self, profile_mode: str = "EQUILIBRE") -> Dict[str, List[Dict]]:
        """
        Retourne les meilleures paires pour chaque catégorie primaire
        """
        result = {}
        for cat in ["AR", "SMG", "LMG", "SNIPER"]:
            primaries = self.by_category[cat]
            if primaries:
                # Top primaire de cette catégorie
                top_primary = sorted(
                    primaries,
                    key=lambda w: (w.get("is_meta", False), w.get("damage", 0) * w.get("fire_rate", 0)),
                    reverse=True
                )[0]
                
                duo = self.get_duo_for_primary(top_primary, profile_mode)
                result[cat] = duo
        
        return result

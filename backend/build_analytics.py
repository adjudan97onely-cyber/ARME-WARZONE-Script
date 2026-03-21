"""
📊 BUILD ANALYTICS ENGINE
Tracking et analyse des performances des builds réels
Système de recommandations basé sur data
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class PerformanceRating(Enum):
    """Ratings de performance"""
    EXCELLENT = "excellent"  # 80+
    VERY_GOOD = "very_good"  # 70-79
    GOOD = "good"  # 60-69
    ACCEPTABLE = "acceptable"  # 50-59
    POOR = "poor"  # < 50


@dataclass
class BuildPerformanceMetric:
    """Métrique de performance pour une build"""
    build_id: str
    weapon_primary: str
    weapon_secondary: str
    profile_mode: str
    accuracy_score: float  # 0-100
    ttk_effectiveness: float  # 0-100
    controllability: float  # 0-100
    recoil_management: float  # 0-100
    user_preference: int  # 0-10
    successful_engagements: int
    failed_engagements: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class BuildRecommendation:
    """Recommandation de build"""
    rank: int
    build_name: str
    primary_weapon: str
    secondary_weapon: str
    profile_mode: str
    overall_score: float
    reason: str
    success_rate: float
    recommended_for: str  # "rusheur", "sniper", "all-rounder"


class BuildAnalyticsEngine:
    """
    Moteur d'analytics pour tracking et recommandations
    """
    
    def __init__(self):
        self.metrics_history: List[BuildPerformanceMetric] = []
        self.build_stats: Dict[str, Dict] = {}
        self.user_preferences: Dict[str, float] = {}  # Build ID -> préférence
    
    def record_performance(self, metric: BuildPerformanceMetric) -> None:
        """
        Enregistre une métrique de performance
        """
        self.metrics_history.append(metric)
        
        # Mettre à jour les stats
        build_key = f"{metric.weapon_primary}_{metric.weapon_secondary}_{metric.profile_mode}"
        
        if build_key not in self.build_stats:
            self.build_stats[build_key] = {
                "uses": 0,
                "accuracy_avg": 0,
                "ttk_effectiveness_avg": 0,
                "controllability_avg": 0,
                "recoil_avg": 0,
                "success_rate": 0,
                "overall_score": 0,
            }
        
        stats = self.build_stats[build_key]
        stats["uses"] += 1
        
        # Mettre à jour moyennes
        n = stats["uses"]
        stats["accuracy_avg"] = (stats["accuracy_avg"] * (n - 1) + metric.accuracy_score) / n
        stats["ttk_effectiveness_avg"] = (stats["ttk_effectiveness_avg"] * (n - 1) + metric.ttk_effectiveness) / n
        stats["controllability_avg"] = (stats["controllability_avg"] * (n - 1) + metric.controllability) / n
        stats["recoil_avg"] = (stats["recoil_avg"] * (n - 1) + metric.recoil_management) / n
        
        # Success rate
        total_engagements = metric.successful_engagements + metric.failed_engagements
        if total_engagements > 0:
            stats["success_rate"] = metric.successful_engagements / total_engagements
        
        # Overall score
        stats["overall_score"] = (
            stats["accuracy_avg"] * 0.25 +
            stats["ttk_effectiveness_avg"] * 0.30 +
            stats["controllability_avg"] * 0.25 +
            stats["recoil_avg"] * 0.20
        )
    
    def get_top_builds(self, limit: int = 10) -> List[BuildRecommendation]:
        """
        Retourne les meilleures builds basées sur les données
        """
        recommendations = []
        
        for rank, (build_key, stats) in enumerate(
            sorted(self.build_stats.items(), 
                   key=lambda x: x[1]["overall_score"], 
                   reverse=True)[:limit],
            1
        ):
            primary, secondary, mode = build_key.split("_", 2)
            
            # Déterminer le type de build
            if mode == "AGRESSIF":
                recommended_for = "rusheur / CQC dominance"
            elif mode == "SNIPER":
                recommended_for = "sniper / tueur d'élite"
            else:
                recommended_for = "polyvalent / tous les playstyles"
            
            # Raison
            if stats["overall_score"] > 75:
                reason = f"Excellent: TTK {stats['ttk_effectiveness_avg']:.0f}, Contrôle {stats['controllability_avg']:.0f}"
            elif stats["overall_score"] > 65:
                reason = f"Très bon: Build équilibrée avec {stats['success_rate']*100:.0f}% de réussite"
            else:
                reason = f"Bon: Spécialisée pour {recommended_for}"
            
            recommendations.append(BuildRecommendation(
                rank=rank,
                build_name=f"{primary} + {secondary}",
                primary_weapon=primary,
                secondary_weapon=secondary,
                profile_mode=mode,
                overall_score=stats["overall_score"],
                reason=reason,
                success_rate=stats["success_rate"],
                recommended_for=recommended_for,
            ))
        
        return recommendations
    
    def get_performance_rating(self, overall_score: float) -> PerformanceRating:
        """
        Retourne le rating de performance
        """
        if overall_score >= 80:
            return PerformanceRating.EXCELLENT
        elif overall_score >= 70:
            return PerformanceRating.VERY_GOOD
        elif overall_score >= 60:
            return PerformanceRating.GOOD
        elif overall_score >= 50:
            return PerformanceRating.ACCEPTABLE
        else:
            return PerformanceRating.POOR
    
    def get_build_insights(self, build_key: str) -> Dict:
        """
        Récupère des insights détaillés sur une build
        """
        if build_key not in self.build_stats:
            return {"error": "Build not found"}
        
        stats = self.build_stats[build_key]
        rating = self.get_performance_rating(stats["overall_score"])
        
        # Identifier forces et faiblesses
        scores = {
            "Accuracy": stats["accuracy_avg"],
            "TTK": stats["ttk_effectiveness_avg"],
            "Controllability": stats["controllability_avg"],
            "Recoil Mgmt": stats["recoil_avg"],
        }
        
        strengths = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        weaknesses = sorted(scores.items(), key=lambda x: x[1])[:2]
        
        return {
            "build": build_key,
            "overall_score": stats["overall_score"],
            "rating": rating.value,
            "uses": stats["uses"],
            "success_rate": stats["success_rate"],
            "strengths": [s[0] for s in strengths],
            "weaknesses": [w[0] for w in weaknesses],
            "recommendation": self._generate_recommendation(rating, stats),
        }
    
    def _generate_recommendation(self, rating: PerformanceRating, stats: Dict) -> str:
        """
        Génère une recommandation textuelle
        """
        if rating == PerformanceRating.EXCELLENT:
            return "Cette build est optimale. À continuer sans modification."
        elif rating == PerformanceRating.VERY_GOOD:
            return "Très bonne build. Considère des fine-tuning mineurs."
        elif rating == PerformanceRating.GOOD:
            return "Build solide. Des améliorations pourraient être apportées."
        elif rating == PerformanceRating.ACCEPTABLE:
            return "Build acceptable. À réviser si performance plafonne."
        else:
            return f"Build en difficulté. Success rate: {stats['success_rate']*100:.0f}%"
    
    def compare_builds(self, builds: List[str]) -> Dict:
        """
        Compare plusieurs builds côte à côte
        """
        comparison = {}
        
        for build in builds:
            if build in self.build_stats:
                comparison[build] = self.build_stats[build]
        
        # Ajouter ranking
        for rank, (build, stats) in enumerate(
            sorted(comparison.items(), 
                   key=lambda x: x[1]["overall_score"], 
                   reverse=True),
            1
        ):
            stats["rank"] = rank
        
        return comparison
    
    def get_trend_analysis(self, build_key: str, window_size: int = 10) -> Dict:
        """
        Analyse la tendance d'une build sur les N derniers usages
        """
        # Filtrer les métriques pour cette build
        recent_metrics = [
            m for m in self.metrics_history[-window_size:]
            if f"{m.weapon_primary}_{m.weapon_secondary}_{m.profile_mode}" == build_key
        ]
        
        if not recent_metrics:
            return {"error": "Pas assez de données"}
        
        # Calculer la tendance
        accuracy_trend = recent_metrics[-1].accuracy_score - recent_metrics[0].accuracy_score
        ttk_trend = recent_metrics[-1].ttk_effectiveness - recent_metrics[0].ttk_effectiveness
        controllability_trend = recent_metrics[-1].controllability - recent_metrics[0].controllability
        
        return {
            "build": build_key,
            "window_size": window_size,
            "accuracy_trend": accuracy_trend,
            "ttk_trend": ttk_trend,
            "controllability_trend": controllability_trend,
            "overall_trend": "improving" if accuracy_trend > 0 and controllability_trend > 0 else "declining" if accuracy_trend < -5 else "stable",
            "recommendation": "Continue! Progression visuelle." if accuracy_trend > 5 else "À revoir" if accuracy_trend < -10 else "Stable - bon équilibre"
        }
    
    def export_analytics_report(self) -> Dict:
        """
        Exporte un rapport complet d'analytics
        """
        return {
            "total_sessions": len(self.metrics_history),
            "total_builds_used": len(self.build_stats),
            "top_builds": self.get_top_builds(5),
            "build_details": {
                build: self.get_build_insights(build)
                for build in list(self.build_stats.keys())[:5]
            },
            "overall_stats": {
                "avg_accuracy": sum(m.accuracy_score for m in self.metrics_history) / len(self.metrics_history) if self.metrics_history else 0,
                "avg_ttk_effectiveness": sum(m.ttk_effectiveness for m in self.metrics_history) / len(self.metrics_history) if self.metrics_history else 0,
                "avg_controllability": sum(m.controllability for m in self.metrics_history) / len(self.metrics_history) if self.metrics_history else 0,
            }
        }

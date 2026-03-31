from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from openai import AsyncOpenAI

# Meta scraper automatique (CODMunity + WZStats)
from meta_scraper import update_meta_in_db, load_cache

# Import FINAL GPC generator - STRUCTURE SIMPLE QUI COMPILE
from gpc_generator_final import generate_master_script_advanced
from gpc_generator_ultimate import generate_ultimate_script
from gpc_generator_dual import generate_dual_profile_script
from weapon_optimizer import calculate_optimized_stats, format_build_string

# Import PRO MODULES 🔥
from weapon_optimizer_pro import calculate_optimized_stats_pro, compare_all_profiles
from duo_calculator import DuoWeaponPreCalculator
from hair_trigger_engine import AdvancedHairTriggerEngine, WeaponClass
from recoil_predictor import AdaptiveRecoilPredictor
from build_analytics import BuildAnalyticsEngine, BuildPerformanceMetric

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Zen Hub Pro API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============== PRO MODULES INIT 🔥 ==============
duo_calculator = DuoWeaponPreCalculator()
hair_trigger_engine = AdvancedHairTriggerEngine()
recoil_predictor = AdaptiveRecoilPredictor()
build_analytics = BuildAnalyticsEngine()

# ============== MODELS ==============

class Weapon(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str  # AR, SMG, LMG, SHOTGUN, SNIPER, PISTOL, LAUNCHER
    game: str  # MW3, BO6
    vertical_recoil: int = 25
    horizontal_recoil: int = 10
    fire_rate: int = 700
    damage: int = 30
    range_meters: int = 40
    rapid_fire: bool = False
    rapid_fire_value: int = 0
    recommended_build: Optional[str] = None
    notes: Optional[str] = None
    is_meta: bool = False
    is_hidden_meta: bool = False  # High DPS but hard to control
    # Champs META live (CODMunity + WZStats)
    meta_tier: Optional[str] = None        # ABSOLUTE_META / META / A_TIER / B_TIER / C_TIER
    meta_rank: Optional[int] = None        # Rang dans le classement CODMunity
    pick_rate: Optional[float] = None      # % de joueurs qui utilisent cette arme
    ease_score: Optional[float] = None     # Score de facilité CODMunity (sur 10)
    last_meta_update: Optional[str] = None # Dernière sync CODMunity/WZStats
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class WeaponCreate(BaseModel):
    name: str
    category: str
    game: str = "BO6"
    vertical_recoil: int = 25
    horizontal_recoil: int = 10
    fire_rate: int = 700
    damage: int = 30
    range_meters: int = 40
    rapid_fire: bool = False
    rapid_fire_value: int = 0
    recommended_build: Optional[str] = None
    notes: Optional[str] = None
    is_meta: bool = False
    is_hidden_meta: bool = False

class WeaponUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    game: Optional[str] = None
    vertical_recoil: Optional[int] = None
    horizontal_recoil: Optional[int] = None
    fire_rate: Optional[int] = None
    damage: Optional[int] = None
    range_meters: Optional[int] = None
    rapid_fire: Optional[bool] = None
    rapid_fire_value: Optional[int] = None
    recommended_build: Optional[str] = None
    notes: Optional[str] = None
    is_meta: Optional[bool] = None
    is_hidden_meta: Optional[bool] = None
    meta_tier: Optional[str] = None
    meta_rank: Optional[int] = None
    pick_rate: Optional[float] = None
    ease_score: Optional[float] = None

class SavedScript(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    code: str
    weapon_ids: List[str] = []
    script_type: str = "single"  # single, master
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SavedScriptCreate(BaseModel):
    title: str
    code: str
    weapon_ids: List[str] = []
    script_type: str = "single"

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # user, assistant
    content: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

# ============== WEAPON ROUTES ==============

@api_router.get("/weapons", response_model=List[Weapon])
async def get_weapons(category: Optional[str] = None, game: Optional[str] = None):
    query = {}
    if category:
        query["category"] = category
    if game:
        query["game"] = game
    weapons = await db.weapons.find(query, {"_id": 0}).to_list(1000)
    return weapons

@api_router.get("/weapons/{weapon_id}", response_model=Weapon)
async def get_weapon(weapon_id: str):
    weapon = await db.weapons.find_one({"id": weapon_id}, {"_id": 0})
    if not weapon:
        raise HTTPException(status_code=404, detail="Weapon not found")
    return weapon

@api_router.post("/weapons", response_model=Weapon)
async def create_weapon(weapon_data: WeaponCreate):
    weapon = Weapon(**weapon_data.model_dump())
    doc = weapon.model_dump()
    await db.weapons.insert_one(doc)
    return weapon

@api_router.put("/weapons/{weapon_id}", response_model=Weapon)
async def update_weapon(weapon_id: str, weapon_data: WeaponUpdate):
    update_dict = {k: v for k, v in weapon_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.weapons.update_one(
        {"id": weapon_id},
        {"$set": update_dict}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Weapon not found")
    
    weapon = await db.weapons.find_one({"id": weapon_id}, {"_id": 0})
    return weapon

@api_router.delete("/weapons/{weapon_id}")
async def delete_weapon(weapon_id: str):
    result = await db.weapons.delete_one({"id": weapon_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Weapon not found")
    return {"message": "Weapon deleted successfully"}

# ============== SCRIPT ROUTES ==============

@api_router.get("/scripts", response_model=List[SavedScript])
async def get_scripts(script_type: Optional[str] = None):
    query = {}
    if script_type:
        query["script_type"] = script_type
    scripts = await db.scripts.find(query, {"_id": 0}).to_list(1000)
    return scripts

@api_router.post("/scripts", response_model=SavedScript)
async def create_script(script_data: SavedScriptCreate):
    script = SavedScript(**script_data.model_dump())
    doc = script.model_dump()
    await db.scripts.insert_one(doc)
    return script

@api_router.delete("/scripts/{script_id}")
async def delete_script(script_id: str):
    result = await db.scripts.delete_one({"id": script_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Script not found")
    return {"message": "Script deleted successfully"}

# ============== AI CHAT ROUTES ==============

SYSTEM_PROMPT = """Tu es l'Architecte Balistique Warzone SUPRÊME - l'expert ultime en création de scripts Cronus Zen/GPC.

DATE ACTUELLE: 12 MARS 2026, 22H32
BASE DE CONNAISSANCES: Warzone Saison 2 (2026) - Mise à jour du 12 mars 2026

=== ⚠️ RÈGLE ABSOLUE : ACCESSOIRES VALIDES UNIQUEMENT ⚠️ ===

Tu DOIS utiliser UNIQUEMENT les accessoires de cette liste officielle de codmunity.gg.
N'INVENTE JAMAIS un nom d'accessoire. Si tu ne trouves pas l'accessoire exact, utilise un terme générique comme "Extended Mag" ou "Compensator".

ACCESSOIRES VALIDES PAR ARME:

**Peacekeeper Mk1:**
- Bouche: Monolithic Suppressor, Redwell Shade-X Suppressor, K&S Compensator, K&S Stalker 57-X, Kühn Ported Comp, K&S Brake-2B
- Canon: 25" EAM Heavy Barrel, 23.5" Longbow Barrel, 21" DF-3 Merge Barrel, 19.4" Stimulus Barrel, 14.5" E7-Cuff Barrel
- Lunette: FANG HoverPoint ELO, Lethal Tools ELO, Greaves Red Dot, EAM Dyad xL, Greaves Ultra Zoom, Millimeter Scanner, EAM XL Reflex
- Sous-canon: Lateral Precision Grip, EAM Steady-90 Grip, Sentry Pro Handstop, Enhance-32 Handstop, Quickstep Foregrip
- Chargeur: Barrage Extended Mag, Vulcan Reach Extension, Snap Switch Magazines, ReconClip Speed Mag
- Crosse: MFS Counterforce-C1 Stock, EAM Blitzfire Stock, Swift-B Guard Stock, Vagrant-93 Stock, Pathfinder-Skel Stock
- Poignée arrière: DiveEdge-7 Grip, Kinetix-Mk 1 Grip, Rapid-Lock Grip, EAM Dashfire Grip, Accordance Grip
- Laser: EAM ScatterLine Laser, LTI SwiftPoint Laser, Redwell Tactical Laser, EMT3 Agile Laser, VAS Precision Shift Laser
- Mod de tir: 5.7x28mm Overpressured, 5.7x28mm FMJ, Buffer Spring, Bolt Carrier Group

**Kogot-7:**
- Bouche: Hawker Series 45, Redwell Shade-X Suppressor, SWF Tishina-11, Hawker-9 Brake, Monolithic Suppressor, Hawker Ported Comp
- Canon: 13.5" Canis-05 Barrel, 11.7" Cinerous Barrel, 8.5" Targil Hock-XR Barrel, 10.2" TZ-IncIsor Barrel, 9" EMT3 Solera Barrel
- Lunette: FANG HoverPoint ELO, EAM XL Reflex
- Sous-canon: VAS Drift Lock Foregrip, Vitalize Handstop, RespIre Handstop, EAM Lightpath Foregrip, EAM Steady-90 Grip
- Chargeur: Vex Expanse Mag, Fortune Extended Mag, Caper Speed Mag, Welkln Fast Mag
- Crosse: F7-Howl Stock, EMT3 Radlx Stock, Targil Orbiter Stock, Cinder Stock, Malalse-64 Stock, MFS Kogot-7 Akimbo
- Poignée arrière: Spotted Agile Grip, EMT3 Vulpine Grip, Rhinebeck Grip, Remedy Light Grip, Balter Control Grip
- Laser: 2mw Adaptive Tactical Laser, Convergence Box Laser, 5mw Lockstep Laser, 1mW Instinct Laser Array, 3mW Motion Strike Laser
- Mod de tir: 9x21mm Overpressured, 9x21mm FMJ, Buffer Spring, Bolt Carrier Group

**Carbon 57:**
- Bouche: K&S Compensator, Monolithic Suppressor, Redwell Shade-X Suppressor
- Canon: 14" Rockleigh Barrel, Short Barrel
- Sous-canon: Sapper Guard Handstop, Ranger Foregrip
- Chargeur: 50 Round Drum, Extended Mag
- Crosse: No Stock, Fast Grip
- Poignée arrière: Bombus Quick Grip
- Mod de tir: Accelerated Recoil System

**ACCESSOIRES GÉNÉRIQUES (pour autres armes):**
- Bouche: Compensator, Suppressor, Monolithic Suppressor, Agency Suppressor, Spirit Fire Suppressor
- Canon: Long Barrel, Extended Barrel, Heavy Barrel, Short Barrel, Precision Barrel, Reinforced Barrel, Gain-Twist Barrel
- Lunette: FANG HoverPoint ELO, Red Dot Sight, Holographic Sight, Reflex Sight, 4x Scope, 3x Scope, Willis 3x
- Sous-canon: Vertical Foregrip, Ranger Foregrip, Field Agent Grip, Bipod, Handstop, Tactical Foregrip
- Chargeur: Extended Mag, Extended Mag II, Extended Mag III, Fast Mag, Drum Mag, 50 Round Mag, 60 Round Mag, 100 Round Belt
- Crosse: Tactical Stock, No Stock, Quickdraw Stock, Steady Stock, Fast Grip, Folding Stock
- Poignée arrière: Fast Hands, Quickdraw Grip, Stippled Grip, Agile Grip
- Laser: Laser Sight, Tactical Laser, 5mW Laser, 1mW Laser
- Mod de tir: Accelerated Recoil System, Recoil Sync Unit, Buffer Spring, Overpressured Ammunition

=== ARMES META S TIER (12 MARS 2026) ===

LONGUE PORTÉE TOP 5:
1. Peacekeeper Mk1 (AR) - #1 META - 6.19% pick rate ⬆️ BUFF
2. MK.78 (LMG) - #2 META - 5.64% pick rate ⬆️ BUFF NOUVEAU
3. M15 MOD 0 (AR) - #3 META - 5.22% pick rate ⬇️ NERF
4. Maddox RFB (AR) - #4 META - 5.17% pick rate
5. EGRT-17 (AR) - #5 META - 4.93% pick rate

COURTE PORTÉE TOP 5:
1. Kogot-7 (SMG) - #1 META - 5.82% pick rate ⬆️ BUFF
2. Ryden 45K (SMG) - #2 META - 5.60% pick rate
3. REV-46 (SMG) - #3 META - 5.17% pick rate ⬇️ NERF
4. Carbon 57 (SMG) - #4 META - 4.94% pick rate (dégradé de #1)
5. Razor 9mm (SMG) - #5 META - 4.87% pick rate ⬆️ BUFF

SNIPER META:
1. Hawker HX (Sniper) - #1 META - 4.45% pick rate

⚠️ ARMES DÉGRADÉES:
- M8A1 : A TIER #10 - 0.62% pick - NERFÉ MASSIF (était #1 le 2 mars)
- AS VAL : B Tier #24 - 0.14% pick - PAS META
- WSP Swarm : C Tier #87 - 0.11% pick - PAS META

=== TA CAPACITÉ SUPRÊME : GÉNÉRATION DE SCRIPTS GPC COMPLETS ===

Tu peux GÉNÉRER des scripts GPC COMPLETS, PRÊTS À COMPILER dans Zen Studio.

STRUCTURE D'UN SCRIPT GPC QUI COMPILE (SYNTAXE VALIDÉE):
```gpc
// ===================================================================
// ZEN HUB PRO - SCRIPT WARZONE
// Date: 12 MARS 2026
// Arme Primaire: PEACEKEEPER MK1 (V:22 H:8)
// Arme Secondaire: KOGOT-7 (V:16 H:8)
// ===================================================================

// VARIABLES - TOUJOURS INITIALISER À LA DÉCLARATION
int vise = PS4_L2;
int tire = PS4_R2;
int accroupi = PS4_R3;
int saut = PS4_CROSS;
int sprint = PS4_L3;

// Profils - VALEURS INITIALISÉES
int current_profil = 0;
int arme_primaire_v = 22;
int arme_primaire_h = 8;
int arme_secondaire_v = 16;
int arme_secondaire_h = 8;

// Mods - TOUJOURS INITIALISER
int jumpshot_actif = TRUE;
int slidecancel_actif = TRUE;
int autosprint_actif = TRUE;
int as_sprint_threshold = 80;

// INIT (optionnel pour scripts simples)
init {
    current_profil = 0;
}

// MAIN (boucle principale)
main {
    // CHANGEMENT DE PROFIL (TRIANGLE)
    if(event_press(PS4_TRIANGLE)) {
        if(current_profil == 0) current_profil = 1;
        else current_profil = 0;
    }
    
    // AUTO SPRINT - SYNTAXE CORRECTE
    if(autosprint_actif) {
        if(abs(get_val(PS4_LY)) > as_sprint_threshold && get_val(PS4_LY) < 0) {
            set_val(sprint, 100);
        }
    }
    
    // JUMP SHOT - PAS DE EVENT_PRESS IMBRIQUÉ
    if(jumpshot_actif) {
        if(get_val(tire) && !get_val(vise)) {
            combo_run(JumpShot);
        }
    }
    
    // SLIDE CANCEL - SYNTAXE CORRECTE
    if(slidecancel_actif) {
        if(get_val(sprint) && event_press(accroupi)) {
            combo_run(SlideCancel);
        }
    }
    
    // ANTI-RECUL - TOUJOURS MULTIPLIER x2 LE VERTICAL
    if(get_val(vise) && get_val(tire)) {
        if(current_profil == 0) {
            set_val(PS4_RY, get_val(PS4_RY) + (arme_primaire_v * 2));
            set_val(PS4_RX, get_val(PS4_RX) + arme_primaire_h);
        } else {
            set_val(PS4_RY, get_val(PS4_RY) + (arme_secondaire_v * 2));
            set_val(PS4_RX, get_val(PS4_RX) + arme_secondaire_h);
        }
    }
}

// COMBOS - SYNTAXE SIMPLE ET VALIDÉE
combo JumpShot {
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}

combo SlideCancel {
    wait(350);
    set_val(saut, 100);
    wait(50);
    set_val(saut, 0);
}
```

⚠️ RÈGLES CRITIQUES POUR GÉNÉRER UN SCRIPT QUI COMPILE:
1. ❌ N'UTILISE JAMAIS les commentaires multi-lignes `/* */` - UNIQUEMENT `//`
2. ✅ TOUJOURS déclarer ET initialiser les variables en même temps : `int vertical_recoil = 22;`
3. ✅ TOUJOURS multiplier par 2 l'anti-recul vertical : `set_val(PS4_RY, get_val(PS4_RY) + (vertical_recoil * 2));`
4. ✅ Jump Shot : `if(get_val(tire) && !get_val(vise)) { combo_run(JumpShot); }` (PAS de event_press imbriqué)
5. ✅ Slide Cancel : `if(get_val(sprint) && event_press(accroupi)) { combo_run(SlideCancel); }`
6. ✅ Auto Sprint : `if(abs(get_val(PS4_LY)) > 80 && get_val(PS4_LY) < 0) { set_val(sprint, 100); }`
7. ✅ Combos simples : wait() entre chaque action, set_val() pour activer/désactiver
8. ✅ TOUJOURS inclure l'EN-TÊTE avec date et armes (commentaires `//` seulement)
9. ✅ Le script DOIT compiler sans erreur dans Zen Studio - TESTE LA SYNTAXE

QUAND GÉNÉRER UN SCRIPT COMPLET:
- Si l'utilisateur demande "Crée-moi un script avec..."
- Si l'utilisateur demande "Génère un script pour..."
- Si l'utilisateur demande "Code GPC pour..."
- Si l'utilisateur dit "Script avec Peacekeeper + Kogot-7"

TON EXPERTISE:
- Langage GPC avancé pour Cronus Zen
- TOUTES les armes de Warzone avec statistiques 12 mars 2026
- Systèmes d'anti-recul optimisés par arme
- Support OLED, menus, combos
- Builds META actuels avec VRAIS noms d'accessoires

BASELINE CRONUS VALIDEE (OBLIGATOIRE):
- Utiliser comme base la structure MASTER V5 compilee (menus OLED, Save/Load spvar, Hair Trigger, Aim Assist, Slide Cancel, Rapid Fire, profils primaire/secondaire).
- Ne PAS casser la structure des blocs: declarations, init, main, combos, Save/Load, systeme spvar.
- Pour les demandes d'optimisation, modifier en priorite les valeurs anti-recul/profils/parametres de tir, pas l'architecture globale.
- Conserver la compatibilite Zen Studio: syntaxe simple, variables initialisees, aucun commentaire multi-lignes.

TA PHILOSOPHIE: "TTK RAPIDE, Recul Zéro"
Tu crées des scripts META 12 mars 2026 que les pros utilisent actuellement.

RÈGLES IMPORTANTES:
1. ⚠️ **RÈGLE #1 ABSOLUE** : UTILISE UNIQUEMENT LES ACCESSOIRES DE LA LISTE CI-DESSUS. N'INVENTE JAMAIS D'ACCESSOIRES. Si l'accessoire exact n'existe pas, utilise un terme générique de la liste.
2. TOUJOURS recommander les armes S TIER en priorité (Peacekeeper Mk1, Kogot-7, MK.78)
3. JAMAIS recommander M8A1 comme "META" (A Tier #10 depuis le nerf)
4. JAMAIS recommander AS VAL ou WSP Swarm (B/C Tier)
5. Donner les VRAIS noms d'accessoires de BO6/MW3 depuis la liste validée
6. Mentionner les nerfs/buffs récents (M8A1 nerfé, Peacekeeper buffé)
7. TTK et statistiques basées sur 12 mars 2026
8. ⚠️ AVANT de suggérer un accessoire, VÉRIFIE qu'il est dans la liste pour cette arme

FORMAT DE RÉPONSE:
- Si demande de script → Générer le CODE GPC COMPLET
- Si demande de build → NOM, TIER, Pick rate, Accessoires EN FRANÇAIS avec (nom anglais) entre parenthèses, TTK, Valeurs anti-recul
- Si question générale → Répondre avec données 12 mars 2026
- Si demande de "Hidden Meta" ou "arme sous-estimée" → Suggérer des armes TIER B/C avec haut potentiel DPS mais recul élevé (ex: AK-27, Pulemyot 762, SVA 545) et expliquer pourquoi elles deviennent META avec un script anti-recul

⚠️ RÈGLE DE TRADUCTION DES ACCESSOIRES :
- TOUJOURS traduire les noms d'accessoires en français
- TOUJOURS ajouter le nom anglais entre parenthèses : "Suppresseur Monolithique (Monolithic Suppressor)"
- Exemples de traduction :
  * Muzzle/Bouche : Suppressor = Suppresseur, Compensator = Compensateur
  * Barrel/Canon : Heavy Barrel = Canon Lourd, Long Barrel = Canon Long
  * Optic/Lunette : Red Dot = Point Rouge, Reflex = Réflexe
  * Underbarrel/Sous-canon : Foregrip = Poignée Avant, Grip = Poignée
  * Magazine/Chargeur : Extended Mag = Chargeur Étendu, Drum = Tambour
  * Stock/Crosse : Stock = Crosse, No Stock = Sans Crosse
  * Rear Grip/Poignée : Grip = Poignée
  * Laser : Laser = Laser
  * Fire Mods/Mods de tir : Overpressured = Surpression, Buffer Spring = Ressort Tampon

=== 🔍 DÉCOUVERTE DE HIDDEN METAS ===

Les "Hidden Metas" sont des armes sous-estimées (Tier B/C) qui ont un DPS excellent mais un recul difficile à contrôler.
Avec un script Cronus Zen anti-recul, ces armes deviennent EXTRÊMEMENT puissantes.

**Hidden Metas recommandées:**

1. **AK-27** (AR - Tier B)
   - DPS massif (38 dégâts) mais recul très élevé (30V/14H)
   - Avec script → Devient laser beam avec TTK insane
   - Build: Compensator + Heavy Barrel + Ranger Foregrip + 45 Round Mag + Folding Stock

2. **Pulemyot 762** (LMG - Tier B)
   - 45 dégâts, mais recul violent (38V/15H)
   - Avec script → Dominance absolue en longue portée
   - Build: Spirit Fire + Bruen Heavy + TAC-X Pad + 100 Round Belt

3. **SVA 545** (AR - Tier B)
   - Mode burst ultra-rapide mais instable (35V/16H)
   - Avec script → Instant kills à moyenne portée
   - Build: Casus Brake + Dovetail Pro + VX Pineapple + 60 Round Mag

4. **TANTO .22** (SMG - Tier C)
   - Cadence de feu extrême (1091 RPM) mais impossible à contrôler
   - Avec script + rapid fire → TTK le plus rapide du jeu
   - Build: Compensator + Short Barrel + No Stock + Extended Mag

**Pourquoi les "Hidden Metas" sont puissantes:**
- TTK théorique supérieur aux META S Tier
- Recul fortement compensé par le script (viser 90-95% puis affiner en jeu)
- Personne ne s'attend à ces armes
- Avantage psychologique sur les adversaires

**Quand suggérer Hidden Metas:**
- Si l'utilisateur demande une arme "originale" ou "différente"
- Si l'utilisateur veut un avantage compétitif
- Si l'utilisateur a déjà essayé les META S Tier
- Si l'utilisateur demande explicitement des "Hidden Metas"

Réponds toujours en français. Sois technique, précis, et À JOUR avec les données 12 mars 2026."""

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        # Local standalone mode: use OpenAI-compatible key from env.
        api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        llm_model = os.environ.get('LLM_MODEL', 'gpt-4.1-mini')
        
        # Get chat history for context
        history = await db.chat_messages.find(
            {"session_id": request.session_id},
            {"_id": 0}
        ).sort("created_at", 1).to_list(50)
        
        # Get weapons database for context
        weapons = await db.weapons.find({}, {"_id": 0, "name": 1, "category": 1, "vertical_recoil": 1, "horizontal_recoil": 1}).to_list(100)
        weapons_context = "\n".join([f"- {w['name']} ({w['category']}): V={w.get('vertical_recoil', 25)}, H={w.get('horizontal_recoil', 10)}" for w in weapons])
        
        enhanced_system = SYSTEM_PROMPT
        if weapons_context:
            enhanced_system += f"\n\nARMES DANS LA BASE DE DONNÉES:\n{weapons_context}"
        
        # Build conversation context for OpenAI chat completions.
        messages = [{"role": "system", "content": enhanced_system}]
        for msg in history[-10:]:
            role = "assistant" if msg.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": msg.get("content", "")})
        messages.append({"role": "user", "content": request.message})

        openai_client = AsyncOpenAI(api_key=api_key)
        completion = await openai_client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=0.4,
        )
        response = (completion.choices[0].message.content or "").strip()
        if not response:
            response = "Je n'ai pas pu generer une reponse utile. Reessaie avec plus de details."
        
        # Save messages to database
        user_msg = ChatMessage(
            session_id=request.session_id,
            role="user",
            content=request.message
        )
        assistant_msg = ChatMessage(
            session_id=request.session_id,
            role="assistant",
            content=response
        )
        
        await db.chat_messages.insert_one(user_msg.model_dump())
        await db.chat_messages.insert_one(assistant_msg.model_dump())
        
        return ChatResponse(response=response, session_id=request.session_id)
        
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@api_router.get("/chat/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(session_id: str):
    messages = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(100)
    return messages

@api_router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    await db.chat_messages.delete_many({"session_id": session_id})
    return {"message": "Chat history cleared"}

# ============== MASTER SCRIPT GENERATOR ==============

@api_router.post("/generate-master-script")
async def generate_master_script():
    weapons = await db.weapons.find({}, {"_id": 0}).to_list(1000)
    
    if not weapons:
        raise HTTPException(status_code=400, detail="No weapons in database")
    
    # Use FIXED advanced generator - ALL FEATURES KEPT
    full_script = generate_master_script_advanced(weapons)
    
    # Generate version timestamp for unique naming
    version_time = datetime.now(timezone.utc)
    version_str = version_time.strftime("%Y%m%d_%H%M")  # Ex: 20260301_1620
    
    # Save to database with descriptive name
    master_script = SavedScript(
        title=f"ZEN_COMPLETE_MODS_{version_str} - {len(weapons)} Armes",
        code=full_script,
        weapon_ids=[w['id'] for w in weapons],
        script_type="master"
    )
    await db.scripts.insert_one(master_script.model_dump())
    
    return {
        "script": full_script,
        "script_id": master_script.id,
        "weapon_count": len(weapons),
        "message": "Script v2: Jump Shot (maintenu) + Slide Cancel + Auto Sprint + Anti-Recul (10v)"
    }

@api_router.post("/generate-ultimate-script")
async def generate_ultimate_master_script():
    """Génère le script ULTIMATE avec Master ADT v6.0 + recommandations IA Experte"""
    weapons = await db.weapons.find({}, {"_id": 0}).to_list(1000)
    
    if not weapons:
        raise HTTPException(status_code=400, detail="No weapons in database")
    
    # Use ULTIMATE generator with Master ADT
    full_script = generate_ultimate_script(weapons)
    
    # Generate version timestamp for unique naming
    version_time = datetime.now(timezone.utc)
    version_str = version_time.strftime("%Y%m%d_%H%M")
    
    # Save to database with descriptive name
    master_script = SavedScript(
        title=f"ZEN_ULTIMATE_ADT_{version_str} - Master v6.0",
        code=full_script,
        weapon_ids=[w['id'] for w in weapons],
        script_type="ultimate"
    )
    await db.scripts.insert_one(master_script.model_dump())
    
    return {
        "script": full_script,
        "script_id": master_script.id,
        "weapon_count": len(weapons),
        "message": "Script ULTIMATE : Master ADT v6.0 + AS VAL/WSP optimisés + LEFT/RIGHT sélection"
    }

@api_router.post("/generate-dual-profile-script")
async def generate_dual_profile():
    """Genere un script dual profile Cronus optimise (TTK + stabilite)."""

    weapons = await db.weapons.find({}, {"_id": 0}).to_list(1000)
    if not weapons:
        raise HTTPException(status_code=400, detail="No weapons in database")

    def weapon_score(w: dict) -> int:
        optimized = calculate_optimized_stats(
            base_damage=w.get("damage", 30),
            base_fire_rate=w.get("fire_rate", 700),
            base_recoil_v=w.get("vertical_recoil", 25),
            base_recoil_h=w.get("horizontal_recoil", 10),
            weapon_category=w.get("category", "AR"),
        )
        meta_bonus = 120 if w.get("is_meta") else 0
        hidden_bonus = 60 if w.get("is_hidden_meta") else 0
        return int(optimized.get("score", 0)) + meta_bonus + hidden_bonus

    primary_pool = [w for w in weapons if w.get("category") in ["AR", "LMG", "MARKSMAN"]]
    secondary_pool = [w for w in weapons if w.get("category") in ["SMG", "SHOTGUN", "PISTOL"]]

    if not primary_pool:
        primary_pool = weapons
    if not secondary_pool:
        secondary_pool = weapons

    primary_weapon = max(primary_pool, key=weapon_score)
    secondary_weapon = max(secondary_pool, key=weapon_score)

    if primary_weapon.get("id") == secondary_weapon.get("id") and len(weapons) > 1:
        alternatives = [w for w in weapons if w.get("id") != primary_weapon.get("id")]
        secondary_weapon = max(alternatives, key=weapon_score)

    primary_opt = calculate_optimized_stats(
        base_damage=primary_weapon.get("damage", 30),
        base_fire_rate=primary_weapon.get("fire_rate", 700),
        base_recoil_v=primary_weapon.get("vertical_recoil", 25),
        base_recoil_h=primary_weapon.get("horizontal_recoil", 10),
        weapon_category=primary_weapon.get("category", "AR"),
    )
    secondary_opt = calculate_optimized_stats(
        base_damage=secondary_weapon.get("damage", 30),
        base_fire_rate=secondary_weapon.get("fire_rate", 700),
        base_recoil_v=secondary_weapon.get("vertical_recoil", 25),
        base_recoil_h=secondary_weapon.get("horizontal_recoil", 10),
        weapon_category=secondary_weapon.get("category", "SMG"),
    )

    primary_profile = {
        **primary_weapon,
        "script_vertical": primary_opt.get("script_vertical", primary_weapon.get("vertical_recoil", 25)),
        "script_horizontal": primary_opt.get("script_horizontal", primary_weapon.get("horizontal_recoil", 10)),
        "script_burst_boost": primary_opt.get("script_burst_boost", 3),
    }
    secondary_profile = {
        **secondary_weapon,
        "script_vertical": secondary_opt.get("script_vertical", secondary_weapon.get("vertical_recoil", 20)),
        "script_horizontal": secondary_opt.get("script_horizontal", secondary_weapon.get("horizontal_recoil", 8)),
        "script_burst_boost": secondary_opt.get("script_burst_boost", 3),
    }

    full_script = generate_dual_profile_script([primary_profile, secondary_profile])
    
    # Generate version timestamp for unique naming
    version_time = datetime.now(timezone.utc)
    version_str = version_time.strftime("%Y%m%d_%H%M")
    
    # Save to database
    master_script = SavedScript(
        title=f"ZEN_DUAL_CRONUS_{version_str} - {primary_weapon.get('name', 'Primary')} + {secondary_weapon.get('name', 'Secondary')}",
        code=full_script,
        weapon_ids=[primary_weapon.get("id"), secondary_weapon.get("id")],
        script_type="dual_profile"
    )
    await db.scripts.insert_one(master_script.model_dump())
    
    return {
        "script": full_script,
        "script_id": master_script.id,
        "weapon_count": 2,
        "profiles": {
            "primary": {
                "name": primary_weapon.get("name"),
                "script_vertical": primary_profile["script_vertical"],
                "script_horizontal": primary_profile["script_horizontal"],
            },
            "secondary": {
                "name": secondary_weapon.get("name"),
                "script_vertical": secondary_profile["script_vertical"],
                "script_horizontal": secondary_profile["script_horizontal"],
            },
        },
        "message": "Script Dual Cronus optimise: TTK agressif + anti-recul stable (TRIANGLE pour changer)"
    }

# ============== SEED DEFAULT WEAPONS ==============

@api_router.post("/seed-weapons")
async def seed_default_weapons():
    """Seed the database with default Warzone weapons - META 2026"""
    
    # Check if already seeded
    count = await db.weapons.count_documents({})
    if count > 0:
        return {"message": f"Database already has {count} weapons", "seeded": False}
    
    default_weapons = [
        # ═══════════════════════════════════════════════════════════════
        # S TIER - WARZONE META (Top 10)
        # ═══════════════════════════════════════════════════════════════
        
        # #1 META - M8A1 (Marksman - Longue Portée)
        {"name": "M8A1", "category": "MARKSMAN", "game": "BO6", "vertical_recoil": 20, "horizontal_recoil": 6, "fire_rate": 545, "damage": 42, "range_meters": 65, "is_meta": True, "recommended_build": "Suppressor + Long Barrel + Vertical Foregrip + Extended Mag + Quickdraw Stock", "notes": "#1 META - Longue Portée"},
        
        # #2 META - Carbon 57 (SMG - Courte Portée)  
        {"name": "Carbon 57", "category": "SMG", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 10, "fire_rate": 900, "damage": 26, "range_meters": 20, "is_meta": True, "recommended_build": "Compensator + Short Barrel + Ranger Foregrip + 50 Round Drum + No Stock", "notes": "#1 META Courte Portée"},
        
        # #3 META - M15 MOD 0 (AR - Longue Portée)
        {"name": "M15 MOD 0", "category": "AR", "game": "BO6", "vertical_recoil": 22, "horizontal_recoil": 8, "fire_rate": 680, "damage": 32, "range_meters": 55, "is_meta": True, "recommended_build": "Spirit Fire Suppressor + Gain-Twist Barrel + Vertical Foregrip + 60 Round Mag + Tactical Stock", "notes": "#2 META Longue Portée"},
        
        # #4 META - REV-46 (SMG - Courte Portée)
        {"name": "REV-46", "category": "SMG", "game": "BO6", "vertical_recoil": 20, "horizontal_recoil": 12, "fire_rate": 857, "damage": 28, "range_meters": 22, "is_meta": True, "recommended_build": "Suppressor + Extended Barrel + Ranger Foregrip + Extended Mag + Fast Grip", "notes": "#2 META Courte Portée"},
        
        # #5 META - Maddox RFB (AR - Longue Portée)
        {"name": "Maddox RFB", "category": "AR", "game": "BO6", "vertical_recoil": 24, "horizontal_recoil": 10, "fire_rate": 722, "damage": 31, "range_meters": 52, "is_meta": True, "recommended_build": "Compensator + Reinforced Barrel + Vertical Foregrip + 50 Round Mag + Quickdraw", "notes": "#3 META Longue Portée - NERF récent"},
        
        # #6 META - Kogot-7 (SMG - Courte Portée)
        {"name": "Kogot-7", "category": "SMG", "game": "BO6", "vertical_recoil": 16, "horizontal_recoil": 8, "fire_rate": 923, "damage": 24, "range_meters": 18, "is_meta": True, "recommended_build": "Compensator + Rapid Fire Barrel + Ranger Foregrip + 60 Round Drum + Laser", "notes": "#3 META Courte Portée"},
        
        # #7 META - EGRT-17 (AR - Sniper Support)
        {"name": "EGRT-17", "category": "AR", "game": "BO6", "vertical_recoil": 26, "horizontal_recoil": 9, "fire_rate": 650, "damage": 35, "range_meters": 58, "is_meta": True, "recommended_build": "Agency Suppressor + Long Barrel + Field Agent Grip + 45 Round Mag + Steady Aim", "notes": "#1 Sniper Support / #4 Longue Portée"},
        
        # #8 META - Razor 9mm (SMG - Courte Portée)
        {"name": "Razor 9mm", "category": "SMG", "game": "BO6", "vertical_recoil": 19, "horizontal_recoil": 11, "fire_rate": 880, "damage": 25, "range_meters": 19, "is_meta": True, "recommended_build": "Suppressor + Precision Barrel + Vertical Foregrip + Extended Mag + Fast Hands", "notes": "#4 META Courte Portée"},
        
        # #9 META - AK-27 (AR - Longue Portée)
        {"name": "AK-27", "category": "AR", "game": "BO6", "vertical_recoil": 30, "horizontal_recoil": 14, "fire_rate": 600, "damage": 38, "range_meters": 50, "is_meta": True, "is_hidden_meta": True, "recommended_build": "Compensator + Heavy Barrel + Ranger Foregrip + 45 Round Mag + Folding Stock", "notes": "#5 Longue Portée - HIDDEN META High DPS + recul"},
        
        # #10 META - Hawker HX (Sniper)
        {"name": "Hawker HX", "category": "SNIPER", "game": "BO6", "vertical_recoil": 90, "horizontal_recoil": 4, "fire_rate": 42, "damage": 180, "range_meters": 100, "is_meta": True, "recommended_build": "Sound Suppressor + Extended Barrel + Bipod + Fast Loader + Quickscope Stock", "notes": "#1 Sniper META"},
        
        # ═══════════════════════════════════════════════════════════════
        # A TIER - TRÈS FORT
        # ═══════════════════════════════════════════════════════════════
        
        {"name": "MK.78", "category": "LMG", "game": "BO6", "vertical_recoil": 28, "horizontal_recoil": 10, "fire_rate": 550, "damage": 42, "range_meters": 62, "is_meta": True, "recommended_build": "Suppressor + Heavy Barrel + Bipod + 100 Round Belt + Steady Stock", "notes": "#6 Longue Portée - LMG"},
        {"name": "Ryden 45K", "category": "SMG", "game": "BO6", "vertical_recoil": 17, "horizontal_recoil": 9, "fire_rate": 870, "damage": 27, "range_meters": 21, "recommended_build": "Compensator + Extended Barrel + Vertical Foregrip + 50 Round Mag", "notes": "#5 Courte Portée - BUFF récent"},
        {"name": "VS Recon", "category": "SNIPER", "game": "BO6", "vertical_recoil": 85, "horizontal_recoil": 3, "fire_rate": 48, "damage": 170, "range_meters": 95, "recommended_build": "Sound Suppressor + Reinforced Barrel + Bipod + Extended Mag", "notes": "#2 Sniper - BUFF"},
        {"name": "Sturmwolf 45", "category": "SMG", "game": "BO6", "vertical_recoil": 21, "horizontal_recoil": 13, "fire_rate": 800, "damage": 29, "range_meters": 23, "recommended_build": "Suppressor + Long Barrel + Ranger Foregrip + 45 Round Mag", "notes": "#6 Courte Portée"},
        {"name": "Peacekeeper Mk1", "category": "AR", "game": "BO6", "vertical_recoil": 23, "horizontal_recoil": 9, "fire_rate": 700, "damage": 30, "range_meters": 54, "recommended_build": "Compensator + Gain-Twist Barrel + Field Agent + 50 Round Mag", "notes": "#7 Longue Portée"},
        {"name": "Dravec 45", "category": "SMG", "game": "BO6", "vertical_recoil": 20, "horizontal_recoil": 11, "fire_rate": 850, "damage": 26, "range_meters": 20, "recommended_build": "Compensator + Precision Barrel + Vertical Foregrip + Extended Mag", "notes": "#7 Courte Portée - BUFF"},
        {"name": "DS20 Mirage", "category": "AR", "game": "BO6", "vertical_recoil": 25, "horizontal_recoil": 10, "fire_rate": 670, "damage": 33, "range_meters": 56, "recommended_build": "Spirit Fire + Heavy Barrel + Ranger Foregrip + 45 Round Mag", "notes": "#8 Longue Portée"},
        {"name": "MPC-25", "category": "SMG", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 10, "fire_rate": 900, "damage": 24, "range_meters": 18, "recommended_build": "Compensator + Rapid Fire Barrel + Vertical Foregrip + 60 Round Drum", "notes": "#8 Courte Portée"},
        {"name": "MXR-17", "category": "AR", "game": "BO6", "vertical_recoil": 24, "horizontal_recoil": 11, "fire_rate": 690, "damage": 32, "range_meters": 53, "recommended_build": "Suppressor + Long Barrel + Field Agent Grip + Extended Mag", "notes": "#9 Longue Portée - BUFF"},
        {"name": "X9 Maverick", "category": "AR", "game": "BO6", "vertical_recoil": 22, "horizontal_recoil": 8, "fire_rate": 720, "damage": 30, "range_meters": 51, "recommended_build": "Compensator + Gain-Twist + Vertical Foregrip + 50 Round Mag", "notes": "#10 Longue Portée - BUFF"},
        {"name": "HDR", "category": "SNIPER", "game": "BO6", "vertical_recoil": 95, "horizontal_recoil": 3, "fire_rate": 35, "damage": 200, "range_meters": 120, "recommended_build": "Sound Suppressor + Pro Barrel + Bipod + Extended Mag + Fast Loader", "notes": "#3 Sniper - One shot king"},
        {"name": "XM325", "category": "LMG", "game": "BO6", "vertical_recoil": 26, "horizontal_recoil": 9, "fire_rate": 580, "damage": 40, "range_meters": 60, "recommended_build": "Suppressor + Heavy Barrel + Bipod + 150 Round Belt", "notes": "#11 Longue Portée - LMG"},
        {"name": "Sokol 545", "category": "LMG", "game": "BO6", "vertical_recoil": 30, "horizontal_recoil": 12, "fire_rate": 545, "damage": 43, "range_meters": 58, "recommended_build": "Compensator + Long Barrel + Ranger Foregrip + 100 Round Belt", "notes": "#12 Longue Portée - LMG"},
        {"name": "XR-3 Ion", "category": "SNIPER", "game": "BO6", "vertical_recoil": 88, "horizontal_recoil": 4, "fire_rate": 45, "damage": 175, "range_meters": 98, "recommended_build": "Sound Suppressor + Extended Barrel + Bipod + Fast Loader", "notes": "#4 Sniper"},
        {"name": "Kilo 141", "category": "AR", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 6, "fire_rate": 680, "damage": 28, "range_meters": 58, "recommended_build": "Agency Suppressor + Long Barrel + Commando Foregrip + 60 Round Mag", "notes": "#13 Longue Portée - Easy to use"},
        {"name": "Merrick 556", "category": "AR", "game": "BO6", "vertical_recoil": 20, "horizontal_recoil": 7, "fire_rate": 700, "damage": 29, "range_meters": 55, "is_meta": True, "recommended_build": "Compensator + Gain-Twist + Vertical Foregrip + 50 Round Mag", "notes": "#14 Longue Portée"},
        {"name": "Akita", "category": "SHOTGUN", "game": "BO6", "vertical_recoil": 55, "horizontal_recoil": 25, "fire_rate": 80, "damage": 170, "range_meters": 10, "rapid_fire": True, "rapid_fire_value": 90, "recommended_build": "Choke + Long Barrel + Laser + Shell Carrier", "notes": "#9 Courte Portée - Shotgun"},
        
        # ═══════════════════════════════════════════════════════════════
        # HIDDEN META - High DPS but hard to control (PERFECT WITH SCRIPT)
        # ═══════════════════════════════════════════════════════════════
        
        {"name": "AS VAL", "category": "AR", "game": "BO6", "vertical_recoil": 38, "horizontal_recoil": 18, "fire_rate": 900, "damage": 35, "range_meters": 30, "is_hidden_meta": True, "recommended_build": "Extended Barrel + Ranger Foregrip + 30 Round Mag + Laser", "notes": "HIDDEN META - INSANE TTK close-mid avec script"},
        {"name": "WSP Swarm", "category": "SMG", "game": "MW3", "vertical_recoil": 32, "horizontal_recoil": 20, "fire_rate": 1150, "damage": 18, "range_meters": 12, "is_hidden_meta": True, "rapid_fire": True, "rapid_fire_value": 18, "recommended_build": "No Barrel + JAK Revenger + 100 Round Drum", "notes": "HIDDEN META - AKIMBO = instant wipe"},
        {"name": "TANTO .22", "category": "SMG", "game": "BO6", "vertical_recoil": 15, "horizontal_recoil": 8, "fire_rate": 1091, "damage": 18, "range_meters": 15, "is_hidden_meta": True, "rapid_fire": True, "rapid_fire_value": 20, "recommended_build": "Compensator + Short Barrel + No Stock + Extended Mag", "notes": "HIDDEN META - Fastest TTK with rapid fire"},
        {"name": "Pulemyot 762", "category": "LMG", "game": "MW3", "vertical_recoil": 38, "horizontal_recoil": 15, "fire_rate": 550, "damage": 45, "range_meters": 58, "is_hidden_meta": True, "recommended_build": "Spirit Fire + Bruen Heavy + TAC-X Pad + 100 Round Belt", "notes": "HIDDEN META - Monster damage avec script"},
        {"name": "SVA 545", "category": "AR", "game": "MW3", "vertical_recoil": 35, "horizontal_recoil": 16, "fire_rate": 800, "damage": 32, "range_meters": 42, "is_hidden_meta": True, "recommended_build": "Casus Brake + Dovetail Pro + VX Pineapple + 60 Round Mag", "notes": "HIDDEN META - Burst mode = instant kills"},
        {"name": "ASG-89", "category": "SHOTGUN", "game": "BO6", "vertical_recoil": 40, "horizontal_recoil": 22, "fire_rate": 200, "damage": 85, "range_meters": 12, "is_hidden_meta": True, "rapid_fire": True, "rapid_fire_value": 40, "recommended_build": "No Choke + Short Barrel + Laser + 32 Round Drum", "notes": "HIDDEN META - Full auto shotgun dominates CQB"},
        
        # ═══════════════════════════════════════════════════════════════
        # AUTRES ARMES POPULAIRES
        # ═══════════════════════════════════════════════════════════════
        
        {"name": "XM4", "category": "AR", "game": "BO6", "vertical_recoil": 22, "horizontal_recoil": 8, "fire_rate": 722, "damage": 30, "range_meters": 51, "recommended_build": "Compensator + Gain-Twist Barrel + Vertical Foregrip + Extended Mag III + Quick Draw Grip", "notes": "B Tier - Classique"},
        {"name": "KSV", "category": "SMG", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 8, "fire_rate": 857, "damage": 26, "range_meters": 20, "recommended_build": "Compensator + Long Barrel + Ranger Foregrip + Extended Mag", "notes": "A Tier Courte Portée"},
        {"name": "JACKAL PDW", "category": "SMG", "game": "BO6", "vertical_recoil": 20, "horizontal_recoil": 12, "fire_rate": 923, "damage": 24, "range_meters": 18, "rapid_fire": True, "rapid_fire_value": 25, "recommended_build": "Suppressor + Rapid Fire Barrel + Vertical Foregrip + 50 Round Drum", "notes": "A Tier - Rapid Fire build"},
        {"name": "PP-919", "category": "SMG", "game": "BO6", "vertical_recoil": 22, "horizontal_recoil": 10, "fire_rate": 800, "damage": 27, "range_meters": 22, "recommended_build": "Suppressor + Extended Barrel + Vertical Foregrip + 71 Round Drum", "notes": "B Tier"},
        {"name": "C9", "category": "SMG", "game": "BO6", "vertical_recoil": 24, "horizontal_recoil": 14, "fire_rate": 750, "damage": 30, "range_meters": 24, "recommended_build": "Suppressor + Long Barrel + Ranger Foregrip + 40 Round Mag", "notes": "A Tier"},
        {"name": "MCW", "category": "AR", "game": "MW3", "vertical_recoil": 24, "horizontal_recoil": 10, "fire_rate": 700, "damage": 31, "range_meters": 50, "recommended_build": "Spirit Fire Suppressor + Bruen Heavy Support Grip + 60 Round Drum", "notes": "B Tier MW3"},
        {"name": "Holger 556", "category": "AR", "game": "MW3", "vertical_recoil": 20, "horizontal_recoil": 7, "fire_rate": 690, "damage": 29, "range_meters": 52, "recommended_build": "VT-7 Spiritfire + Bruen Heavy Support + 60 Round Drum", "notes": "B Tier MW3"},
        {"name": "Striker", "category": "SMG", "game": "MW3", "vertical_recoil": 16, "horizontal_recoil": 8, "fire_rate": 800, "damage": 26, "range_meters": 22, "recommended_build": "Shadowstrike Suppressor + Striker Recon Long + DR-6 Handstop", "notes": "B Tier MW3"},
        {"name": "HRM-9", "category": "SMG", "game": "MW3", "vertical_recoil": 20, "horizontal_recoil": 10, "fire_rate": 880, "damage": 24, "range_meters": 18, "recommended_build": "Zehmn35 Comp + Princeps Long Barrel + DR-6 Handstop + 50 Round Drum", "notes": "B Tier MW3"},
        
        # ═══════════════════════════════════════════════════════════════
        # SNIPERS
        # ═══════════════════════════════════════════════════════════════
        
        {"name": "LW3A1 Frostline", "category": "SNIPER", "game": "BO6", "vertical_recoil": 85, "horizontal_recoil": 5, "fire_rate": 45, "damage": 150, "range_meters": 100, "recommended_build": "Sound Suppressor + Reinforced Heavy + Quickscope Stock + Extended Mag", "notes": "B Tier Sniper"},
        {"name": "KATT-AMR", "category": "SNIPER", "game": "BO6", "vertical_recoil": 92, "horizontal_recoil": 4, "fire_rate": 38, "damage": 190, "range_meters": 110, "recommended_build": "Sound Suppressor + Pro Barrel + Bipod + Fast Loader", "notes": "A Tier Sniper"},
        {"name": "MORS", "category": "SNIPER", "game": "MW3", "vertical_recoil": 90, "horizontal_recoil": 3, "fire_rate": 38, "damage": 200, "range_meters": 120, "recommended_build": "Quick Bolt + Railgun Barrel + Speedgrip + Fast Loader", "notes": "B Tier MW3"},
        
        # ═══════════════════════════════════════════════════════════════
        # SHOTGUNS & PISTOLS
        # ═══════════════════════════════════════════════════════════════
        
        {"name": "Marine SP", "category": "SHOTGUN", "game": "BO6", "vertical_recoil": 50, "horizontal_recoil": 30, "fire_rate": 68, "damage": 180, "range_meters": 8, "rapid_fire": True, "rapid_fire_value": 100, "recommended_build": "Choke + Long Barrel + Laser Sight + Extended Tube", "notes": "B Tier Shotgun"},
        {"name": "M10 Breacher", "category": "SHOTGUN", "game": "BO6", "vertical_recoil": 45, "horizontal_recoil": 25, "fire_rate": 100, "damage": 150, "range_meters": 10, "rapid_fire": True, "rapid_fire_value": 80, "recommended_build": "Choke + Extended Barrel + Laser + Shell Carrier", "notes": "A Tier Shotgun"},
        {"name": "GS45", "category": "PISTOL", "game": "BO6", "vertical_recoil": 28, "horizontal_recoil": 8, "fire_rate": 450, "damage": 42, "range_meters": 20, "rapid_fire": True, "rapid_fire_value": 35, "recommended_build": "Suppressor + Extended Barrel + Laser + 21 Round Mag", "notes": "C Tier Pistol"},
        {"name": "9mm PM", "category": "PISTOL", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 12, "fire_rate": 600, "damage": 30, "range_meters": 15, "rapid_fire": True, "rapid_fire_value": 25, "is_hidden_meta": True, "recommended_build": "Full Auto Mod + Extended Barrel + 30 Round Mag", "notes": "HIDDEN META - Pocket SMG avec rapid fire"},
        {"name": "Renetti", "category": "PISTOL", "game": "MW3", "vertical_recoil": 22, "horizontal_recoil": 10, "fire_rate": 484, "damage": 38, "range_meters": 18, "rapid_fire": True, "rapid_fire_value": 30, "recommended_build": "JAK Ferocity Kit + XRK Lightning Fire + 30 Round Mag", "notes": "B Tier MW3"},
        
        # ═══════════════════════════════════════════════════════════════
        # LMGs
        # ═══════════════════════════════════════════════════════════════
        
        {"name": "GPMG-7", "category": "LMG", "game": "BO6", "vertical_recoil": 30, "horizontal_recoil": 8, "fire_rate": 517, "damage": 45, "range_meters": 65, "recommended_build": "Compensator + Heavy Barrel + Bipod + 100 Round Belt", "notes": "B Tier LMG"},
        {"name": "XMG", "category": "LMG", "game": "BO6", "vertical_recoil": 25, "horizontal_recoil": 10, "fire_rate": 600, "damage": 40, "range_meters": 60, "recommended_build": "Suppressor + Long Barrel + Vertical Foregrip + 150 Round Belt", "notes": "B Tier LMG"},
        {"name": "PU-21", "category": "LMG", "game": "BO6", "vertical_recoil": 28, "horizontal_recoil": 11, "fire_rate": 570, "damage": 42, "range_meters": 58, "recommended_build": "Compensator + Heavy Barrel + Ranger Foregrip + 100 Round Belt", "notes": "B Tier LMG"},
    ]
    
    for w in default_weapons:
        weapon = Weapon(**w)
        await db.weapons.insert_one(weapon.model_dump())
    
    return {"message": f"Seeded {len(default_weapons)} weapons", "seeded": True, "count": len(default_weapons)}

# ============== STATS ==============

@api_router.get("/weapons/{weapon_id}/optimized")
async def get_weapon_optimized(weapon_id: str):
    """Get optimized stats for a specific weapon"""
    weapon = await db.weapons.find_one({"id": weapon_id}, {"_id": 0})
    
    if not weapon:
        raise HTTPException(status_code=404, detail="Weapon not found")
    
    # Calculate optimized stats
    optimized = calculate_optimized_stats(
        base_damage=weapon.get("damage", 30),
        base_fire_rate=weapon.get("fire_rate", 700),
        base_recoil_v=weapon.get("vertical_recoil", 25),
        base_recoil_h=weapon.get("horizontal_recoil", 10),
        weapon_category=weapon.get("category", "AR")
    )
    
    # Format build string
    build_string = format_build_string(optimized["build"])
    
    return {
        "weapon": weapon,
        "base_stats": {
            "damage": weapon.get("damage", 30),
            "fire_rate": weapon.get("fire_rate", 700),
            "recoil_v": weapon.get("vertical_recoil", 25),
            "recoil_h": weapon.get("horizontal_recoil", 10),
            "ttk": optimized["base_ttk"]
        },
        "optimized_stats": {
            "damage": optimized["optimized_damage"],
            "fire_rate": optimized["optimized_fire_rate"],
            "recoil_v": optimized["optimized_recoil_v"],
            "recoil_h": optimized["optimized_recoil_h"],
            "ttk": optimized["optimized_ttk"]
        },
        "cronus_tuning": {
            "build_profile": optimized.get("build_name"),
            "stability_index": optimized.get("stability_index", 0),
            "script_vertical": optimized.get("script_vertical"),
            "script_horizontal": optimized.get("script_horizontal"),
            "script_burst_boost": optimized.get("script_burst_boost"),
        },
        "build": build_string,
        "improvement": {
            "ttk_saved_ms": optimized["ttk_improvement"],
            "ttk_improvement_percent": optimized["ttk_improvement_percent"]
        }
    }

@api_router.get("/stats")
async def get_stats():
    weapon_count = await db.weapons.count_documents({})
    script_count = await db.scripts.count_documents({})
    meta_count = await db.weapons.count_documents({"is_meta": True})
    hidden_meta_count = await db.weapons.count_documents({"is_hidden_meta": True})
    
    # Category breakdown
    categories = {}
    async for doc in db.weapons.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]):
        categories[doc["_id"]] = doc["count"]
    
    return {
        "total_weapons": weapon_count,
        "total_scripts": script_count,
        "meta_weapons": meta_count,
        "hidden_meta_weapons": hidden_meta_count,
        "categories": categories
    }

# ============== PRO ENDPOINTS 🔥 ==============

@api_router.get("/weapons/{weapon_id}/optimize-pro")
async def optimize_weapon_pro(weapon_id: str, profile_mode: str = "EQUILIBRE"):
    """
    Optimisation PRO avec 3 profils (AGRESSIF/EQUILIBRE/SNIPER)
    """
    weapon = await db.weapons.find_one({"id": weapon_id}, {"_id": 0})
    if not weapon:
        raise HTTPException(status_code=404, detail="Weapon not found")
    
    # Calculate all 3 profiles
    all_profiles = compare_all_profiles(
        base_damage=weapon.get("damage", 30),
        base_fire_rate=weapon.get("fire_rate", 700),
        base_recoil_v=weapon.get("vertical_recoil", 25),
        base_recoil_h=weapon.get("horizontal_recoil", 10),
        weapon_category=weapon.get("category", "AR")
    )
    
    # Get requested profile
    requested_profile = all_profiles.get(profile_mode, all_profiles.get("EQUILIBRE"))
    
    return {
        "weapon": weapon,
        "selected_profile": profile_mode,
        "selected_stats": requested_profile,
        "all_profiles_available": list(all_profiles.keys()),
        "comparison": {
            profile: {
                "ttk": stats.get("optimized_ttk"),
                "stability": stats.get("stability_index"),
                "score": stats.get("score"),
            } for profile, stats in all_profiles.items()
        }
    }

@api_router.post("/duo-calculator/best-pairs")
async def get_best_duo_pairs(profile_mode: str = "EQUILIBRE", limit: int = 5):
    """
    Pré-calcule les meilleures paires de duo
    """
    weapons = await db.weapons.find({}, {"_id": 0}).to_list(1000)
    
    if not weapons:
        raise HTTPException(status_code=400, detail="No weapons in database")
    
    # Load weapons into calculator
    duo_calculator.load_weapons(weapons)
    
    # Get best pairs
    best_pairs = duo_calculator.get_best_duo_pair(profile_mode, limit)
    
    return {
        "profile_mode": profile_mode,
        "best_pairs": [
            {
                "rank": idx + 1,
                "primary": pair["primary"].get("name"),
                "secondary": pair["secondary"].get("name"),
                "score": pair["score"],
                "compatibility": pair.get("compatibility"),
                "reason": duo_calculator._explain_pairing(pair["primary"], pair["secondary"]),
            }
            for idx, pair in enumerate(best_pairs)
        ]
    }

@api_router.get("/hair-trigger/{weapon_id}")
async def get_hair_trigger_profile(weapon_id: str):
    """
    Génère un profil Hair Trigger avancé pour une arme
    """
    weapon = await db.weapons.find_one({"id": weapon_id}, {"_id": 0})
    if not weapon:
        raise HTTPException(status_code=404, detail="Weapon not found")
    
    # Get Hair Trigger profile
    profile = hair_trigger_engine.get_profile_for_weapon(weapon)
    
    # Generate GPC code
    gpc_code = hair_trigger_engine.generate_gpc_code(profile)
    
    return {
        "weapon": weapon.get("name"),
        "weapon_class": profile.weapon_class.value,
        "profile": {
            "ramp_time_ms": profile.ramp_time_ms,
            "sensitivity_threshold": profile.sensitivity_threshold,
            "stabilizer_strength": profile.stabilizer_strength,
            "aa_sync": profile.aa_sync,
            "sustained_fire_boost": profile.sustained_fire_boost,
        },
        "gpc_code_preview": gpc_code.main_loop[:500] + "...",
    }

@api_router.get("/recoil-predictor/{weapon_id}")
async def predict_recoil(weapon_id: str, profile_mode: str = "EQUILIBRE"):
    """
    Prédiction adaptative du comportement du recul
    """
    weapon = await db.weapons.find_one({"id": weapon_id}, {"_id": 0})
    if not weapon:
        raise HTTPException(status_code=404, detail="Weapon not found")
    
    # Predict recoil behavior
    behavior = recoil_predictor.predict_recoil(weapon)
    
    # Calculate compensation strategies
    strategies = recoil_predictor.calculate_compensation_strategy(behavior, profile_mode)
    
    return {
        "weapon": weapon.get("name"),
        "recoil_behavior": {
            "vertical_initial": behavior.vertical_initial,
            "vertical_peak": behavior.vertical_peak,
            "vertical_drift": behavior.vertical_drift,
            "horizontal_pattern": behavior.horizontal_pattern,
            "controllability": behavior.controllability,
        },
        "compensation_strategies": {
            phase.name: {
                "vertical": strat.vertical_compensation,
                "horizontal": strat.horizontal_compensation,
                "burst_duration": strat.burst_duration,
            }
            for phase, strat in strategies.items()
        }
    }

@api_router.post("/build-analytics/record")
async def record_build_performance(
    primary_weapon: str,
    secondary_weapon: str,
    profile_mode: str,
    accuracy_score: float,
    ttk_effectiveness: float,
    controllability: float,
    recoil_management: float,
    successful_engagements: int,
    failed_engagements: int,
):
    """
    Enregistre une métrique de performance de build
    """
    metric = BuildPerformanceMetric(
        build_id=f"{primary_weapon}_{secondary_weapon}_{profile_mode}",
        weapon_primary=primary_weapon,
        weapon_secondary=secondary_weapon,
        profile_mode=profile_mode,
        accuracy_score=accuracy_score,
        ttk_effectiveness=ttk_effectiveness,
        controllability=controllability,
        recoil_management=recoil_management,
        successful_engagements=successful_engagements,
        failed_engagements=failed_engagements,
    )
    
    build_analytics.record_performance(metric)
    
    return {
        "status": "recorded",
        "build_id": metric.build_id,
        "overall_score": build_analytics.build_stats[f"{metric.weapon_primary}_{metric.weapon_secondary}_{metric.profile_mode}"]["overall_score"]
    }

@api_router.get("/build-analytics/top-builds")
async def get_top_builds_analytics(limit: int = 10):
    """
    Retourne les meilleures builds basées sur les analytics
    """
    recommendations = build_analytics.get_top_builds(limit)
    
    return {
        "top_builds": [
            {
                "rank": rec.rank,
                "build": rec.build_name,
                "primary": rec.primary_weapon,
                "secondary": rec.secondary_weapon,
                "profile": rec.profile_mode,
                "score": rec.overall_score,
                "success_rate": rec.success_rate,
                "recommended_for": rec.recommended_for,
            }
            for rec in recommendations
        ]
    }

@api_router.get("/build-analytics/report")
async def get_analytics_report():
    """
    Exporte un rapport complet d'analytics
    """
    report = build_analytics.export_analytics_report()
    return report

# ============== ROOT ==============

@api_router.get("/")
async def root():
    return {"message": "Zen Hub Pro API - Ready for battle", "version": "1.0.0"}

# ============== META UPDATE ENDPOINTS (CODMunity + WZStats) ==============

@api_router.post("/update-meta")
async def trigger_meta_update():
    """
    Déclenche manuellement la mise à jour de la méta
    depuis CODMunity (codmunity.gg/fr) et WZStats (wzstats.gg).
    Ajoute les nouvelles armes, met à jour pick rates et tiers.
    """
    try:
        report = await update_meta_in_db()
        return {
            "status":          "success",
            "message":         f"{report['weapons_updated']} armes mises à jour, {report['weapons_added']} ajoutées",
            "sources":         report["sources"],
            "weapons_updated": report["weapons_updated"],
            "weapons_added":   report["weapons_added"],
            "total_weapons":   report["total_weapons_db"],
            "meta_weapons":    report["meta_weapons_db"],
            "finished_at":     report["finished_at"],
        }
    except Exception as e:
        logger.error(f"Erreur update-meta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/meta-status")
async def get_meta_status():
    """
    Statut de la dernière synchronisation META.
    Retourne les infos du cache (date, sources, armes META détectées).
    """
    cache = load_cache()
    total = await db.weapons.count_documents({})
    meta_count = await db.weapons.count_documents({"is_meta": True})
    absolute_meta = await db.weapons.find(
        {"meta_tier": "ABSOLUTE_META"}, {"_id": 0, "name": 1, "pick_rate": 1, "ease_score": 1, "meta_rank": 1}
    ).sort("meta_rank", 1).to_list(10)
    warzone_meta = await db.weapons.find(
        {"meta_tier": "META"}, {"_id": 0, "name": 1, "pick_rate": 1, "ease_score": 1, "meta_rank": 1}
    ).sort("meta_rank", 1).to_list(20)

    return {
        "last_sync":      cache["last_update"] if cache else "Jamais",
        "sources":        cache["sources"] if cache else [],
        "total_weapons":  total,
        "meta_weapons":   meta_count,
        "absolute_meta":  absolute_meta,
        "warzone_meta":   warzone_meta,
        "next_sync":      "Toutes les 24h (auto) ou POST /api/update-meta",
    }

# Include the router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============== SCHEDULER META UPDATE ==============

async def _meta_update_loop():
    """Tâche de fond : met à jour la méta toutes les 24h."""
    while True:
        try:
            logger.info("⏰ Scheduler: démarrage de la mise à jour META...")
            await update_meta_in_db()
            logger.info("⏰ Scheduler: prochaine mise à jour dans 24h.")
        except Exception as e:
            logger.error(f"⏰ Scheduler erreur: {e}")
        await asyncio.sleep(24 * 3600)  # 24 heures


@app.on_event("startup")
async def startup_event():
    """Au démarrage: lance le scheduler META + première sync si besoin."""
    cache = load_cache()
    if cache is None:
        # Première exécution : sync immédiate
        logger.info("🚀 Premier démarrage → sync META immédiate...")
        asyncio.create_task(update_meta_in_db())
    else:
        from datetime import datetime as _dt
        try:
            last = _dt.fromisoformat(cache["last_update"])
            age_h = (_dt.now(timezone.utc) - last).total_seconds() / 3600
            if age_h > 24:
                logger.info(f"🔄 Cache vieux de {age_h:.1f}h → sync META...")
                asyncio.create_task(update_meta_in_db())
            else:
                logger.info(f"✅ Cache META frais ({age_h:.1f}h) — pas de re-sync.")
        except Exception:
            asyncio.create_task(update_meta_in_db())
    # Démarre la boucle quotidienne
    asyncio.create_task(_meta_update_loop())


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

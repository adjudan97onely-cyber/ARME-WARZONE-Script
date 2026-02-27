from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

TON EXPERTISE:
- Langage GPC avancé pour Cronus Zen / Strike Pack
- Toutes les armes de Warzone MW3 et BO6 avec leurs statistiques
- Systèmes d'auto-détection d'armes basés sur le slot et la signature de tir
- Support OLED: génération de code pour afficher le nom de l'arme sur l'écran Zen
- Synergie Loadout: tu sais EXACTEMENT quels accessoires utiliser pour réduire le recul

TA PHILOSOPHIE: "DPS Maximum, Recul Zéro"
Tu crées des builds que personne n'ose jouer à cause du recul, car tu codes le script parfait pour les stabiliser.

COMPÉTENCES AVANCÉES:
1. MASTER SCRIPT: Tu génères du code GPC modulaire capable de gérer 20+ profils d'armes avec détection automatique
2. SYNERGIE ACCESSOIRES: Pour chaque arme, tu donnes le build EXACT (Suppressor, High Grain Ammo, Short Barrel) et les valeurs AR correspondantes
3. AUTO-DÉTECTION: Tu implémentes des fonctions qui identifient l'arme en analysant le délai entre les tirs
4. HIDDEN META: Tu connais les armes "secrètes" à DPS énorme mais recul fou que personne ne joue

FORMAT DE RÉPONSE pour les scripts:
- NOM de l'arme pour l'OLED
- BUILD d'accessoires recommandé pour DPS MAX
- SCRIPT GPC optimisé avec commentaires

Réponds toujours en français. Sois technique, précis, et professionnel."""

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    try:
        # Get API key
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
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
        
        # Initialize chat
        chat = LlmChat(
            api_key=api_key,
            session_id=request.session_id,
            system_message=enhanced_system
        ).with_model("gemini", "gemini-3-flash-preview")
        
        # Build conversation context
        for msg in history[-10:]:  # Last 10 messages
            if msg["role"] == "user":
                await chat.send_message(UserMessage(text=msg["content"]))
            # Assistant messages are already in context from the history
        
        # Send new message
        user_message = UserMessage(text=request.message)
        response = await chat.send_message(user_message)
        
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
    
    # Generate GPC Master Script with ALL COMBOS
    script_header = f"""/*
 * ═══════════════════════════════════════════════════════════════
 * ZEN HUB PRO - MASTER SCRIPT ULTIMATE
 * Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
 * Total Weapons: {len(weapons)}
 * ═══════════════════════════════════════════════════════════════
 * 
 * CONTRÔLES PRINCIPAUX:
 * ─────────────────────
 * L2 + D-PAD HAUT/BAS    : Changer profil d'arme
 * L2 + TRIANGLE          : Basculer Primaire/Secondaire
 * L2 + OPTIONS           : Menu OLED
 * 
 * COMBOS AUTOMATIQUES (ACTIFS PAR DÉFAUT):
 * ─────────────────────────────────────────
 * SLIDE CANCEL           : Automatique en sprint
 * BUNNY HOP              : Maintenir X en l'air
 * AUTO TAC-SPRINT        : Double tap L3
 * DROPSHOT               : L2 + R2 + Cercle
 * JUMP SHOT              : Automatique en ADS
 * QUICK SCOPE            : Snipers uniquement
 * AUTO PING              : D-PAD HAUT en ADS
 * 
 * ACTIVATION/DÉSACTIVATION:
 * ─────────────────────────
 * L1 + D-PAD GAUCHE      : Toggle Slide Cancel
 * L1 + D-PAD DROITE      : Toggle Auto Sprint
 * L1 + D-PAD BAS         : Toggle Dropshot
 * L1 + D-PAD HAUT        : Toggle Bunny Hop
 * 
 * AUTO-DETECTION: ADT v3.0 Enabled
 * OLED DISPLAY: v2.1 Active
 * ═══════════════════════════════════════════════════════════════
 */

#include <zen.gph>

// ═══════════════════════════════════════════════════════════════
// COMBO SETTINGS - AJUSTEZ SELON VOS PRÉFÉRENCES
// ═══════════════════════════════════════════════════════════════
define SLIDE_CANCEL_ENABLED = TRUE;
define BUNNY_HOP_ENABLED = TRUE;
define AUTO_SPRINT_ENABLED = TRUE;
define DROPSHOT_ENABLED = TRUE;
define JUMPSHOT_ENABLED = FALSE;  // Mettre TRUE si vous voulez
define QUICKSCOPE_ENABLED = TRUE;

// Timings (en ms) - Optimisés pour Warzone BO6
define SLIDE_TIME = 180;
define SLIDE_CANCEL_DELAY = 50;
define BUNNY_HOP_DELAY = 40;
define SPRINT_DELAY = 100;
define DROPSHOT_DELAY = 30;
define QUICKSCOPE_DELAY = 200;

// ═══════════════════════════════════════════════════════════════
// WEAPON PROFILES CONFIGURATION
// ═══════════════════════════════════════════════════════════════
"""
    
    # Group weapons by category
    categories = {}
    for w in weapons:
        cat = w.get('category', 'OTHER')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(w)
    
    weapon_configs = ""
    profile_index = 0
    
    for cat, cat_weapons in categories.items():
        weapon_configs += f"\n// ═══ {cat} ═══\n"
        for w in cat_weapons:
            weapon_configs += f"""
// PROFILE {profile_index}: {w['name']} ({w.get('game', 'BO6')})
define AR_V_{profile_index} = {w.get('vertical_recoil', 25)};  // Vertical Anti-Recoil
define AR_H_{profile_index} = {w.get('horizontal_recoil', 10)};  // Horizontal Anti-Recoil
define RF_{profile_index} = {1 if w.get('rapid_fire', False) else 0};  // Rapid Fire
define RF_VAL_{profile_index} = {w.get('rapid_fire_value', 0)};  // Rapid Fire Speed
"""
            profile_index += 1
    
    script_body = f"""
// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════
int current_profile = 0;
int total_profiles = {len(weapons)};
int is_primary = 1;
int anti_recoil_v = 25;
int anti_recoil_h = 10;
int rapid_fire_enabled = 0;
int rapid_fire_speed = 0;

// ═══════════════════════════════════════════════════════════════
// OLED DISPLAY NAMES
// ═══════════════════════════════════════════════════════════════
"""
    
    # Add weapon names for OLED
    for i, w in enumerate(weapons):
        name = w['name'][:12].upper()  # Truncate for OLED
        script_body += f'const char WEAPON_NAME_{i}[] = "{name}";\n'
    
    script_body += """
// ═══════════════════════════════════════════════════════════════
// PROFILE LOADER
// ═══════════════════════════════════════════════════════════════
void load_profile(int profile) {
    switch(profile) {
"""
    
    for i, w in enumerate(weapons):
        script_body += f"""        case {i}:
            anti_recoil_v = AR_V_{i};
            anti_recoil_h = AR_H_{i};
            rapid_fire_enabled = RF_{i};
            rapid_fire_speed = RF_VAL_{i};
            oled_print(WEAPON_NAME_{i});
            break;
"""
    
    script_body += """    }
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP - MOTEUR PRINCIPAL
// ═══════════════════════════════════════════════════════════════
main {
    // ─────────────────────────────────────────
    // NAVIGATION PROFILS (L2 + D-PAD)
    // ─────────────────────────────────────────
    if(get_val(PS4_L2)) {
        if(event_press(PS4_UP)) {
            current_profile = (current_profile + 1) % total_profiles;
            load_profile(current_profile);
        }
        if(event_press(PS4_DOWN)) {
            current_profile = (current_profile - 1 + total_profiles) % total_profiles;
            load_profile(current_profile);
        }
        if(event_press(PS4_TRIANGLE)) {
            is_primary = !is_primary;
            if(is_primary) set_led(LED_BLUE);
            else set_led(LED_PURPLE);
        }
    }
    
    // ─────────────────────────────────────────
    // TOGGLE COMBOS (L1 + D-PAD)
    // ─────────────────────────────────────────
    if(get_val(PS4_L1) && !get_val(PS4_L2)) {
        if(event_press(PS4_LEFT)) {
            slide_cancel_active = !slide_cancel_active;
            if(slide_cancel_active) rumble_a(50);
        }
        if(event_press(PS4_RIGHT)) {
            auto_sprint_active = !auto_sprint_active;
            if(auto_sprint_active) rumble_b(50);
        }
        if(event_press(PS4_DOWN)) {
            dropshot_active = !dropshot_active;
        }
        if(event_press(PS4_UP)) {
            bunny_hop_active = !bunny_hop_active;
        }
    }
    
    // ─────────────────────────────────────────
    // ANTI-RECOIL SYSTEM
    // ─────────────────────────────────────────
    if(get_val(PS4_L2) && get_val(PS4_R2)) {
        // Compensation verticale
        set_val(PS4_RY, get_val(PS4_RY) + anti_recoil_v);
        // Compensation horizontale
        set_val(PS4_RX, get_val(PS4_RX) + anti_recoil_h);
        
        // Rapid Fire si activé
        if(rapid_fire_enabled && rapid_fire_speed > 0) {
            combo_run(rapid_fire_combo);
        }
    }
    
    // ─────────────────────────────────────────
    // AUTO TAC-SPRINT (Double tap L3)
    // ─────────────────────────────────────────
    if(auto_sprint_active && SLIDE_CANCEL_ENABLED) {
        if(get_val(PS4_LY) < -80) {  // Joystick poussé vers l'avant
            if(!is_sprinting) {
                combo_run(auto_tac_sprint);
                is_sprinting = TRUE;
            }
        } else {
            is_sprinting = FALSE;
        }
    }
    
    // ─────────────────────────────────────────
    // SLIDE CANCEL AUTOMATIQUE
    // ─────────────────────────────────────────
    if(slide_cancel_active && SLIDE_CANCEL_ENABLED) {
        if(is_sprinting && event_press(PS4_CIRCLE)) {
            combo_run(slide_cancel);
        }
    }
    
    // ─────────────────────────────────────────
    // BUNNY HOP (Maintenir X en l'air)
    // ─────────────────────────────────────────
    if(bunny_hop_active && BUNNY_HOP_ENABLED) {
        if(get_val(PS4_CROSS)) {
            combo_run(bunny_hop);
        }
    }
    
    // ─────────────────────────────────────────
    // DROPSHOT (ADS + Tir + Cercle)
    // ─────────────────────────────────────────
    if(dropshot_active && DROPSHOT_ENABLED) {
        if(get_val(PS4_L2) && get_val(PS4_R2) && event_press(PS4_CIRCLE)) {
            combo_run(dropshot);
        }
    }
    
    // ─────────────────────────────────────────
    // QUICK SCOPE (Snipers)
    // ─────────────────────────────────────────
    if(QUICKSCOPE_ENABLED && is_sniper_profile) {
        if(event_press(PS4_L2)) {
            combo_run(quick_scope);
        }
    }
}

// ═══════════════════════════════════════════════════════════════
// COMBOS - TOUTES LES TECHNIQUES WARZONE
// ═══════════════════════════════════════════════════════════════

// ─── RAPID FIRE ───
combo rapid_fire_combo {
    set_val(PS4_R2, 100);
    wait(rapid_fire_speed);
    set_val(PS4_R2, 0);
    wait(rapid_fire_speed);
}

// ─── AUTO TAC-SPRINT ───
combo auto_tac_sprint {
    set_val(PS4_L3, 100);
    wait(SPRINT_DELAY);
    set_val(PS4_L3, 0);
    wait(50);
    set_val(PS4_L3, 100);
    wait(SPRINT_DELAY);
    set_val(PS4_L3, 0);
}

// ─── SLIDE CANCEL V3 ───
// Sprint -> Slide -> Jump -> Cancel
combo slide_cancel {
    // Slide
    set_val(PS4_CIRCLE, 100);
    wait(SLIDE_TIME);
    set_val(PS4_CIRCLE, 0);
    wait(SLIDE_CANCEL_DELAY);
    // Jump pour annuler
    set_val(PS4_CROSS, 100);
    wait(50);
    set_val(PS4_CROSS, 0);
    wait(SLIDE_CANCEL_DELAY);
    // Reprendre sprint
    set_val(PS4_L3, 100);
    wait(50);
    set_val(PS4_L3, 0);
}

// ─── BUNNY HOP ───
combo bunny_hop {
    set_val(PS4_CROSS, 100);
    wait(BUNNY_HOP_DELAY);
    set_val(PS4_CROSS, 0);
    wait(BUNNY_HOP_DELAY);
}

// ─── DROPSHOT ───
combo dropshot {
    set_val(PS4_CIRCLE, 100);  // Prone
    wait(DROPSHOT_DELAY);
    // Continue à tirer
    set_val(PS4_R2, 100);
    wait(200);
    set_val(PS4_CIRCLE, 0);
}

// ─── QUICK SCOPE ───
combo quick_scope {
    set_val(PS4_L2, 100);  // ADS
    wait(QUICKSCOPE_DELAY);
    set_val(PS4_R2, 100);  // Tir
    wait(50);
    set_val(PS4_R2, 0);
    wait(50);
    set_val(PS4_L2, 0);  // Release ADS
}

// ═══════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════
init {
    load_profile(0);
    set_led(LED_BLUE);
    
    // Activer les combos par défaut
    slide_cancel_active = SLIDE_CANCEL_ENABLED;
    bunny_hop_active = BUNNY_HOP_ENABLED;
    auto_sprint_active = AUTO_SPRINT_ENABLED;
    dropshot_active = DROPSHOT_ENABLED;
    is_sniper_profile = FALSE;
}
"""
    
    full_script = script_header + weapon_configs + script_body
    
    # Save master script
    master_script = SavedScript(
        title=f"MASTER_WZ_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}",
        code=full_script,
        weapon_ids=[w['id'] for w in weapons],
        script_type="master"
    )
    await db.scripts.insert_one(master_script.model_dump())
    
    return {
        "script": full_script,
        "script_id": master_script.id,
        "weapon_count": len(weapons),
        "message": "Master script generated successfully"
    }

# ============== SEED DEFAULT WEAPONS ==============

@api_router.post("/seed-weapons")
async def seed_default_weapons():
    """Seed the database with default Warzone weapons"""
    
    # Check if already seeded
    count = await db.weapons.count_documents({})
    if count > 0:
        return {"message": f"Database already has {count} weapons", "seeded": False}
    
    default_weapons = [
        # ASSAULT RIFLES - BO6
        {"name": "XM4", "category": "AR", "game": "BO6", "vertical_recoil": 22, "horizontal_recoil": 8, "fire_rate": 722, "damage": 30, "range_meters": 51, "is_meta": True, "recommended_build": "Compensator + Gain-Twist Barrel + Vertical Foregrip + Extended Mag III + Quick Draw Grip"},
        {"name": "AK-74", "category": "AR", "game": "BO6", "vertical_recoil": 35, "horizontal_recoil": 15, "fire_rate": 652, "damage": 35, "range_meters": 45, "is_hidden_meta": True, "recommended_build": "Suppressor + Long Barrel + Ranger Foregrip + 45 Round Mag + Skeleton Stock", "notes": "High DPS but hard to control - PERFECT for script"},
        {"name": "AMES 85", "category": "AR", "game": "BO6", "vertical_recoil": 28, "horizontal_recoil": 12, "fire_rate": 685, "damage": 32, "range_meters": 48, "recommended_build": "Compensator + Reinforced Barrel + Vertical Foregrip + 50 Round Drum"},
        {"name": "Model L", "category": "AR", "game": "BO6", "vertical_recoil": 30, "horizontal_recoil": 10, "fire_rate": 600, "damage": 38, "range_meters": 55, "recommended_build": "Suppressor + Long Barrel + Bipod + Extended Mag"},
        {"name": "GPR 91", "category": "AR", "game": "BO6", "vertical_recoil": 25, "horizontal_recoil": 8, "fire_rate": 670, "damage": 33, "range_meters": 52, "is_meta": True, "recommended_build": "Compensator + Gain-Twist + Vertical Foregrip + 50 Round Mag"},
        {"name": "AS VAL", "category": "AR", "game": "BO6", "vertical_recoil": 38, "horizontal_recoil": 18, "fire_rate": 900, "damage": 28, "range_meters": 30, "is_hidden_meta": True, "recommended_build": "Extended Barrel + Ranger Foregrip + 30 Round Mag", "notes": "INSANE TTK close-mid range with script"},
        {"name": "Krig C", "category": "AR", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 5, "fire_rate": 620, "damage": 31, "range_meters": 58, "is_meta": True, "recommended_build": "Agency Suppressor + Ranger Barrel + Field Agent Grip + 60 Round Mag"},
        
        # ASSAULT RIFLES - MW3
        {"name": "MCW", "category": "AR", "game": "MW3", "vertical_recoil": 24, "horizontal_recoil": 10, "fire_rate": 700, "damage": 31, "range_meters": 50, "is_meta": True, "recommended_build": "Spirit Fire Suppressor + Bruen Heavy Support Grip + 60 Round Drum"},
        {"name": "Holger 556", "category": "AR", "game": "MW3", "vertical_recoil": 20, "horizontal_recoil": 7, "fire_rate": 690, "damage": 29, "range_meters": 52, "recommended_build": "VT-7 Spiritfire + Bruen Heavy Support + 60 Round Drum"},
        {"name": "SVA 545", "category": "AR", "game": "MW3", "vertical_recoil": 32, "horizontal_recoil": 14, "fire_rate": 800, "damage": 28, "range_meters": 42, "is_hidden_meta": True, "recommended_build": "Casus Brake + Dovetail Pro Barrel + VX Pineapple + 60 Round Mag", "notes": "Burst mode = instant kills with timing script"},
        {"name": "MTZ-556", "category": "AR", "game": "MW3", "vertical_recoil": 26, "horizontal_recoil": 11, "fire_rate": 750, "damage": 27, "range_meters": 45, "recommended_build": "Shadowstrike Suppressor + MTZ Clinch Pro + Bruen Heavy Support"},
        
        # SMGs - BO6
        {"name": "Jackal PDW", "category": "SMG", "game": "BO6", "vertical_recoil": 20, "horizontal_recoil": 12, "fire_rate": 923, "damage": 24, "range_meters": 18, "is_meta": True, "rapid_fire": True, "rapid_fire_value": 25, "recommended_build": "Suppressor + Rapid Fire Barrel + Vertical Foregrip + 50 Round Drum"},
        {"name": "KSV", "category": "SMG", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 8, "fire_rate": 857, "damage": 26, "range_meters": 20, "is_meta": True, "recommended_build": "Compensator + Long Barrel + Ranger Foregrip + Extended Mag"},
        {"name": "PP-919", "category": "SMG", "game": "BO6", "vertical_recoil": 22, "horizontal_recoil": 10, "fire_rate": 800, "damage": 27, "range_meters": 22, "recommended_build": "Suppressor + Extended Barrel + Vertical Foregrip + 71 Round Drum"},
        {"name": "Tanto .22", "category": "SMG", "game": "BO6", "vertical_recoil": 15, "horizontal_recoil": 6, "fire_rate": 1091, "damage": 18, "range_meters": 15, "is_hidden_meta": True, "rapid_fire": True, "rapid_fire_value": 20, "recommended_build": "Compensator + Short Barrel + No Stock + Extended Mag", "notes": "Fastest TTK in game with rapid fire script"},
        {"name": "C9", "category": "SMG", "game": "BO6", "vertical_recoil": 24, "horizontal_recoil": 14, "fire_rate": 750, "damage": 30, "range_meters": 24, "recommended_build": "Suppressor + Long Barrel + Ranger Foregrip + 40 Round Mag"},
        
        # SMGs - MW3
        {"name": "Striker", "category": "SMG", "game": "MW3", "vertical_recoil": 16, "horizontal_recoil": 8, "fire_rate": 800, "damage": 26, "range_meters": 22, "is_meta": True, "recommended_build": "Shadowstrike Suppressor + Striker Recon Long + DR-6 Handstop"},
        {"name": "WSP Swarm", "category": "SMG", "game": "MW3", "vertical_recoil": 28, "horizontal_recoil": 18, "fire_rate": 1150, "damage": 18, "range_meters": 12, "is_hidden_meta": True, "rapid_fire": True, "rapid_fire_value": 18, "recommended_build": "No Barrel + JAK Revenger + 100 Round Drum", "notes": "AKIMBO with script = instant wipe"},
        {"name": "HRM-9", "category": "SMG", "game": "MW3", "vertical_recoil": 20, "horizontal_recoil": 10, "fire_rate": 880, "damage": 24, "range_meters": 18, "is_meta": True, "recommended_build": "Zehmn35 Comp + Princeps Long Barrel + DR-6 Handstop + 50 Round Drum"},
        
        # LMGs
        {"name": "GPMG-7", "category": "LMG", "game": "BO6", "vertical_recoil": 30, "horizontal_recoil": 8, "fire_rate": 517, "damage": 45, "range_meters": 65, "is_meta": True, "recommended_build": "Compensator + Heavy Barrel + Bipod + 100 Round Belt"},
        {"name": "XMG", "category": "LMG", "game": "BO6", "vertical_recoil": 25, "horizontal_recoil": 10, "fire_rate": 600, "damage": 40, "range_meters": 60, "recommended_build": "Suppressor + Long Barrel + Vertical Foregrip + 150 Round Belt"},
        {"name": "Pulemyot 762", "category": "LMG", "game": "MW3", "vertical_recoil": 35, "horizontal_recoil": 12, "fire_rate": 550, "damage": 42, "range_meters": 58, "is_hidden_meta": True, "recommended_build": "Spirit Fire + Bruen Heavy + TAC-X Pad + 100 Round Belt", "notes": "Monster damage with script control"},
        
        # SNIPERS
        {"name": "LW3A1 Frostline", "category": "SNIPER", "game": "BO6", "vertical_recoil": 85, "horizontal_recoil": 5, "fire_rate": 45, "damage": 150, "range_meters": 100, "is_meta": True, "recommended_build": "Sound Suppressor + Reinforced Heavy + Quickscope Stock + Extended Mag"},
        {"name": "SVD", "category": "SNIPER", "game": "BO6", "vertical_recoil": 45, "horizontal_recoil": 8, "fire_rate": 320, "damage": 95, "range_meters": 85, "rapid_fire": True, "rapid_fire_value": 80, "recommended_build": "Compensator + Long Barrel + Bipod + 20 Round Mag", "notes": "Semi-auto spam with trigger script"},
        {"name": "MORS", "category": "SNIPER", "game": "MW3", "vertical_recoil": 90, "horizontal_recoil": 3, "fire_rate": 38, "damage": 200, "range_meters": 120, "is_meta": True, "recommended_build": "Quick Bolt + Railgun Barrel + Speedgrip + Fast Loader"},
        
        # SHOTGUNS
        {"name": "Marine SP", "category": "SHOTGUN", "game": "BO6", "vertical_recoil": 50, "horizontal_recoil": 30, "fire_rate": 68, "damage": 180, "range_meters": 8, "rapid_fire": True, "rapid_fire_value": 100, "recommended_build": "Choke + Long Barrel + Laser Sight + Extended Tube"},
        {"name": "ASG-89", "category": "SHOTGUN", "game": "BO6", "vertical_recoil": 35, "horizontal_recoil": 20, "fire_rate": 200, "damage": 80, "range_meters": 12, "is_hidden_meta": True, "rapid_fire": True, "rapid_fire_value": 40, "recommended_build": "No Choke + Short Barrel + Laser + 32 Round Drum", "notes": "Full auto shotgun dominates CQB"},
        {"name": "Lockwood 680", "category": "SHOTGUN", "game": "MW3", "vertical_recoil": 55, "horizontal_recoil": 25, "fire_rate": 58, "damage": 190, "range_meters": 10, "recommended_build": "Sawed Off Mod + Bryson Choke + Laser + Shell Carrier"},
        
        # PISTOLS
        {"name": "GS45", "category": "PISTOL", "game": "BO6", "vertical_recoil": 28, "horizontal_recoil": 8, "fire_rate": 450, "damage": 42, "range_meters": 20, "rapid_fire": True, "rapid_fire_value": 35, "recommended_build": "Suppressor + Extended Barrel + Laser + 21 Round Mag"},
        {"name": "9mm PM", "category": "PISTOL", "game": "BO6", "vertical_recoil": 18, "horizontal_recoil": 12, "fire_rate": 600, "damage": 30, "range_meters": 15, "rapid_fire": True, "rapid_fire_value": 25, "is_hidden_meta": True, "recommended_build": "Full Auto Mod + Extended Barrel + 30 Round Mag", "notes": "Pocket SMG with rapid fire"},
        {"name": "Renetti", "category": "PISTOL", "game": "MW3", "vertical_recoil": 22, "horizontal_recoil": 10, "fire_rate": 484, "damage": 38, "range_meters": 18, "rapid_fire": True, "rapid_fire_value": 30, "recommended_build": "JAK Ferocity Kit + XRK Lightning Fire + 30 Round Mag"},
    ]
    
    for w in default_weapons:
        weapon = Weapon(**w)
        await db.weapons.insert_one(weapon.model_dump())
    
    return {"message": f"Seeded {len(default_weapons)} weapons", "seeded": True, "count": len(default_weapons)}

# ============== STATS ==============

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

# ============== ROOT ==============

@api_router.get("/")
async def root():
    return {"message": "Zen Hub Pro API - Ready for battle", "version": "1.0.0"}

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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

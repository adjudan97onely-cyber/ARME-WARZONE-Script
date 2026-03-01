#!/usr/bin/env python3
"""
Script d'import massif des armes depuis wzstats.gg
Ajoute toutes les armes META de Warzone dans la base de données
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Mapping des catégories françaises vers anglais
CATEGORY_MAP = {
    "Fusil d'Assaut": "AR",
    "Mitraillette": "SMG",
    "Mitrailleuse": "LMG",
    "Fusil de précision": "SNIPER",
    "Marksman": "MARKSMAN",
    "Fusil à Pompe": "SHOTGUN",
    "Pistolet": "PISTOL",
    "BR": "BR",
    "Spécial": "SPECIAL"
}

# Toutes les armes extraites de wzstats.gg
WZSTATS_WEAPONS = [
    # ═══════════════════════════════════════════════════════════════
    # S TIER - META TOP 10
    # ═══════════════════════════════════════════════════════════════
    {"name": "M8A1", "category": "MARKSMAN", "game": "BO6", "tier": "S", "rank": 1, "vertical_recoil": 20, "horizontal_recoil": 6, "fire_rate": 545, "is_meta": True},
    {"name": "Carbon 57", "category": "SMG", "game": "BO6", "tier": "S", "rank": 2, "vertical_recoil": 18, "horizontal_recoil": 10, "fire_rate": 900, "is_meta": True},
    {"name": "M15 MOD 0", "category": "AR", "game": "BO6", "tier": "S", "rank": 3, "vertical_recoil": 22, "horizontal_recoil": 8, "fire_rate": 680, "is_meta": True},
    {"name": "REV-46", "category": "SMG", "game": "BO6", "tier": "S", "rank": 4, "vertical_recoil": 20, "horizontal_recoil": 12, "fire_rate": 857, "is_meta": True},
    {"name": "Maddox RFB", "category": "AR", "game": "BO6", "tier": "S", "rank": 5, "vertical_recoil": 24, "horizontal_recoil": 10, "fire_rate": 722, "is_meta": True},
    {"name": "Kogot-7", "category": "SMG", "game": "BO6", "tier": "S", "rank": 6, "vertical_recoil": 16, "horizontal_recoil": 8, "fire_rate": 923, "is_meta": True},
    {"name": "EGRT-17", "category": "AR", "game": "BO6", "tier": "S", "rank": 7, "vertical_recoil": 26, "horizontal_recoil": 9, "fire_rate": 650, "is_meta": True},
    {"name": "Razor 9mm", "category": "SMG", "game": "BO6", "tier": "S", "rank": 8, "vertical_recoil": 19, "horizontal_recoil": 11, "fire_rate": 880, "is_meta": True},
    {"name": "AK-27", "category": "AR", "game": "BO6", "tier": "S", "rank": 9, "vertical_recoil": 30, "horizontal_recoil": 14, "fire_rate": 600, "is_meta": True, "is_hidden_meta": True},
    {"name": "Hawker HX", "category": "SNIPER", "game": "BO6", "tier": "S", "rank": 10, "vertical_recoil": 90, "horizontal_recoil": 4, "fire_rate": 42, "is_meta": True},
    
    # ═══════════════════════════════════════════════════════════════
    # A TIER
    # ═══════════════════════════════════════════════════════════════
    {"name": "X9 Maverick", "category": "AR", "game": "BO6", "tier": "A", "vertical_recoil": 23, "horizontal_recoil": 8, "fire_rate": 700},
    {"name": "Ryden 45K", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 17, "horizontal_recoil": 9, "fire_rate": 870},
    {"name": "MK.78", "category": "LMG", "game": "BO6", "tier": "A", "vertical_recoil": 28, "horizontal_recoil": 12, "fire_rate": 650},
    {"name": "Dravec 45", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 18, "horizontal_recoil": 10, "fire_rate": 850},
    {"name": "VS Recon", "category": "SNIPER", "game": "BO6", "tier": "A", "vertical_recoil": 85, "horizontal_recoil": 5, "fire_rate": 45},
    {"name": "Peacekeeper Mk1", "category": "AR", "game": "BO6", "tier": "A", "vertical_recoil": 24, "horizontal_recoil": 9, "fire_rate": 690},
    {"name": "DS20 Mirage", "category": "AR", "game": "BO6", "tier": "A", "vertical_recoil": 25, "horizontal_recoil": 10, "fire_rate": 670},
    {"name": "Sturmwolf 45", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 19, "horizontal_recoil": 11, "fire_rate": 840},
    {"name": "MPC-25", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 17, "horizontal_recoil": 10, "fire_rate": 860},
    {"name": "MXR-17", "category": "AR", "game": "BO6", "tier": "A", "vertical_recoil": 26, "horizontal_recoil": 11, "fire_rate": 660},
    {"name": "HDR", "category": "SNIPER", "game": "MW", "tier": "A", "vertical_recoil": 92, "horizontal_recoil": 6, "fire_rate": 40},
    {"name": "XM325", "category": "LMG", "game": "BO6", "tier": "A", "vertical_recoil": 30, "horizontal_recoil": 13, "fire_rate": 640},
    {"name": "Sokol 545", "category": "LMG", "game": "BO6", "tier": "A", "vertical_recoil": 29, "horizontal_recoil": 12, "fire_rate": 650},
    {"name": "XR-3 Ion", "category": "SNIPER", "game": "BO6", "tier": "A", "vertical_recoil": 88, "horizontal_recoil": 5, "fire_rate": 43},
    {"name": "Kilo 141", "category": "AR", "game": "MW", "tier": "A", "vertical_recoil": 22, "horizontal_recoil": 7, "fire_rate": 750},
    {"name": "Merrick 556", "category": "AR", "game": "BO6", "tier": "A", "vertical_recoil": 23, "horizontal_recoil": 8, "fire_rate": 710},
    {"name": "Akita", "category": "SHOTGUN", "game": "BO6", "tier": "A", "vertical_recoil": 40, "horizontal_recoil": 15, "fire_rate": 120},
    {"name": "Shadow SK", "category": "SNIPER", "game": "BO6", "tier": "A", "vertical_recoil": 86, "horizontal_recoil": 6, "fire_rate": 44},
    {"name": "M10 Breacher", "category": "SHOTGUN", "game": "BO6", "tier": "A", "vertical_recoil": 38, "horizontal_recoil": 14, "fire_rate": 130},
    {"name": "M34 Novaline", "category": "MARKSMAN", "game": "BO6", "tier": "A", "vertical_recoil": 21, "horizontal_recoil": 7, "fire_rate": 500},
    {"name": "Warden 308", "category": "MARKSMAN", "game": "BO6", "tier": "A", "vertical_recoil": 22, "horizontal_recoil": 8, "fire_rate": 480},
    {"name": "Velox 5.7", "category": "PISTOL", "game": "BO6", "tier": "A", "vertical_recoil": 12, "horizontal_recoil": 6, "fire_rate": 500},
    {"name": "RK-9", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 18, "horizontal_recoil": 11, "fire_rate": 830},
    {"name": "SG-12", "category": "SHOTGUN", "game": "BO6", "tier": "A", "vertical_recoil": 42, "horizontal_recoil": 16, "fire_rate": 110},
    {"name": "Echo 12", "category": "SHOTGUN", "game": "BO6", "tier": "A", "vertical_recoil": 39, "horizontal_recoil": 15, "fire_rate": 125},
    {"name": "CODA 9", "category": "PISTOL", "game": "BO6", "tier": "A", "vertical_recoil": 13, "horizontal_recoil": 7, "fire_rate": 480},
    {"name": "Jäger 45", "category": "PISTOL", "game": "BO6", "tier": "A", "vertical_recoil": 14, "horizontal_recoil": 8, "fire_rate": 460},
    {"name": "TR2", "category": "MARKSMAN", "game": "BO6", "tier": "A", "vertical_recoil": 20, "horizontal_recoil": 6, "fire_rate": 520},
    {"name": "C9", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 16, "horizontal_recoil": 9, "fire_rate": 890},
    {"name": "Dresden 9mm", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 17, "horizontal_recoil": 10, "fire_rate": 870},
    {"name": "SWAT 5.56", "category": "MARKSMAN", "game": "BO6", "tier": "A", "vertical_recoil": 23, "horizontal_recoil": 9, "fire_rate": 490},
    {"name": "GPR 91", "category": "AR", "game": "BO6", "tier": "A", "vertical_recoil": 27, "horizontal_recoil": 11, "fire_rate": 650},
    {"name": "JACKAL PDW", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 19, "horizontal_recoil": 12, "fire_rate": 820},
    {"name": "X52 Resonator", "category": "SPECIAL", "game": "BO6", "tier": "A", "vertical_recoil": 15, "horizontal_recoil": 5, "fire_rate": 600},
    {"name": "CR-56 AMAX", "category": "AR", "game": "MW", "tier": "A", "vertical_recoil": 26, "horizontal_recoil": 10, "fire_rate": 640},
    {"name": "LADRA", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 18, "horizontal_recoil": 11, "fire_rate": 850},
    {"name": "AMES 85", "category": "AR", "game": "BO6", "tier": "A", "vertical_recoil": 25, "horizontal_recoil": 10, "fire_rate": 680},
    {"name": "PPSh-41", "category": "SMG", "game": "CW", "tier": "A", "vertical_recoil": 20, "horizontal_recoil": 13, "fire_rate": 780},
    {"name": "KSV", "category": "SMG", "game": "BO6", "tier": "A", "vertical_recoil": 17, "horizontal_recoil": 10, "fire_rate": 860},
    {"name": "GREKHOVA", "category": "PISTOL", "game": "BO6", "tier": "A", "vertical_recoil": 15, "horizontal_recoil": 8, "fire_rate": 440},
    {"name": "KATT-AMR", "category": "SNIPER", "game": "MW3", "tier": "A", "vertical_recoil": 94, "horizontal_recoil": 7, "fire_rate": 38},
    {"name": "Victus XMR", "category": "SNIPER", "game": "MW2", "tier": "A", "vertical_recoil": 96, "horizontal_recoil": 8, "fire_rate": 36},
    {"name": "FJX Imperium", "category": "SNIPER", "game": "MW2", "tier": "A", "vertical_recoil": 95, "horizontal_recoil": 7, "fire_rate": 37},
    {"name": "LR 7.62", "category": "SNIPER", "game": "BO6", "tier": "A", "vertical_recoil": 87, "horizontal_recoil": 6, "fire_rate": 42},
    {"name": "Kar98k", "category": "MARKSMAN", "game": "MW", "tier": "A", "vertical_recoil": 24, "horizontal_recoil": 5, "fire_rate": 450},
    
    # ═══════════════════════════════════════════════════════════════
    # B TIER (Ajout sélectif des armes les plus populaires)
    # ═══════════════════════════════════════════════════════════════
    {"name": "SAUG", "category": "SMG", "game": "BO4", "tier": "B", "vertical_recoil": 19, "horizontal_recoil": 12, "fire_rate": 810},
    {"name": "ABR A1", "category": "AR", "game": "BO6", "tier": "B", "vertical_recoil": 28, "horizontal_recoil": 12, "fire_rate": 630},
    {"name": "LC10", "category": "SMG", "game": "CW", "tier": "B", "vertical_recoil": 18, "horizontal_recoil": 11, "fire_rate": 840},
    {"name": "KOMPAKT 92", "category": "SMG", "game": "BO6", "tier": "B", "vertical_recoil": 20, "horizontal_recoil": 13, "fire_rate": 800},
    {"name": "Cypher 091", "category": "AR", "game": "BO6", "tier": "B", "vertical_recoil": 27, "horizontal_recoil": 11, "fire_rate": 660},
    {"name": "XM4", "category": "AR", "game": "CW", "tier": "B", "vertical_recoil": 24, "horizontal_recoil": 9, "fire_rate": 720},
    {"name": "AS VAL", "category": "AR", "game": "MW", "tier": "B", "vertical_recoil": 22, "horizontal_recoil": 10, "fire_rate": 900},
    {"name": "FFAR 1", "category": "AR", "game": "CW", "tier": "B", "vertical_recoil": 26, "horizontal_recoil": 12, "fire_rate": 800},
    {"name": "MODEL L", "category": "AR", "game": "BO6", "tier": "B", "vertical_recoil": 25, "horizontal_recoil": 10, "fire_rate": 690},
    {"name": "KRIG C", "category": "AR", "game": "BO6", "tier": "B", "vertical_recoil": 23, "horizontal_recoil": 8, "fire_rate": 710},
    {"name": "M13B", "category": "AR", "game": "MW2", "tier": "B", "vertical_recoil": 21, "horizontal_recoil": 7, "fire_rate": 780},
    {"name": "M4", "category": "AR", "game": "MW", "tier": "B", "vertical_recoil": 22, "horizontal_recoil": 8, "fire_rate": 750},
    {"name": "Striker", "category": "SMG", "game": "MW3", "tier": "B", "vertical_recoil": 19, "horizontal_recoil": 11, "fire_rate": 830},
    {"name": "MX9", "category": "SMG", "game": "VG", "tier": "B", "vertical_recoil": 18, "horizontal_recoil": 12, "fire_rate": 850},
    {"name": "BAS-P", "category": "SMG", "game": "MW2", "tier": "B", "vertical_recoil": 17, "horizontal_recoil": 10, "fire_rate": 870},
    {"name": "Vaznev-9k", "category": "SMG", "game": "MW2", "tier": "B", "vertical_recoil": 19, "horizontal_recoil": 11, "fire_rate": 820},
    {"name": "VEL 46", "category": "SMG", "game": "MW2", "tier": "B", "vertical_recoil": 18, "horizontal_recoil": 10, "fire_rate": 860},
    {"name": "Marine SP", "category": "SHOTGUN", "game": "BO6", "tier": "B", "vertical_recoil": 41, "horizontal_recoil": 16, "fire_rate": 115},
    {"name": "Sakin MG38", "category": "LMG", "game": "MW2", "tier": "B", "vertical_recoil": 31, "horizontal_recoil": 14, "fire_rate": 620},
    {"name": "MCW", "category": "AR", "game": "MW3", "tier": "B", "vertical_recoil": 23, "horizontal_recoil": 9, "fire_rate": 700},
    {"name": "XMG", "category": "LMG", "game": "BO6", "tier": "B", "vertical_recoil": 32, "horizontal_recoil": 15, "fire_rate": 610},
    {"name": "STG44", "category": "AR", "game": "VG", "tier": "B", "vertical_recoil": 24, "horizontal_recoil": 10, "fire_rate": 680},
    {"name": "HRM-9", "category": "SMG", "game": "MW3", "tier": "B", "vertical_recoil": 18, "horizontal_recoil": 11, "fire_rate": 840},
    {"name": "AK-74", "category": "AR", "game": "BO6", "tier": "B", "vertical_recoil": 28, "horizontal_recoil": 13, "fire_rate": 610},
    {"name": "PDSW 528", "category": "SMG", "game": "MW2", "tier": "B", "vertical_recoil": 17, "horizontal_recoil": 10, "fire_rate": 880},
    {"name": "TAQ-56", "category": "AR", "game": "MW2", "tier": "B", "vertical_recoil": 25, "horizontal_recoil": 10, "fire_rate": 670},
    {"name": "LW3A1 FROSTLINE", "category": "SNIPER", "game": "CW", "tier": "B", "vertical_recoil": 89, "horizontal_recoil": 6, "fire_rate": 41},
    {"name": "Reclaimer 18", "category": "SHOTGUN", "game": "BO6", "tier": "B", "vertical_recoil": 40, "horizontal_recoil": 15, "fire_rate": 120},
    {"name": "Feng 82", "category": "LMG", "game": "BO6", "tier": "B", "vertical_recoil": 30, "horizontal_recoil": 13, "fire_rate": 630},
    {"name": "GOBLIN MK2", "category": "AR", "game": "BO6", "tier": "B", "vertical_recoil": 26, "horizontal_recoil": 11, "fire_rate": 650},
]

async def import_weapons():
    """Import toutes les armes dans la base de données"""
    
    print("🔫 Import des armes de wzstats.gg en cours...")
    print(f"Total d'armes à importer : {len(WZSTATS_WEAPONS)}")
    print()
    
    # Vérifier les armes existantes
    existing_weapons = await db.weapons.find({}, {"name": 1, "_id": 0}).to_list(1000)
    existing_names = {w['name'] for w in existing_weapons}
    
    print(f"✅ Armes déjà présentes : {len(existing_names)}")
    print()
    
    added_count = 0
    skipped_count = 0
    
    for weapon_data in WZSTATS_WEAPONS:
        if weapon_data['name'] in existing_names:
            print(f"⏭️  {weapon_data['name']} - Déjà présente")
            skipped_count += 1
            continue
        
        # Créer le document weapon
        weapon = {
            "id": str(uuid.uuid4()),
            "name": weapon_data['name'],
            "category": weapon_data['category'],
            "game": weapon_data['game'],
            "vertical_recoil": weapon_data.get('vertical_recoil', 25),
            "horizontal_recoil": weapon_data.get('horizontal_recoil', 10),
            "fire_rate": weapon_data.get('fire_rate', 700),
            "damage": 30,
            "range_meters": 40,
            "rapid_fire": False,
            "rapid_fire_value": 0,
            "recommended_build": None,
            "notes": f"{weapon_data.get('tier', 'B')} Tier - Rank #{weapon_data.get('rank', 0)}" if weapon_data.get('rank') else f"{weapon_data.get('tier', 'B')} Tier",
            "is_meta": weapon_data.get('is_meta', False),
            "is_hidden_meta": weapon_data.get('is_hidden_meta', False)
        }
        
        await db.weapons.insert_one(weapon)
        print(f"✅ {weapon['name']} - Ajoutée ({weapon['category']}, {weapon['game']}, {weapon.get('notes', '')})")
        added_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ Import terminé !")
    print(f"   Armes ajoutées : {added_count}")
    print(f"   Armes ignorées (déjà présentes) : {skipped_count}")
    print(f"   Total dans la base : {len(existing_names) + added_count}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(import_weapons())

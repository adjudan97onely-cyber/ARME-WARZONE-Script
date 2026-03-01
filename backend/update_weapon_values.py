#!/usr/bin/env python3
"""
Script pour mettre à jour les valeurs de recul d'AS VAL et WSP SWARM
selon les recommandations de l'IA Experte
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def update_weapon_values():
    """Met à jour AS VAL et WSP SWARM avec les valeurs optimisées"""
    
    print("🔧 Mise à jour des valeurs de recul...")
    print("=" * 60)
    
    # Mettre à jour AS VAL
    result_asval = await db.weapons.update_one(
        {"name": "AS VAL"},
        {"$set": {
            "vertical_recoil": 28,
            "horizontal_recoil": 18,
            "notes": "Valeurs optimisées par IA Experte - V:28 H:18"
        }}
    )
    
    if result_asval.modified_count > 0:
        print("✅ AS VAL mise à jour : V=28, H=18")
    else:
        print("⚠️  AS VAL non trouvée ou déjà à jour")
    
    # Mettre à jour WSP SWARM
    result_wsp = await db.weapons.update_one(
        {"name": {"$regex": "WSP.*SWARM", "$options": "i"}},
        {"$set": {
            "vertical_recoil": 22,
            "horizontal_recoil": 20,
            "notes": "Valeurs optimisées par IA Experte - V:22 H:20"
        }}
    )
    
    if result_wsp.modified_count > 0:
        print("✅ WSP SWARM mise à jour : V=22, H=20")
    else:
        print("⚠️  WSP SWARM non trouvée ou déjà à jour")
    
    print("=" * 60)
    print("✅ Mise à jour terminée !")
    
    # Vérifier les valeurs
    asval = await db.weapons.find_one({"name": "AS VAL"}, {"_id": 0})
    if asval:
        print(f"\nAS VAL : V={asval['vertical_recoil']}, H={asval['horizontal_recoil']}")
    
    wsp = await db.weapons.find_one({"name": {"$regex": "WSP.*SWARM", "$options": "i"}}, {"_id": 0})
    if wsp:
        print(f"WSP SWARM : V={wsp['vertical_recoil']}, H={wsp['horizontal_recoil']}")

if __name__ == "__main__":
    asyncio.run(update_weapon_values())

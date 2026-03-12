#!/usr/bin/env python3
"""
Ajout des 2 nouvelles armes à venir (valeurs à 0)
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def add_future_weapons():
    """Ajoute les 2 nouvelles armes avec valeurs à 0"""
    
    print("🆕 AJOUT DES NOUVELLES ARMES À VENIR")
    print("=" * 60)
    
    # 1. Voyak KT-3 (AR)
    await db.weapons.update_one(
        {"name": "Voyak KT-3"},
        {"$set": {
            "category": "AR",
            "game": "BO7",
            "vertical_recoil": 0,
            "horizontal_recoil": 0,
            "fire_rate": 700,
            "is_meta": False,
            "notes": "NOUVELLE ARME Season 2 Reloaded - Pas encore sortie - Valeurs à définir"
        }},
        upsert=True
    )
    print("✅ Voyak KT-3 (AR) - Ajoutée (valeurs à 0)")
    
    # 2. Swordfish A1 (Marksman)
    await db.weapons.update_one(
        {"name": "Swordfish A1"},
        {"$set": {
            "category": "MARKSMAN",
            "game": "BO7",
            "vertical_recoil": 0,
            "horizontal_recoil": 0,
            "fire_rate": 450,
            "is_meta": False,
            "notes": "NOUVELLE ARME Season 2 Reloaded - Pas encore sortie - Valeurs à définir"
        }},
        upsert=True
    )
    print("✅ Swordfish A1 (Marksman) - Ajoutée (valeurs à 0)")
    
    print("=" * 60)
    print("✅ Nouvelles armes ajoutées !")
    print()
    print("📝 Note : Valeurs à 0 car armes pas encore sorties")
    print("   L'utilisateur pourra les configurer après la sortie")

if __name__ == "__main__":
    asyncio.run(add_future_weapons())

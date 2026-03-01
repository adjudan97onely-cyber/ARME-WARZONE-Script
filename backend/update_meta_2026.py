#!/usr/bin/env python3
"""
Script pour mettre à jour M8A1 et Carbon 57 avec les valeurs META mars 2026
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

async def update_meta_2026():
    """Met à jour M8A1 et Carbon 57 avec les valeurs META mars 2026"""
    
    print("🔧 Mise à jour META MARS 2026...")
    print("=" * 60)
    
    # Mettre à jour M8A1
    result_m8a1 = await db.weapons.update_one(
        {"name": "M8A1"},
        {"$set": {
            "vertical_recoil": 20,
            "horizontal_recoil": 6,
            "is_meta": True,
            "notes": "#1 META LONGUE PORTÉE - Mars 2026 - V:20 H:6 - TTK 610ms"
        }}
    )
    
    if result_m8a1.modified_count > 0:
        print("✅ M8A1 mise à jour : V=20, H=6 (#1 META Longue Portée)")
    else:
        print("⚠️  M8A1 non trouvée ou déjà à jour")
    
    # Mettre à jour Carbon 57
    result_carbon = await db.weapons.update_one(
        {"name": "Carbon 57"},
        {"$set": {
            "vertical_recoil": 18,
            "horizontal_recoil": 10,
            "is_meta": True,
            "notes": "#1 META COURTE PORTÉE - Mars 2026 - V:18 H:10 - TTK 495ms"
        }}
    )
    
    if result_carbon.modified_count > 0:
        print("✅ Carbon 57 mise à jour : V=18, H=10 (#1 META Courte Portée)")
    else:
        print("⚠️  Carbon 57 non trouvée ou déjà à jour")
    
    # Retirer le flag META d'AS VAL et WSP SWARM
    await db.weapons.update_one(
        {"name": "AS VAL"},
        {"$set": {
            "is_meta": False,
            "notes": "B Tier - Obsolète mars 2026 - 0.15% pick rate"
        }}
    )
    print("⚠️  AS VAL : META retiré (B Tier)")
    
    await db.weapons.update_one(
        {"name": {"$regex": "WSP.*SWARM", "$options": "i"}},
        {"$set": {
            "is_meta": False,
            "notes": "C Tier - Obsolète mars 2026 - 0.10% pick rate"
        }}
    )
    print("⚠️  WSP SWARM : META retiré (C Tier)")
    
    print("=" * 60)
    print("✅ Mise à jour terminée !")
    
    # Vérifier les valeurs
    m8a1 = await db.weapons.find_one({"name": "M8A1"}, {"_id": 0})
    if m8a1:
        print(f"\n✅ M8A1 : V={m8a1['vertical_recoil']}, H={m8a1['horizontal_recoil']} (META: {m8a1.get('is_meta')})")
    
    carbon = await db.weapons.find_one({"name": "Carbon 57"}, {"_id": 0})
    if carbon:
        print(f"✅ Carbon 57 : V={carbon['vertical_recoil']}, H={carbon['horizontal_recoil']} (META: {carbon.get('is_meta')})")
    
    asval = await db.weapons.find_one({"name": "AS VAL"}, {"_id": 0})
    if asval:
        print(f"\n⚠️  AS VAL : V={asval['vertical_recoil']}, H={asval['horizontal_recoil']} (META: {asval.get('is_meta')})")

if __name__ == "__main__":
    asyncio.run(update_meta_2026())

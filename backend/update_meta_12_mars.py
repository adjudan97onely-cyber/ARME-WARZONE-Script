#!/usr/bin/env python3
"""
Mise à jour META 12 mars 2026
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

async def update_meta_12_mars():
    """Mise à jour META 12 mars 2026"""
    
    print("🔧 MISE À JOUR META 12 MARS 2026")
    print("=" * 60)
    
    # 1. Peacekeeper Mk1 - NOUVEAU #1 META
    result = await db.weapons.update_one(
        {"name": "Peacekeeper Mk1"},
        {"$set": {
            "vertical_recoil": 22,
            "horizontal_recoil": 8,
            "is_meta": True,
            "fire_rate": 700,
            "notes": "#1 META 12 mars 2026 - BUFFÉ - 6.19% pick - V:22 H:8"
        }},
        upsert=True
    )
    print("✅ Peacekeeper Mk1 : #1 META (6.19% pick)")
    
    # 2. Kogot-7 - #1 COURTE PORTÉE
    await db.weapons.update_one(
        {"name": "Kogot-7"},
        {"$set": {
            "vertical_recoil": 16,
            "horizontal_recoil": 8,
            "is_meta": True,
            "fire_rate": 923,
            "notes": "#1 COURTE PORTÉE 12 mars 2026 - BUFFÉ - 5.82% pick - V:16 H:8"
        }}
    )
    print("✅ Kogot-7 : #1 Courte Portée (5.82% pick)")
    
    # 3. MK.78 - NOUVEAU #2 LONGUE PORTÉE (LMG)
    await db.weapons.update_one(
        {"name": "MK.78"},
        {"$set": {
            "vertical_recoil": 28,
            "horizontal_recoil": 12,
            "is_meta": True,
            "fire_rate": 650,
            "notes": "#2 LONGUE PORTÉE 12 mars 2026 - BUFFÉ - 5.64% pick - V:28 H:12"
        }},
        upsert=True
    )
    print("✅ MK.78 (LMG) : #2 Longue Portée (5.64% pick)")
    
    # 4. Ryden 45K - #2 COURTE PORTÉE
    await db.weapons.update_one(
        {"name": "Ryden 45K"},
        {"$set": {
            "vertical_recoil": 17,
            "horizontal_recoil": 9,
            "is_meta": True,
            "fire_rate": 870,
            "notes": "#2 COURTE PORTÉE 12 mars 2026 - 5.60% pick - V:17 H:9"
        }}
    )
    print("✅ Ryden 45K : #2 Courte Portée (5.60% pick)")
    
    # 5. M15 MOD 0 - #3 LONGUE (NERFÉ)
    await db.weapons.update_one(
        {"name": "M15 MOD 0"},
        {"$set": {
            "vertical_recoil": 24,
            "horizontal_recoil": 8,
            "is_meta": True,
            "fire_rate": 680,
            "notes": "#3 LONGUE 12 mars 2026 - NERFÉ - 5.22% pick - V:24 H:8"
        }}
    )
    print("✅ M15 MOD 0 : #3 Longue (NERFÉ)")
    
    # 6. REV-46 - #3 COURTE (NERFÉ)
    await db.weapons.update_one(
        {"name": "REV-46"},
        {"$set": {
            "vertical_recoil": 20,
            "horizontal_recoil": 12,
            "is_meta": True,
            "fire_rate": 857,
            "notes": "#3 COURTE 12 mars 2026 - NERFÉ - 5.17% pick - V:20 H:12"
        }}
    )
    print("✅ REV-46 : #3 Courte (NERFÉ)")
    
    # 7. Maddox RFB - #4 LONGUE
    await db.weapons.update_one(
        {"name": "Maddox RFB"},
        {"$set": {
            "vertical_recoil": 24,
            "horizontal_recoil": 10,
            "is_meta": True,
            "notes": "#4 LONGUE 12 mars 2026 - 5.17% pick - V:24 H:10"
        }}
    )
    print("✅ Maddox RFB : #4 Longue")
    
    # 8. Carbon 57 - #4 COURTE (dégradé de #1)
    await db.weapons.update_one(
        {"name": "Carbon 57"},
        {"$set": {
            "vertical_recoil": 18,
            "horizontal_recoil": 10,
            "is_meta": True,
            "notes": "#4 COURTE 12 mars 2026 - Dégradé - 4.94% pick - V:18 H:10"
        }}
    )
    print("✅ Carbon 57 : #4 Courte (dégradé)")
    
    # 9. EGRT-17 - #5 LONGUE
    await db.weapons.update_one(
        {"name": "EGRT-17"},
        {"$set": {
            "vertical_recoil": 26,
            "horizontal_recoil": 9,
            "is_meta": True,
            "notes": "#5 LONGUE 12 mars 2026 - 4.93% pick"
        }}
    )
    print("✅ EGRT-17 : #5 Longue")
    
    # 10. Razor 9mm - #5 COURTE (BUFFÉ)
    await db.weapons.update_one(
        {"name": "Razor 9mm"},
        {"$set": {
            "vertical_recoil": 19,
            "horizontal_recoil": 11,
            "is_meta": True,
            "notes": "#5 COURTE 12 mars 2026 - BUFFÉ - 4.87% pick"
        }}
    )
    print("✅ Razor 9mm : #5 Courte (BUFFÉ)")
    
    # 11. M8A1 - DÉGRADÉ A TIER (était #1)
    await db.weapons.update_one(
        {"name": "M8A1"},
        {"$set": {
            "vertical_recoil": 20,
            "horizontal_recoil": 6,
            "is_meta": False,
            "notes": "A TIER #10 - 12 mars 2026 - NERFÉ MASSIF - 0.62% pick"
        }}
    )
    print("⚠️  M8A1 : A TIER (NERFÉ de #1 à #10)")
    
    print("=" * 60)
    print("✅ Mise à jour terminée !")
    
    # Vérification
    print("\n📊 TOP 5 META 12 MARS 2026:")
    top_meta = await db.weapons.find({"is_meta": True}, {"_id": 0, "name": 1, "vertical_recoil": 1, "horizontal_recoil": 1, "notes": 1}).sort([("notes", 1)]).limit(5).to_list(5)
    for i, weapon in enumerate(top_meta, 1):
        print(f"{i}. {weapon['name']} - V:{weapon['vertical_recoil']} H:{weapon['horizontal_recoil']}")

if __name__ == "__main__":
    asyncio.run(update_meta_12_mars())

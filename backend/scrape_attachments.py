#!/usr/bin/env python3
"""
Scraper d'accessoires depuis codmunity.gg pour les armes de Warzone
Ce script extrait les accessoires réels pour chaque arme
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import json
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

# Mapping des noms d'armes dans notre DB vers les URLs codmunity
WEAPON_URL_MAP = {
    "Peacekeeper Mk1": "peacekeeper-mk1",
    "Kogot-7": "kogot-7",
    "Carbon 57": "carbon-57",
    "M15 MOD 0": "m15-mod-0",
    "REV-46": "rev-46",
    "Maddox RFB": "maddox-rfb",
    "EGRT-17": "egrt-17",
    "Razor 9mm": "razor-9mm",
    "MK.78": "mk-78",
    "Ryden 45K": "ryden-45k",
    "Hawker HX": "hawker-hx",
    "AS VAL": "as-val",
    "AK-27": "ak-27",
    "Dravec 45": "dravec-45",
    "DS20 Mirage": "ds20-mirage",
    "MPC-25": "mpc-25",
    "MXR-17": "mxr-17",
    "X9 Maverick": "x9-maverick",
    "Sturmwolf 45": "sturmwolf-45",
    "Merrick 556": "merrick-556",
}

async def scrape_weapon_attachments(weapon_name: str, weapon_url: str):
    """Scrape les accessoires d'une arme depuis codmunity.gg"""
    url = f"https://codmunity.gg/weapon/bo7/{weapon_url}"
    
    print(f"  Scraping {weapon_name}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client_http:
            response = await client_http.get(url, follow_redirects=True)
            
            if response.status_code != 200:
                print(f"    ❌ Erreur HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire les accessoires depuis la section "Attachments"
            attachments = {
                "muzzle": [],
                "barrel": [],
                "optic": [],
                "underbarrel": [],
                "magazine": [],
                "stock": [],
                "rear_grip": [],
                "laser": [],
                "fire_mods": []
            }
            
            # Parser le HTML pour extraire les noms d'accessoires
            # Les accessoires sont généralement dans des divs avec le nom de l'accessoire
            attachment_divs = soup.find_all('div', class_=lambda x: x and 'attachment' in x.lower() if x else False)
            
            # Alternative : rechercher tous les textes qui semblent être des accessoires
            # En se basant sur les données que j'ai déjà vues
            text_content = soup.get_text()
            
            # Extraire les accessoires depuis le texte (méthode simple)
            lines = text_content.split('\n')
            current_category = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Détecter les catégories
                if 'Muzzle' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'muzzle'
                elif 'Barrel' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'barrel'
                elif 'Optic' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'optic'
                elif 'Underbarrel' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'underbarrel'
                elif 'Magazine' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'magazine'
                elif 'Stock' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'stock'
                elif 'Rear Grip' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'rear_grip'
                elif 'Laser' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'laser'
                elif 'Fire Mods' in line and 'Level' in lines[i+1] if i+1 < len(lines) else False:
                    current_category = 'fire_mods'
                
                # Si on a une catégorie active, extraire les noms d'accessoires
                if current_category and line and len(line) > 3 and 'Level' not in line and '%' not in line:
                    # Filtrer les lignes qui ressemblent à des noms d'accessoires
                    if not any(skip in line.lower() for skip in ['ads speed', 'sprint', 'reload', 'bullet', 'damage', 'recoil', 'movement', 'hipfire', 'gun kick', 'separator', 'rpm']):
                        if line not in attachments[current_category]:
                            attachments[current_category].append(line)
            
            # Nettoyer les listes (garder max 15 par catégorie)
            for category in attachments:
                attachments[category] = attachments[category][:15]
            
            print(f"    ✅ {sum(len(v) for v in attachments.values())} accessoires extraits")
            return attachments
            
    except Exception as e:
        print(f"    ❌ Erreur: {str(e)}")
        return None

async def main():
    print("=" * 70)
    print("🔍 SCRAPING DES ACCESSOIRES WARZONE DEPUIS CODMUNITY.GG")
    print("=" * 70)
    print()
    
    all_attachments = {}
    
    for weapon_name, weapon_url in WEAPON_URL_MAP.items():
        attachments = await scrape_weapon_attachments(weapon_name, weapon_url)
        if attachments:
            all_attachments[weapon_name] = attachments
        await asyncio.sleep(1)  # Respecter le rate limiting
    
    print()
    print("=" * 70)
    print(f"✅ SCRAPING TERMINÉ : {len(all_attachments)} armes")
    print("=" * 70)
    
    # Sauvegarder dans un fichier JSON
    output_file = ROOT_DIR / 'weapon_attachments.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_attachments, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Données sauvegardées dans : {output_file}")
    
    # Afficher un échantillon
    print("\n📊 ÉCHANTILLON DES DONNÉES :")
    for weapon in list(all_attachments.keys())[:3]:
        print(f"\n  {weapon}:")
        for category, items in all_attachments[weapon].items():
            if items:
                print(f"    - {category}: {len(items)} items")

if __name__ == "__main__":
    asyncio.run(main())

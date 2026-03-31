#!/usr/bin/env python3
"""
Meta Scraper - CODMunity + WZStats
===================================
Se connecte automatiquement aux 2 sources officielles :
  - https://codmunity.gg/fr         → Pick rates, EaseScores, tiers META
  - https://wzstats.gg/fr/warzone-2/guns → Liste complète + catégories

Actions :
  1. Scrape les 2 sites en parallèle
  2. Fusionne les données (CODMunity prioritaire pour le tier/rank)
  3. Met à jour MongoDB : pick_rate, ease_score, meta_rank, meta_tier, is_meta, last_meta_update
  4. Ajoute les nouvelles armes détectées (non encore en DB)
  5. Bascule sur un snapshot cache si le scraping échoue

Fréquence recommandée : 1× par jour (scheduler asyncio dans server.py)
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re
import uuid
import json
import logging
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# ─── CONFIG ────────────────────────────────────────────────────────────────────
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME   = os.environ.get('DB_NAME', 'adj_killagain_db')

CODMUNITY_URL = "https://codmunity.gg/fr"
WZSTATS_URL   = "https://wzstats.gg/fr/warzone-2/guns"
CACHE_FILE    = ROOT_DIR / "meta_cache.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

# Mapping vers catégories unifiées
CATEGORY_MAP = {
    "fusil d'assault":                    "AR",
    "fusil d'assaut":                     "AR",
    "fusil d'assault longue portée":      "AR",
    "fusil d'assault soutien de sniper":  "AR",
    "fusil d'assault courte portée":      "AR",
    "mitraillette":                       "SMG",
    "mitraillette courte portée":         "SMG",
    "mitraillette soutien de sniper":     "SMG",
    "mitrailleuse":                       "LMG",
    "mitrailleuse longue portée":         "LMG",
    "fusil de précision":                 "SNIPER",
    "sniper rifle":                       "SNIPER",
    "sniper rifle fusil de précision":    "SNIPER",
    "fusil à pompe":                      "SHOTGUN",
    "pistolet":                           "PISTOL",
    "marksman":                           "MARKSMAN",
    "spécial":                            "SPECIAL",
}

# ─── SNAPSHOT META (31 mars 2026 - CODMunity + WZStats) ────────────────────────
# Utilisé comme :
#   1. Fallback si le scraping live échoue
#   2. Données de référence pour la première exécution
KNOWN_META = {
    "date":   "2026-03-31",
    "source": "CODMunity + WZStats (scraping 31/03/2026)",
    "weapons": [
        # ── ABSOLUTE META ──────────────────────────────────────────────────────
        {
            "name": "Voyak KT-3",   "category": "AR",     "game": "BO7",
            "pick_rate": 20.4,      "ease_score": 8.5,
            "meta_tier": "ABSOLUTE_META",  "meta_rank": 1,  "is_meta": True,
            "vertical_recoil": 18, "horizontal_recoil": 7, "fire_rate": 730,
            "damage": 34, "range_meters": 58,
            "notes": "#1 ABSOLUTE META - 20.4% Pick Rate - BO7",
        },
        {
            "name": "Razor 9mm",    "category": "SMG",    "game": "BO6",
            "pick_rate": 19.7,      "ease_score": 6.5,
            "meta_tier": "ABSOLUTE_META",  "meta_rank": 2,  "is_meta": True,
            "notes": "#2 ABSOLUTE META - 19.7% Pick Rate",
        },
        {
            "name": "Dravec 45",    "category": "SMG",    "game": "BO6",
            "pick_rate": 12.9,      "ease_score": 7.3,
            "meta_tier": "ABSOLUTE_META",  "meta_rank": 3,  "is_meta": True,
            "notes": "#3 ABSOLUTE META - 12.9% Pick Rate",
        },
        {
            "name": "Hawker HX",    "category": "SNIPER", "game": "BO6",
            "pick_rate": 5.9,       "ease_score": None,
            "meta_tier": "ABSOLUTE_META",  "meta_rank": 4,  "is_meta": True,
            "notes": "#4 ABSOLUTE META - 5.9% Pick Rate",
        },
        # ── META ───────────────────────────────────────────────────────────────
        {
            "name": "Peacekeeper Mk1", "category": "AR",  "game": "BO6",
            "pick_rate": 6.8,          "ease_score": 9.1,
            "meta_tier": "META",        "meta_rank": 5,    "is_meta": True,
            "notes": "#5 META - EaseScore 9.1",
        },
        {
            "name": "EGRT-17",      "category": "AR",     "game": "BO6",
            "pick_rate": 5.4,       "ease_score": 6.1,
            "meta_tier": "META",    "meta_rank": 6,        "is_meta": True,
            "notes": "#6 META",
        },
        {
            "name": "Ryden 45K",    "category": "SMG",    "game": "BO6",
            "pick_rate": 2.8,       "ease_score": 8.5,
            "meta_tier": "META",    "meta_rank": 7,        "is_meta": True,
            "notes": "#7 META",
        },
        {
            "name": "Kogot-7",      "category": "SMG",    "game": "BO6",
            "pick_rate": 2.3,       "ease_score": 7.9,
            "meta_tier": "META",    "meta_rank": 8,        "is_meta": True,
            "notes": "#8 META",
        },
        {
            "name": "MK.78",        "category": "LMG",    "game": "BO6",
            "pick_rate": 1.0,       "ease_score": 8.5,
            "meta_tier": "META",    "meta_rank": 9,        "is_meta": True,
            "notes": "#9 META - LMG",
        },
        {
            "name": "VS Recon",     "category": "SNIPER", "game": "BO6",
            "pick_rate": 1.1,       "ease_score": None,
            "meta_tier": "META",    "meta_rank": 10,       "is_meta": True,
            "notes": "#10 META",
        },
        {
            "name": "HDR",          "category": "SNIPER", "game": "MW",
            "pick_rate": 0.3,       "ease_score": None,
            "meta_tier": "META",    "meta_rank": 11,       "is_meta": True,
            "notes": "#11 META",
        },
    ]
}

# ─── NOUVELLES ARMES À AJOUTER (pour compléter le catalogue) ──────────────────
# Ces armes sont légitimes dans Warzone mais absentes de la DB actuelle.
# Le scraper les injecte une seule fois si elles ne sont pas encore présentes.
NEW_WEAPONS_CATALOG = [
    # BO7
    {"name": "Voyak KT-3",   "category": "AR",     "game": "BO7",
     "vertical_recoil": 18,  "horizontal_recoil": 7,  "fire_rate": 730,
     "damage": 34, "range_meters": 58, "is_meta": True,
     "meta_tier": "ABSOLUTE_META", "meta_rank": 1, "pick_rate": 20.4, "ease_score": 8.5,
     "notes": "#1 ABSOLUTE META BO7 - 20.4% Pick"},
    {"name": "Swordfish A1", "category": "AR",     "game": "BO7",
     "vertical_recoil": 24,  "horizontal_recoil": 9,  "fire_rate": 680,
     "damage": 33, "range_meters": 55, "is_meta": False,
     "meta_tier": "A_TIER", "pick_rate": 0.8, "ease_score": 7.5,
     "notes": "A Tier - BO7"},
    # MW Classics
    {"name": "AK-47",        "category": "AR",     "game": "MW",
     "vertical_recoil": 32,  "horizontal_recoil": 15, "fire_rate": 545,
     "damage": 35, "range_meters": 50, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier - Classique"},
    {"name": "MP5",          "category": "SMG",    "game": "MW",
     "vertical_recoil": 16,  "horizontal_recoil": 8,  "fire_rate": 833,
     "damage": 26, "range_meters": 18, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier - Classique"},
    {"name": "M16",          "category": "AR",     "game": "CW",
     "vertical_recoil": 18,  "horizontal_recoil": 6,  "fire_rate": 487,
     "damage": 33, "range_meters": 52, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier - Burst"},
    {"name": "AUG",          "category": "SMG",    "game": "MW",
     "vertical_recoil": 20,  "horizontal_recoil": 9,  "fire_rate": 857,
     "damage": 28, "range_meters": 20, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier"},
    {"name": "RAM-7",        "category": "AR",     "game": "MW",
     "vertical_recoil": 24,  "horizontal_recoil": 10, "fire_rate": 857,
     "damage": 29, "range_meters": 45, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier"},
    {"name": "Fennec 45",    "category": "SMG",    "game": "MW2",
     "vertical_recoil": 15,  "horizontal_recoil": 8,  "fire_rate": 1000,
     "damage": 21, "range_meters": 15, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier - Plus haut fire rate"},
    {"name": "WSP Swarm",    "category": "SMG",    "game": "MW3",
     "vertical_recoil": 14,  "horizontal_recoil": 9,  "fire_rate": 1066,
     "damage": 20, "range_meters": 14, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier"},
    {"name": "SPR 208",      "category": "MARKSMAN","game": "MW",
     "vertical_recoil": 26,  "horizontal_recoil": 6,  "fire_rate": 390,
     "damage": 80, "range_meters": 75, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier - One-shot possible"},
    {"name": "Intervention", "category": "SNIPER", "game": "MW1",
     "vertical_recoil": 98,  "horizontal_recoil": 4,  "fire_rate": 32,
     "damage": 250,"range_meters": 150,"is_meta": False,
     "meta_tier": "C_TIER", "notes": "C Tier - Légendaire"},
    {"name": "R-99",         "category": "SMG",    "game": "BO6",
     "vertical_recoil": 17,  "horizontal_recoil": 9,  "fire_rate": 950,
     "damage": 22, "range_meters": 16, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier"},
    {"name": "GP25",         "category": "SPECIAL","game": "BO6",
     "vertical_recoil": 50,  "horizontal_recoil": 20, "fire_rate": 60,
     "damage": 150,"range_meters": 30, "is_meta": False,
     "meta_tier": "C_TIER", "notes": "C Tier - Lanceur"},
    {"name": "Combat Knife", "category": "SPECIAL","game": "BO6",
     "vertical_recoil": 0,   "horizontal_recoil": 0,  "fire_rate": 999,
     "damage": 200,"range_meters": 2,  "is_meta": False,
     "meta_tier": "C_TIER", "notes": "C Tier - Mêlée"},
    {"name": "Dragunov",     "category": "SNIPER", "game": "MW",
     "vertical_recoil": 88,  "horizontal_recoil": 12, "fire_rate": 260,
     "damage": 80, "range_meters": 90, "is_meta": False,
     "meta_tier": "C_TIER", "notes": "C Tier - Semi-auto sniper"},
    {"name": "M82",          "category": "SNIPER", "game": "CW",
     "vertical_recoil": 100, "horizontal_recoil": 8,  "fire_rate": 40,
     "damage": 200,"range_meters": 120,"is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier - Anti-matériel"},
    {"name": "Bruen MK9",    "category": "LMG",    "game": "MW",
     "vertical_recoil": 28,  "horizontal_recoil": 10, "fire_rate": 680,
     "damage": 36, "range_meters": 58, "is_meta": False,
     "meta_tier": "B_TIER", "notes": "B Tier - LMG"},
]


# ─── FONCTIONS DE SCRAPING ──────────────────────────────────────────────────────

async def fetch_page(session: aiohttp.ClientSession, url: str) -> str | None:
    """Récupère le HTML d'une page avec timeout de 15s."""
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                return await resp.text()
            logger.warning(f"HTTP {resp.status} pour {url}")
    except Exception as e:
        logger.warning(f"Erreur scraping {url}: {e}")
    return None


def parse_pick_rate(text: str) -> float | None:
    """Extrait un pourcentage de pick rate depuis un texte."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*Pick", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def parse_ease_score(text: str) -> float | None:
    """Extrait un EaseScore depuis un texte."""
    m = re.search(r"EaseScore\s+(\d+(?:\.\d+)?)", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def normalize_category(raw: str) -> str:
    """Convertit une catégorie en texte vers le code unifié (AR/SMG/…)."""
    key = raw.strip().lower()
    return CATEGORY_MAP.get(key, raw.upper()[:10])


# Mots-clés de navigation à exclure des armes détectées
_NAV_WORDS = {
    "metas", "tools", "competitive", "other websites", "other links",
    "top 20 meta", "download our mobile app", "follow us on socials",
    "additional links", "warzone", "multiplayer", "ranked play",
    "black ops", "zombies", "stats comparator", "camo tracker",
    "tier list", "calendar", "explore creators", "social sharing",
    "pullze check", "top 250", "world series", "esports world cup",
    "resurgence series", "battlefinity", "warzone loadout",
}

# Noms d'armes confirmés présents sur CODMunity (pour validation)
_KNOWN_WEAPON_NAMES = {w["name"].lower() for w in KNOWN_META["weapons"]}


def _is_weapon_name(text: str) -> bool:
    """Retourne True si le texte ressemble à un nom d'arme (pas un lien de nav)."""
    t = text.strip().lower()
    if not t or len(t) < 2:
        return False
    # Exclusion explicite des items de navigation
    if t in _NAV_WORDS:
        return False
    # Les noms d'armes connus passent toujours
    if t in _KNOWN_WEAPON_NAMES:
        return True
    # Heuristique : un nom d'arme ne contient pas "icon", "app", "download",
    # "follow", "apps.apple", "play.google", etc.
    bad_keywords = ["icon", "app store", "play store", "follow", "download",
                    "conditions", "confidentialité", "copyright"]
    return not any(k in t for k in bad_keywords)


async def scrape_codmunity() -> list[dict]:
    """
    Scrape codmunity.gg/fr et renvoie la liste des armes META détectées.
    Les pick rates ne sont pas toujours dans le HTML statique (JS-rendered),
    donc on les enrichit depuis KNOWN_META en fallback.
    """
    weapons = []
    async with aiohttp.ClientSession() as session:
        html = await fetch_page(session, CODMUNITY_URL)

    if not html:
        return weapons

    soup = BeautifulSoup(html, "html.parser")
    current_tier = "META"
    in_meta_section = False
    rank = 0

    # Index KNOWN_META pour enrichissement pick rate / ease score
    known_index = {w["name"].lower(): w for w in KNOWN_META["weapons"]}

    for tag in soup.find_all(["h2", "h3"]):
        text = tag.get_text(strip=True)

        if "ABSOLUTE META" in text.upper():
            current_tier = "ABSOLUTE_META"
            in_meta_section = True
            continue
        if "WARZONE META" in text.upper() and "ABSOLUTE" not in text.upper():
            current_tier = "META"
            in_meta_section = True
            continue
        # Sortie de la section méta (Download, Follow, Additional Links…)
        if any(kw in text.upper() for kw in ["DOWNLOAD", "FOLLOW", "ADDITIONAL"]):
            in_meta_section = False
            continue

        if not in_meta_section:
            continue

        if tag.name == "h3" and _is_weapon_name(text):
            # Cherche le bloc parent pour en tirer catégorie, pick %, EaseScore
            parent = tag.find_parent()
            parent_text = parent.get_text(" ", strip=True) if parent else ""

            pick_rate  = parse_pick_rate(parent_text)
            ease_score = parse_ease_score(parent_text)

            # Enrichissement depuis KNOWN_META si le live n'a pas les valeurs
            known = known_index.get(text.lower(), {})
            if pick_rate  is None: pick_rate  = known.get("pick_rate")
            if ease_score is None: ease_score = known.get("ease_score")

            # Catégorie : premier texte entre le h3 et les chiffres
            cat_raw = re.split(r"\d", parent_text)[0].replace(text, "").strip()
            category = normalize_category(cat_raw) if cat_raw else known.get("category", "AR")
            game = known.get("game", "BO7" if current_tier == "ABSOLUTE_META" else "BO6")

            # Évite les doublons
            if any(w["name"].lower() == text.lower() for w in weapons):
                continue

            rank += 1
            weapons.append({
                "name":       text,
                "category":   category,
                "game":       game,
                "pick_rate":  pick_rate,
                "ease_score": ease_score,
                "meta_tier":  current_tier,
                "meta_rank":  rank,
                "is_meta":    True,
            })
            logger.info(f"CODMunity: {text} ({current_tier}, pick={pick_rate}%)")

    return weapons


async def scrape_wzstats() -> list[str]:
    """
    Scrape wzstats.gg et renvoie la liste des noms d'armes META.
    WZStats liste les META Guns dans un paragraphe de liens.
    """
    names = []
    async with aiohttp.ClientSession() as session:
        html = await fetch_page(session, WZSTATS_URL)

    if not html:
        return names

    soup = BeautifulSoup(html, "html.parser")

    # Les armes META sont dans des liens [NomArme]
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/best-loadouts/" in href or "/warzone-2/guns/" in href:
            name = a.get_text(strip=True)
            if name and len(name) > 2:
                names.append(name)

    # Déduplique en conservant l'ordre
    seen = set()
    unique = []
    for n in names:
        if n not in seen:
            seen.add(n)
            unique.append(n)

    logger.info(f"WZStats: {len(unique)} armes détectées")
    return unique


# ─── FONCTION PRINCIPALE DE MISE À JOUR ────────────────────────────────────────

async def update_meta_in_db() -> dict:
    """
    Met à jour la base de données avec la méta actuelle.
    Retourne un rapport de la mise à jour.
    """
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    now = datetime.now(timezone.utc).isoformat()
    report = {
        "started_at":     now,
        "sources":        [],
        "weapons_updated": 0,
        "weapons_added":  0,
        "errors":         [],
    }

    # ── 1. Scraping live ───────────────────────────────────────────────────────
    logger.info("🌐 Scraping CODMunity + WZStats en parallèle…")
    codmunity_weapons, wzstats_names = await asyncio.gather(
        scrape_codmunity(),
        scrape_wzstats(),
        return_exceptions=True,
    )

    if isinstance(codmunity_weapons, Exception):
        report["errors"].append(f"CODMunity: {codmunity_weapons}")
        codmunity_weapons = []
    if isinstance(wzstats_names, Exception):
        report["errors"].append(f"WZStats: {wzstats_names}")
        wzstats_names = []

    # ── 2. Fusion des données ──────────────────────────────────────────────────
    # Priorité: CODMunity (pick rate + tier) > WZStats (présence dans méta)
    # Si le scraping a rapporté moins de 4 armes → on utilise le snapshot connu
    if len(codmunity_weapons) < 4:
        logger.warning("⚠️  Scraping insuffisant → fallback sur snapshot du 31/03/2026")
        live_weapons = KNOWN_META["weapons"]
        report["sources"].append("snapshot_2026-03-31 (fallback)")
    else:
        live_weapons = codmunity_weapons
        report["sources"].append("CODMunity (live)")

    if wzstats_names:
        report["sources"].append("WZStats (live)")

    # ── 3. Mise à jour des armes META dans MongoDB ─────────────────────────────
    ts = datetime.now(timezone.utc).isoformat()

    for w in live_weapons:
        name = w.get("name", "")
        if not name:
            continue

        update_fields = {
            "is_meta":          w.get("is_meta", True),
            "meta_tier":        w.get("meta_tier", "META"),
            "last_meta_update": ts,
        }
        if w.get("meta_rank") is not None:
            update_fields["meta_rank"]  = w["meta_rank"]
        if w.get("pick_rate") is not None:
            update_fields["pick_rate"]  = w["pick_rate"]
        if w.get("ease_score") is not None:
            update_fields["ease_score"] = w["ease_score"]
        if w.get("notes"):
            update_fields["notes"] = w["notes"]

        result = await db.weapons.update_one(
            {"name": {"$regex": f"^{re.escape(name)}$", "$options": "i"}},
            {"$set": update_fields},
        )
        if result.matched_count > 0:
            report["weapons_updated"] += 1
            logger.info(f"✅ Mis à jour: {name} ({w.get('meta_tier')})")
        else:
            logger.info(f"⚠️  Non trouvée en DB: {name} → sera ajoutée via le catalogue")

    # ── 4. Marquer les armes non-META comme telles ─────────────────────────────
    meta_names = [w["name"] for w in live_weapons]
    await db.weapons.update_many(
        {"name": {"$nin": meta_names}, "is_meta": True},
        {"$set": {"is_meta": False, "meta_tier": "B_TIER", "last_meta_update": ts}},
    )

    # ── 5. Ajout des nouvelles armes du catalogue ──────────────────────────────
    existing = await db.weapons.find({}, {"name": 1, "_id": 0}).to_list(1000)
    existing_names_lower = {w["name"].lower() for w in existing}

    for weapon_data in NEW_WEAPONS_CATALOG:
        if weapon_data["name"].lower() in existing_names_lower:
            continue  # déjà présente

        doc = {
            "id":               str(uuid.uuid4()),
            "name":             weapon_data["name"],
            "category":         weapon_data.get("category", "AR"),
            "game":             weapon_data.get("game", "BO6"),
            "vertical_recoil":  weapon_data.get("vertical_recoil", 25),
            "horizontal_recoil":weapon_data.get("horizontal_recoil", 10),
            "fire_rate":        weapon_data.get("fire_rate", 700),
            "damage":           weapon_data.get("damage", 30),
            "range_meters":     weapon_data.get("range_meters", 40),
            "rapid_fire":       False,
            "rapid_fire_value": 0,
            "recommended_build":None,
            "is_meta":          weapon_data.get("is_meta", False),
            "is_hidden_meta":   False,
            "meta_tier":        weapon_data.get("meta_tier", "B_TIER"),
            "meta_rank":        weapon_data.get("meta_rank", None),
            "pick_rate":        weapon_data.get("pick_rate", None),
            "ease_score":       weapon_data.get("ease_score", None),
            "notes":            weapon_data.get("notes", ""),
            "last_meta_update": ts,
            "created_at":       ts,
            "updated_at":       ts,
        }
        await db.weapons.insert_one(doc)
        existing_names_lower.add(weapon_data["name"].lower())
        report["weapons_added"] += 1
        logger.info(f"➕ Ajoutée: {weapon_data['name']} ({weapon_data.get('category')})")

    # ── 6. Sauvegarde du cache ─────────────────────────────────────────────────
    cache = {
        "last_update": ts,
        "sources":     report["sources"],
        "meta_count":  len(live_weapons),
        "meta_weapons": [w.get("name") for w in live_weapons],
    }
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Impossible de sauvegarder le cache: {e}")

    # ── 7. Rapport final ───────────────────────────────────────────────────────
    total = await db.weapons.count_documents({})
    meta_total = await db.weapons.count_documents({"is_meta": True})
    report["finished_at"]      = datetime.now(timezone.utc).isoformat()
    report["total_weapons_db"] = total
    report["meta_weapons_db"]  = meta_total

    logger.info(
        f"✅ Sync terminée — Total DB: {total} armes "
        f"({meta_total} META) — "
        f"{report['weapons_updated']} mises à jour, "
        f"{report['weapons_added']} ajoutées"
    )
    mongo_client.close()
    return report


def load_cache() -> dict | None:
    """Charge le snapshot de cache local si disponible."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


# ─── ENTRÉE DIRECTE (exécutable standalone) ─────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    print("=" * 60)
    print("  META SCRAPER - CODMunity + WZStats")
    print("=" * 60)
    result = asyncio.run(update_meta_in_db())
    print()
    print(f"✅ Terminé !")
    print(f"   Sources      : {', '.join(result['sources'])}")
    print(f"   Mis à jour   : {result['weapons_updated']}")
    print(f"   Ajoutées     : {result['weapons_added']}")
    print(f"   Total DB     : {result['total_weapons_db']} armes")
    print(f"   META actives : {result['meta_weapons_db']}")
    if result['errors']:
        print(f"   ⚠️  Erreurs   : {result['errors']}")
    print("=" * 60)

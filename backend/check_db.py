import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent / '.env')
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]

async def check():
    total = await db.weapons.count_documents({})
    meta  = await db.weapons.count_documents({'is_meta': True})
    abs_meta = await db.weapons.count_documents({'meta_tier': 'ABSOLUTE_META'})
    print(f"Total armes : {total}")
    print(f"META        : {meta}")
    print(f"ABSOLUTE META: {abs_meta}")
    print()
    print("--- TOP META (pick rate) ---")
    async for w in db.weapons.find({'is_meta': True}, {'_id':0,'name':1,'meta_tier':1,'pick_rate':1,'ease_score':1,'meta_rank':1}).sort('meta_rank', 1):
        pr = f"{w.get('pick_rate','?')}%" if w.get('pick_rate') else '-'
        es = w.get('ease_score', '?')
        rank = w.get('meta_rank', '?')
        tier = w.get('meta_tier', '?')
        print(f"  [{rank}] {w['name']:25} {tier:15} pick:{pr:8} ease:{es}")

asyncio.run(check())

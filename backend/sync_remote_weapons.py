import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from pymongo import MongoClient

root = Path(r"c:\Darknexus-main\warzone\backend")
load_dotenv(root / '.env')

mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'zen_hub_pro')
remote_url = 'https://projet-studio.preview.emergentagent.com/api/weapons'

resp = requests.get(remote_url, timeout=25)
resp.raise_for_status()
weapons = resp.json()
if not isinstance(weapons, list):
    raise RuntimeError('remote data is not list')

client = MongoClient(mongo_url)
col = client[db_name]['weapons']
col.delete_many({})
if weapons:
    col.insert_many(weapons)
print('IMPORTED_WEAPONS=' + str(col.count_documents({})))

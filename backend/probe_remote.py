import requests
base='https://projet-studio.preview.emergentagent.com'
paths=['/api','/api/','/api/stats','/api/weapons','/api/weapons/','/api/seed-weapons','/api/chat']
for p in paths:
    u=base+p
    try:
        r=requests.get(u,timeout=12)
        print(p, r.status_code)
    except Exception as e:
        print(p, 'ERR', e)

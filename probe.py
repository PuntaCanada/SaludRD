import json, urllib.request, urllib.parse, sys
sources=["listado-de-centros-de-salud","establecimientos-de-salud-sns","establecimientos-de-salud-habilitados-y-no-habilitados"]
failed=False
for slug in sources:
    url='https://datos.gov.do/api/3/action/package_show?'+urllib.parse.urlencode({'id':slug})
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'PublicDataDirectory/1.0','Accept':'application/json'}),timeout=35) as r: d=json.load(r)
        p=d['result']; print(json.dumps({'dataset':slug,'license':p.get('license_id'),'modified':p.get('metadata_modified'),'csv':[{'url':x.get('url'),'name':x.get('name')} for x in p.get('resources',[]) if x.get('format','').lower()=='csv']},ensure_ascii=False))
    except Exception as e:
        print(slug,repr(e),file=sys.stderr)
        failed=True

if failed: sys.exit(1)

"""Validate official SNS workbook; publication is gated on explicit licence clearance."""
import io,json,urllib.request,hashlib,os,tempfile
from pathlib import Path
from openpyxl import load_workbook
URL='https://repositorio.sns.gob.do/descargas/76/establecimientos-de-salud/2120/hospitales-y-centros-de-primer-nivel-de-atencion-act-23-10-2026.xlsx'
def parse(data):
    sheet=load_workbook(io.BytesIO(data),read_only=True,data_only=True).active
    iterator=sheet.values
    headers=next(iterator)
    required=['ID_CENTRO','NombreCentro','Provincia','Municipio','Suspendido','Nivel_atencion']
    if any(k not in headers for k in required): raise ValueError('Schema changed')
    idx={k:headers.index(k) for k in required}
    result={}
    skipped=0
    for row in iterator:
        def get(k):
            v=row[idx[k]]
            return '' if v is None else str(v).strip()
        id,name,province,city,status,level=(get(k) for k in required)
        if not all([id,name,province,city]) or status.casefold() not in ('0','0.0','no','false'):
            skipped+=1
            continue
        item=dict(id=id,name=name,province=province,city=city,level=level,source=URL,sourceDate='2026-10-23')
        if id in result and result[id]!=item: raise ValueError('Conflicting facility ID')
        result[id]=item
    return list(result.values()),skipped
def main():
    with urllib.request.urlopen(URL,timeout=45) as r: data=r.read(20_000_001)
    if not data or len(data)>20_000_000: raise ValueError('Invalid download size')
    rows,skipped=parse(data)
    print('validated',len(rows),'skipped',skipped,'sha256',hashlib.sha256(data).hexdigest())
    if len(rows)<100 or len({r['province'] for r in rows})<10: raise ValueError('Coverage threshold failed')
    # No public data write until the licence for this specific workbook is confirmed.
    if os.environ.get('SNS_REUSE_APPROVED')!='yes': return
    target=Path('data/observations.json')
    old=json.loads(target.read_text())
    if len(rows)<len(old): raise ValueError('Refusing smaller dataset')
    # Keep manual records until their identity can be reconciled with official IDs.
    combined=rows+[r for r in old if not r.get('id') and not any(x['name'].casefold()==r['name'].casefold() and x['province'].casefold()==r['province'].casefold() for x in rows)]
    fd,tmp=tempfile.mkstemp(dir=target.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(combined,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
if __name__=='__main__': main()

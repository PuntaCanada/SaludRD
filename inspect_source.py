import io,json,urllib.request,hashlib
URL="https://repositorio.sns.gob.do/descargas/76/establecimientos-de-salud/2120/hospitales-y-centros-de-primer-nivel-de-atencion-act-23-10-2026.xlsx"
with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'PublicDataDirectory/1.0'}),timeout=45) as response:
    data=response.read(20_000_001)
if not data or len(data)>20_000_000: raise ValueError('Invalid download size')
print('bytes',len(data),'sha256',hashlib.sha256(data).hexdigest())
from openpyxl import load_workbook
book=load_workbook(io.BytesIO(data),read_only=True,data_only=True)
for sheet in book:
    print('sheet',sheet.title,'dimensions',sheet.max_row,sheet.max_column)
    for row in sheet.iter_rows(min_row=1,max_row=8,values_only=True): print(repr(row)[:2000])

from pathlib import Path
import hashlib,json
O=Path(__file__).resolve().parent;R=O.parents[2];p=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=p.read_bytes()
rows=[]
for f in json.loads((O/'results.json').read_text())[0]['functions']:
 address=int(f['stock_address'],16);stripped=address-0x3300;absolute=stripped+32;n=f['stock_bytes'];data=b[absolute:absolute+n]
 assert hashlib.sha256(data).hexdigest()==f['sha256']
 rows.append({'function':f['function'],'flash_address':address,'flash_base':0x3300,'wrapper_bytes':32,'wrapper_stripped_offset':stripped,'absolute_payload_offset':absolute,'bytes':n,'sha256':hashlib.sha256(data).hexdigest()})
out={'schema_version':1,'payload_path':str(p.relative_to(R)),'payload_sha256':hashlib.sha256(b).hexdigest(),'result_receipt_sha256':hashlib.sha256((O/'results.json').read_bytes()).hexdigest(),'targets':rows,'legacy_records_mutated':False}
(O/'coordinate-receipt.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS absolute and wrapper-stripped target coordinates')

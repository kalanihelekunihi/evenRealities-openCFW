from pathlib import Path
import json,hashlib
exec(Path('/tmp/g2-index16278.py').read_text().split('paths=')[0])
source=root/'campaign-private-instruction-image-candidates-16280/001/excluded.json';excluded=json.loads(source.read_text());reports=[]
for item in excluded:
 if item['reason']!='no whole-file candidate image byte match':continue
 p=Path(item['path']);raw=p.read_bytes();assert h(raw)==item['sha256'];obj=json.loads(raw)
 if isinstance(obj,dict) and isinstance(obj.get('regions'),list):obj=obj['regions']
 if isinstance(obj,dict) and isinstance(obj.get('instructions'),list):obj=[obj]
 if obj and all(isinstance(x,dict) and ('address' in x or 'pc' in x) for x in obj):obj=[{'instructions':obj}]
 rows=[]
 for block in obj:
  for row in block['instructions']:
   addr=row.get('address',row.get('pc'));addr=int(addr,0) if isinstance(addr,str) else addr;field=next(k for k in ['source_bytes_hex','source_bytes','bytes_hex','bytes','encoding'] if k in row);value=row[field];v=bytes.fromhex(''.join(value) if isinstance(value,list) else value);rows.append((addr,v,field))
 candidates=[]
 for image,space,mm,data in spaces:
  for variant in ['as_recorded','each_halfword_byte_swapped']:
   matched=0;mapped=0;first=None
   for addr,rawbytes,field in rows:
    v=rawbytes if variant=='as_recorded' else b''.join(rawbytes[j:j+2][::-1] for j in range(0,len(rawbytes),2));possible=[m['image_start']+addr-m['loaded_start'] for m in mm if m['loaded_start']<=addr and addr+len(v)<=m['loaded_end']]
    if possible:mapped+=1
    valid=[off for off in possible if data[off:off+len(v)]==v]
    if len(valid)==1:matched+=1
    elif first is None:first=dict(address=addr,recorded_byte_field=field,recorded_hex=rawbytes.hex(),candidate_hex=v.hex(),mapped_image_offsets=possible,actual_hex=[data[off:off+len(v)].hex() for off in possible])
   if mapped:candidates.append(dict(image_id=image,address_space_id=space,byte_interpretation=variant,matched_rows=matched,mapped_rows=mapped,first_mismatch=first))
 candidates.sort(key=lambda x:(-x['matched_rows'],-x['mapped_rows'],x['image_id'],x['byte_interpretation']));reports.append(dict(path=str(p),sha256=h(raw),instruction_rows=len(rows),best_candidate_diagnostics=candidates[:3],qualification='No repair or ownership admission; mismatch is evidence for further inspection'))
o=Path('reviews/P2-15877-instruction-mismatch-triage-independent-review/001/fresh');o.mkdir(parents=True,exist_ok=False);(o/'triage.json').write_text(json.dumps(reports,indent=2)+'\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'summary.json').write_text(json.dumps(dict(accepted=False,status='diagnostic',source_path=str(source),source_sha256=h(source.read_bytes()),inventory_sha256=h(iraw),records=len(reports),records_with_partial_byte_match=sum(bool(r['best_candidate_diagnostics'] and r['best_candidate_diagnostics'][0]['matched_rows']) for r in reports),limitations=['Scores do not prove image ownership or semantics','Entire mismatch records remain excluded','No file repair promotion coverage admission or gates']),indent=2)+'\n');print('PASS',len(reports))
for r in reports[:8]:print(Path(r['path']).parent.parent.name,r['instruction_rows'],r['best_candidate_diagnostics'][0] if r['best_candidate_diagnostics'] else 'unmapped')

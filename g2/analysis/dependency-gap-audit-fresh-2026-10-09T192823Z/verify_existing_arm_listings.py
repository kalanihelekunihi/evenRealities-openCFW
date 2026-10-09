from pathlib import Path
import re,json,hashlib,subprocess
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
images={}
for line in (ROOT/'g2/build/pseudocode-first/20260930T190500Z/inventory/images.jsonl').read_text().splitlines():
 d=json.loads(line)
 if d['id'] in ['apollo_main:flash','apollo_bootloader:flash','touch:flash','case:flash']:
  b=Path(d['content_path']).read_bytes();assert sha(b)==d['content_sha256'];m=d['address_spaces'][0]['mappings'][0]
  images[d['payload_id']]={'bytes':b,'base':m['loaded_start'],'payload_offset':d['source_span'][0],'hash':sha(b)}
inventory=[];selected=[]
for rel in sorted(subprocess.check_output(['rg','--files','--hidden','--no-ignore','g2'],text=True).splitlines()):
 p=ROOT/rel
 if not re.search(r'(disassembl|disasm|objdump|\.s$|\.asm$)',p.name,re.I):continue
 if any(x in p.parts for x in ['coverage-audit-parallel-2026-10-09',OUT.name]):continue
 inventory.append(str(p.relative_to(ROOT)))
 if p.suffix.lower() not in ['.txt','.disasm','.s','.asm']:continue
 if ('original' in p.name.lower() and 'disasm' in p.name.lower()) or ('original' in p.name.lower() and 'disassembl' in p.name.lower()) or (p.name=='disassembly.txt' and 'bootloader-completion-2026-10-06' in p.parts):selected.append(p)
summary={k:{'addresses':set(),'files':[],'mismatches':0,'data_directive_bytes':0} for k in images}
receipts=[]
for p in selected:
 text=p.read_text(errors='replace');counts={};bad=[];directives=0
 gnu='Disassembly of section ' in text and 'file format ' in text
 for line in text.splitlines():
  pattern=r'^\s*([0-9a-fA-F]{6,8}):\s+((?:[0-9a-fA-F]{4,8}\s+){1,2})\t([A-Za-z.][A-Za-z0-9_.]*)\b' if gnu else r'^\s*([0-9a-fA-F]{6,8}):?\s+([0-9a-fA-F]{4,8})\s+([A-Za-z.][A-Za-z0-9_.]*)\b'
  m=re.match(pattern,line)
  if not m:continue
  a=int(m[1],16);mn=m[3]
  raw=b''.join(int(t,16).to_bytes(len(t)//2,'little') for t in m[2].split()) if gnu else bytes.fromhex(m[2])
  target=next((k for k,v in images.items() if v['base']<=a<a+len(raw)<=v['base']+len(v['bytes'])),None)
  if target is None:continue
  v=images[target];off=a-v['base'];actual=v['bytes'][off:off+len(raw)]
  # GNU banner-marked ARM listings serialize little-endian halfword tokens;
  # Capstone exports serialize byte strings. Never infer format from equality.
  if actual!=raw:summary[target]['mismatches']+=1;bad.append({'component':target,'address':hex(a),'shown':raw.hex(),'actual':actual.hex()});continue
  data=mn.startswith('.') or mn.lower() in ['dcw','dcd','db','dw']
  if data:summary[target]['data_directive_bytes']+=len(raw);directives+=len(raw);continue
  summary[target]['addresses'].update(range(off+v['payload_offset'],off+v['payload_offset']+len(raw)));counts[target]=counts.get(target,0)+len(raw)
 if counts or bad:receipts.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p.read_bytes()),'matched_line_bytes':counts,'data_directive_bytes':directives,'mismatch_count':len(bad),'mismatch_examples':bad[:3],'explicit_CODE_header':bool(re.search(r'^CODE ',text,re.M)),'locked_range_header':bool(re.search(r'^# Locked runtime ',text,re.M))})
 for k in counts:summary[k]['files'].append(str(p.relative_to(ROOT)))
payloads={'apollo_main':3523396,'apollo_bootloader':148599,'touch':34464,'case':55784}
result=[]
for k,v in summary.items():
 a=sorted(v.pop('addresses'));ranges=[]
 for i in a:
  if ranges and ranges[-1][1]==i:ranges[-1][1]=i+1
  else:ranges.append([i,i+1])
 result.append({'component':k,'unique_byte_correspondence':len(a),'stored_payload_bytes':payloads[k],'bounded_artifact_payload_percent':100*len(a)/payloads[k],'payload_ranges':ranges,**v,'whole_executable_assembly_percent':None,'limitation':'Original-byte correspondence of selected existing listings only; no independent complete code/data classification. Byte-mismatching rows excluded, overlapping ranges deduplicated.'})
r={'components':result,'receipts':receipts,'candidate_inventory':inventory,'selected_original_candidates':len(selected),'methodology':'Only existing original-labelled ARM listings and original bootloader startup disassembly; serialized byte fields checked directly against authenticated locked flash images and mapped to payload offsets. Public/native/generated assembly and full linear audit dumps excluded. This is a bounded artifact measure, not a whole-firmware executable denominator.'}
(OUT/'EXISTING-ARM-LISTING-VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'selected_candidates':len(selected),'all_assembly_candidates':len(inventory),'components':[{k:v for k,v in x.items() if k not in ['files','payload_ranges']} for x in result]},indent=2))

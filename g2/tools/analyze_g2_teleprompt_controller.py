#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/teleprompt/teleprompt.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-teleprompt-controller-function-map.tsv';PM=ROOT/'tools/manifests/g2-teleprompt-controller-provider-map.tsv';CL=ROOT/'tools/manifests/g2-teleprompt-controller-closure.tsv'
PINS={FM:'8f32be71baf778b418ea271d0d4163bbccb182319f703faee4cc505b3a97d7ca',PM:'7c0a869229295625a284819a4a5d4a9308ade5648cbbdaa446254764619ca4db',CL:'d84dfd593276db9d23ce5eda601b3b19f47b829b9eea2ff265767842cd4a987e'}
PHYS=(0x5899A4,0x58A8E0);PSEUDO=(0x57F460,0x589BC4,0x57F45E);EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x43C0E4,0x47CC60};LVGL={0x441488};CMSIS={0x4490CC,0x44971C,0x4497B6,0x44981C};NANOPB={0x48EB32};FIRST={0x4434D0,0x45A568,0x464BB2,0x478110,0x478252,0x54F50E,0x5540B2,0x5540D6,0x554170,0x55448E,0x55462E,0x55468C,0x555178,0x556AD4,0x556B00,0x5885B4,0x588792,0x58887A,0x58922C,0x58B370,0x58BD74,0x58C89E}
def sh(x):return hashlib.sha256(x).hexdigest()
def provenance():
 if json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24':raise c.AuditError('EasyLogger changed')
 if json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa':raise c.AuditError('LVGL changed')
 if json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53':raise c.AuditError('CMSIS changed')
 if json.loads((ROOT/'third_party/nanopb/PROVENANCE.json').read_text())['upstream']['selected_commit']!='98bf4db69897b53434f3d0ba72e0a3ab1a902824':raise c.AuditError('nanopb changed')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError('manifest changed')
 provenance()
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};inter=set();ins={};calls=[];ind=[];body=b''
 if len(F)!=10 or sum(r['source_path_anchor']=='yes' for r in rows)!=7:raise c.AuditError('inventory changed')
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if sh(raw)!=r['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('body changed')
  body+=raw;ins.update(ii);calls+=cc;ind+=dd;inter.update(range(a+2,z,2))
 calls.sort();ind.sort()
 if len(body)!=2408 or sh(body)!='6de1ef6df7bc2b7e690264c7a6f56a9a7809beeaad1bcb2b7b34fb9c96ee4280' or len(ins)!=904 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='877d350b2415d45f1b16ed1029be0a4d62b4a6cdc24c65efb247624582767239' or ind:raise c.AuditError('instruction closure changed')
 non=c._slice(b,0x58A30C,0x58A8E0)
 if len(non)!=1492 or sh(non)!='21dd508ad316f4a295d66611a263e487a2a760261bd19bd12f651fae4a076559' or sh(c._slice(b,*PHYS))!='242a4ad8b266f47bc3337a7e61d99ee60ae2e86d63041dfe39e38d500d045b65':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='51964f3accb9784ccdefb3d7c0cea4dd79d731ef8145ef64a2ac7733e93142d9' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='59e4e8b251be1766cee0f8d48d9a2065c789d0bc02594e9107b1c53dd96ac05c':raise c.AuditError('boundary changed')
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,LVGL,CMSIS,NANOPB,FIRST)
 if len(calls)!=162 or sum(y in starts for x,y in calls)!=13 or c._pair_digest(calls)!='48aef082bd9f64d8dff006dcbd0a041c90f08dd4101cd6d1e12f7fe121e91016' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(90,4,2,7,3,43):raise c.AuditError('call closure changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=37 or c._pair_digest(entries)!='949a1932cc99591595b20e7769b154b657546e66cefef68062f56cb15e0247cd' or strict!=[(PSEUDO[0],PSEUDO[1])]:raise c.AuditError('BL ingress changed')
 D=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);i=next(D.disasm(c._slice(b,PSEUDO[2],PSEUDO[2]+4),PSEUDO[2]),None)
 if i is None or i.size!=4 or i.mnemonic!='mul' or PSEUDO[0]!=PSEUDO[2]+2:raise c.AuditError('pseudo BL changed')
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};stored=[(a,v) for a,v in words if v in enc];interior=[(a,v) for a,v in words if (v&1) and (v&~1) in inter]
 if len(stored)!=3 or c._pair_digest(stored)!='f15c61dae790b91c368a9f6205d247ea446c8545d6678967447dfbb7444039ce' or interior:raise c.AuditError('stored ingress changed')
 pairs=[(0x58A31C,x) for x in t.literal_references(b,0x58A31C)]
 if len(pairs)!=18 or c._pair_digest(pairs)!='2ae8786de7f7b9b3b0f40c88002ab96aed843adfa572597c763b69667a500afc':raise c.AuditError('path refs changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
 if any('teleprompt.c' in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError('unimplemented object routed')
 return {'schema_version':1,'identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'app\gui\teleprompt\teleprompt.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':10,'ghidra_discovered_functions':8,'restored_functions':2,'path_anchored_functions':7,'body_bytes':2408,'physical_bytes':3900,'noncode_bytes':1492,'reachable_instructions':904,'direct_body_calls':162,'internal_direct_body_calls':13,'external_direct_body_calls':149,'indirect_body_calls':0,'direct_bl_entry_sites':37,'stored_function_entry_pointers':3,'raw_overlapping_pseudo_bl_sites':1,'strict_interior_ingress':0},'provider_boundary':{'easylogger_calls':90,'iar_runtime_calls':4,'lvgl_calls':2,'cmsis_freertos_calls':7,'nanopb_calls':3,'first_party_calls':43,'historical_teleprompt_commit':None,'new_version_discriminator':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))

#!/usr/bin/env python3
"""Fail-closed object/provider audit for service_ancc.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-service-ancc-function-map.tsv";PM=ROOT/"tools/manifests/g2-service-ancc-provider-map.tsv";CL=ROOT/"tools/manifests/g2-service-ancc-closure.tsv"
PINS={FM:"0705fa841980cf7b879858e22e274d3c2600911801c85481aec8c8ece881c626",PM:"1e94dcebcd804f1c1a31b3737f153be79e32839d8c8b81360dbe5ecbe1fbfae0",CL:"d9b92c36703ff859b9c91081974392c9ccb08ee6eb0f4134cca4d96d44c6007d"}
F=((0x49729C,0x4972A2),(0x4972A2,0x4972AA),(0x4972AA,0x4972B2),(0x4972B2,0x4972BA),(0x4972BA,0x4972C2),(0x4972C2,0x49739E),(0x4974D4,0x49758E),(0x49758E,0x497696),(0x497696,0x497826),(0x497826,0x497938),(0x497960,0x497CEA),(0x497CF0,0x497D24));PHYS=(0x49729C,0x497DE6);PATH_ADDR=0x6E9A9C;PATH_CELLS=(0x497944,0x497D74)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x44971C,0x4497B6,0x44981C};IAR={0x439BE4,0x43C0E4,0x44A43C};FIRST={0x443484,0x4434B4,0x4434D0,0x45A568,0x464B2E,0x464BB2,0x464F76,0x467F08,0x46C630,0x4E1A48,0x4E1AF8,0x4E1B28}
PSEUDO=[(0x48E258,0x49739E),(0x497DB6,0x497DC0),(0x497DBA,0x497DDC),(0x4E2898,0x4973F4),(0x4E2CCA,0x497DB4),(0x5850CE,0x4973F4)];STORED=[(0x4933BF,0x497BD5),(0x52C3B6,0x497D01),(0x56C338,0x497B29)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());ancc=json.loads((ROOT/"third_party/ambiqsuite-ancc-profile/PROVENANCE.json").read_text())
 if easy['upstream']['selected_commit']!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or cms['upstreams']['cmsis_freertos']['selected_commit']!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or ancc['upstream']['selected_commit']!="de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f":raise c.AuditError("provider provenance changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=12 or sum(r['path_anchored']=='yes' for r in rows)!=6:raise c.AuditError("function inventory changed")
 starts={a for a,z in F};ins={};calls=[];ind=[];body=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if (int(r['stock_start'],0),int(r['stock_end_exclusive'],0))!=(a,z) or len(raw)!=int(r['interval_bytes']) or sh(raw)!=r['interval_sha256'] or c._uncovered((a,z),ii):raise c.AuditError("function closure changed")
  if set(ins)&set(ii):raise c.AuditError("overlap")
  ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort()
 if len(body)!=2340 or sh(body)!="06d77b4c20cd5b2486b779734d5256cf157c7304fee0b6069e72df2b7b0e90c7" or len(ins)!=875 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="44626c1619a25a5c8af8739dde44003278019e741127eb264e7229603dcdf7c5" or ind:raise c.AuditError("body closure changed")
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=550 or sh(non)!="2782cb030f8625f29424421b3e898544f36d32d75b6e4240824d5972141a06f8" or sh(c._slice(b,*PHYS))!="907bbcdf21e9d1573866e2c0bc3aeb10af18bc76beac9aa4c6535d1512167bbc":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="e56e02da6ea2921497c57a64aea60f9f2b27de783ef86fa320170fcd6032a60c" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="83ad549a8d0942ce589b5dcfe4dfc5e217c716729143dc7932c7a89cef3ccb34":raise c.AuditError("boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,CMSIS,IAR,FIRST)
 if len(calls)!=131 or sum(y in starts for x,y in calls)!=2 or c._pair_digest(calls)!="dc670762a0b57914f183bb04975aa11333117411646a13121ad50b7f204a4024" or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(85,17,10,17):raise c.AuditError("provider closure changed")
 entries=[];strict=[];noncode=[];instruction_entries=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in instruction_entries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode.append((a,y))
 if len(entries)!=31 or c._pair_digest(entries)!="e06fe0b2ae076b17846b3cc2916b957b04659838d38d701ebc039c033e948bf0" or strict or noncode!=PSEUDO:raise c.AuditError("ingress changed")
 found=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0]
  if (v&1) and (v&~1) in instruction_entries:found.append((c.BASE+o,v))
 if found!=STORED:raise c.AuditError("stored callbacks changed")
 if cstring(b,PATH_ADDR)!=r"D:\01_workspace\s200_ap510b_iar_git\platform\service\message_notify\service_ancc.c":raise c.AuditError("path changed")
 refs=sorted((cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell))
 if len(refs)!=19 or c._pair_digest(refs)!="1bf1657915a509dc9b2069552d80a01e31c185d3ade79c3b3b98aad24ac6e3e2":raise c.AuditError("path refs changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("service_ancc.c" in x.get('path','').lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"platform\service\message_notify\service_ancc.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":12,"ghidra_discovered_functions":12,"path_anchored_functions":6,"restored_non_anchor_functions":6,"body_bytes":2340,"physical_bytes":2890,"outer_pool_bytes":550,"reachable_instructions":875,"direct_body_calls":131,"internal_direct_body_calls":2,"external_direct_body_calls":129,"indirect_body_calls":0,"direct_bl_entry_sites":31,"stored_interior_callback_pointers":3,"strict_interior_ingress":0,"raw_noncode_pseudo_bl":6},"behavior":{"fixed_record_count":10,"record_bytes":0x304,"mutex_protected":True,"message_count_callbacks":True,"role_display_sync_policy":True},"provider_boundary":{"easylogger_calls":85,"cmsis_freertos_mutex_calls":17,"iar_dlib_calls":10,"closed_first_party_calls":17,"direct_ambiqsuite_ancc_calls":0,"embedded_ambiqsuite_ancc_definitions":0,"cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","ambiqsuite_ancc_selected_commit":"de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f"},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))

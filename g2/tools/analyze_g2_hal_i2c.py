#!/usr/bin/env python3
"""Fail-closed raw-image object/provider audit for hal_i2c.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-hal-i2c-function-map.tsv";CL=ROOT/"tools/manifests/g2-hal-i2c-closure.tsv";PM=ROOT/"tools/manifests/g2-hal-i2c-provider-map.tsv"
PINS={FM:"609e67779eee297fdd433eb9e22580dd1364993daec40ec0603bb59f4eefae01",CL:"bb7fc8d010bb94e0337971e2f7ad95cf15a4e3803e97dc5ebfc76fba5927e867",PM:"d34446b158c37395008a16781e89b6c2a304f1c36e61d6c0c666e9b52cb7becb"};F=((0x50412C,0x50414A),(0x50414A,0x5041C6),(0x5041C6,0x50423A),(0x50423A,0x50436E),(0x50436E,0x504488),(0x504488,0x5044B4),(0x5044B4,0x5045C0),(0x5045C0,0x50468E),(0x50468E,0x50475C));PHYS=(0x50412C,0x504784);POOL=(0x50475C,0x504784)
EASY={0x43CE9E,0x43D0CE,0x43D574};CMSIS={0x44971C,0x4497B6,0x44981C,0x44989A};IAR={0x439BE4,0x43C0E4};NANOPB={0x48949C};DELAY={0x4910F4};AMBIQ={0x480F0C,0x55C2BC,0x55C32E,0x55C498,0x55C4D0,0x55C518,0x55C558,0x55C7E8,0x55CA94,0x55CC1C};STORED=[(0x438068,0x504488)]
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 amb=json.loads((ROOT/"third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());nano=json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text())
 if amb["upstream"]["selected_commit"]!="5efc0228528a8adce5eae0d226fac85d2551eb3b" or cms["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or nano["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824":raise c.AuditError("provider selection changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=9:raise c.AuditError("function inventory changed")
 starts=set();interiors=set();body=b"";ins={};calls=[];ind=[];anch=0
 for row,bounds in zip(rows,F):
  a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(b,a,z)
  if (a,z)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]:raise c.AuditError("body changed")
  ii,cc,dd=d._recover_function(b,a,z)
  if c._uncovered(bounds,ii):raise c.AuditError("uncovered body")
  starts.add(a);interiors.update(range(a+2,z,2));body+=raw;ins.update(ii);calls+=cc;ind+=dd;anch+=row["source_path_anchor"]=="yes"
 calls.sort();code=b"".join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if anch!=1 or len(body)!=1584 or sh(body)!="6f9a3c1699144e9395ca13118e76654195e533109354d79957b5be4277639d21" or code!=body or len(ins)!=639 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="2be72cabb31305979a256af25bfa28f3cc207ce9307465fc5b6ac7d77ff87e28" or ind:raise c.AuditError("instruction closure changed")
 if sh(c._slice(b,*PHYS))!="b3ce16cc70dc0e086a14365d8c72705ce278ddcc983345645eea538cef8290ed" or sh(c._slice(b,*POOL))!="66f83bb5a9fc3deb303054c063c1b9ac6777cb141f1f52b0bbea245e5ffb9b8f":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x5040D0,PHYS[0]))!="ecf8d4eb0cdfe30680b13fb9d24d6ff71796eb334de386928eee9b01e36277f0" or sh(c._slice(b,PHYS[1],0x50478C))!="0b4c6e5fb38456bd9cb7671776a8d557c1c36c8af9b2400c791e3f74e2ae25e5":raise c.AuditError("boundary changed")
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,CMSIS,IAR,NANOPB,DELAY,AMBIQ)
 if len(calls)!=65 or sum(y in starts for _,y in calls)!=15 or c._pair_digest(calls)!="b8876ff289773233655c6a3f09b69d167e4c9b8e743e0e9d68315b0213279523" or set(ext)!=set().union(*providers):raise c.AuditError("call topology changed")
 if tuple(sum(ext[x] for x in group) for group in providers)!=(5,15,3,4,2,21):raise c.AuditError("provider accounting changed")
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in interiors:strict.append((a,y))
 if len(entries)!=35 or c._pair_digest(entries)!="d307d2987cc40d8cb9f595d4181b8a5b7387862913a2466116ef5d592a7fbdcf" or strict:raise c.AuditError("BL entry topology changed")
 stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0];target=v&~1
  if v&1 and target in starts:stored.append((c.BASE+off,target))
 if stored!=STORED or c._pair_digest(stored)!="9256a4e77411ced721e1c04fecfcb415c4e4832b3a0d671db18c9f678c441072":raise c.AuditError("stored entry topology changed")
 if t.literal_references(b,0x504778)!=[0x50433C]:raise c.AuditError("path references changed")
 return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":9,"ghidra_discovered_functions":9,"path_anchored_functions":1,"body_bytes":1584,"physical_bytes":1624,"outer_pool_bytes":40,"direct_body_calls":65,"internal_direct_body_calls":15,"external_direct_body_calls":50,"indirect_body_calls":0,"direct_bl_entry_sites":35,"stored_entry_pointers":1},"provider_boundary":{"ambiqsuite_calls":21,"cmsis_freertos_calls":15,"easylogger_calls":5,"nanopb_calls":4,"iar_dlib_calls":3,"first_party_delay_calls":2,"ambiqsuite_commit":"5efc0228528a8adce5eae0d226fac85d2551eb3b","new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))

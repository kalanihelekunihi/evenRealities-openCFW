#!/usr/bin/env python3
"""Fail-closed object and provider audit for navigation_data_handler.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM=ROOT/"tools/manifests/g2-navigation-data-handler-function-map.tsv";PM=ROOT/"tools/manifests/g2-navigation-data-handler-provider-map.tsv";CL=ROOT/"tools/manifests/g2-navigation-data-handler-closure.tsv"
PINS={FM:"f253eb83bccf378eda38fb4b5d7edb0abf9ecc1020a6a85822c36789b48766c2",PM:"7ed5098482b4b4b35341331a5593ed71025e2f12d9a06197453a6e1a9dab0d24",CL:"2d8271ebf484e6a166fca5cd432e76cd8361fe703da0d57ebc8efc6b8774277e"}
PHYS=(0x586448,0x5885B4);PATH_ADDR=0x6E8B84;PATH_CELLS=(0x586F0C,0x5872DC,0x58801C,0x58836C)
INLINE_POOLS=[(0x588012,0x58803C),(0x5881AE,0x5881C4)]
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439BE4,0x439C04,0x43C0E4,0x44A43C,0x46CACC};NANOPB={0x48EB32,0x48F49C,0x490120,0x4905F4,0x490C32};CMSIS={0x4497B6,0x44981C};HEAP={0x474CD2,0x474D16};FIRST={0x443484,0x4434D0,0x45A570,0x45AACA,0x464B2E,0x464BB2,0x475B14,0x475C1A,0x498680,0x585CA4}
RAW_PSEUDO=[(0x50566C,0x5877CA),(0x57FB58,0x5872BC)];UNALIGNED_PSEUDO=[(0x455225,0x5879F1),(0x597A65,0x586851)]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstring(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError("unterminated string")
 return b[o:e].decode('ascii')
def provenance():
 easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text());np=json.loads((ROOT/"third_party/nanopb/PROVENANCE.json").read_text());cms=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text());ker=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text())
 if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or np["upstream"]["selected_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824" or cms["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53" or ker["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c":raise c.AuditError("provider provenance changed")
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 provenance()
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=22 or sum(r['source_path_anchor']=='yes' for r in rows)!=7 or sum(r['provenance']=='Ghidra-discovered' for r in rows)!=21:raise c.AuditError("inventory changed")
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows];starts={a for a,z in F};ins={};calls=[];ind=[];interval=b''
 for r,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z);uncovered=c._uncovered((a,z),ii)
  if len(raw)!=int(r['interval_bytes']) or sh(raw)!=r['interval_sha256']:raise c.AuditError("function interval changed")
  if uncovered!=(INLINE_POOLS if a==0x5872F4 else []):raise c.AuditError("instruction/pool partition changed")
  if set(ins)&set(ii):raise c.AuditError("overlapping functions")
  ins.update(ii);calls+=cc;ind+=dd;interval+=raw
 calls.sort();ind.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(interval)!=8140 or sh(interval)!="9e551e069ffcc226d67e111d1e0927f8073f5f6a0604ee6c3980a268997a6b9f" or len(code)!=8076 or sh(code)!="e9aa79516be87a716b01e5f353bd56f929d900ca3222bab1b5fd057cc7246ab8":raise c.AuditError("body closure changed")
 if len(ins)!=2926 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="b361206bc7f38573b2841093a1a9406371b7ebe15765438201b437633adcbce0" or ind:raise c.AuditError("instruction closure changed")
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=480 or sh(non)!="6bc6205f75f08bdcaf40bdd61960cddd417de492328c093512aa57d2f10d032b" or sh(c._slice(b,*PHYS))!="e777cb856d03a44cf7d430280fa989b659825921baf432da227a614a83318912":raise c.AuditError("physical closure changed")
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!="d2e3707b84510eac61eb31e302112e65a74eb37a2e0969d664a82020e058f7f5" or sh(c._slice(b,PHYS[1],PHYS[1]+16))!="b59c07d5f3db89e27a88d7193073f647d9e9333d156b833381fc1e83374b1523":raise c.AuditError("object boundary changed")
 ext=Counter(y for x,y in calls if y not in starts);providers=(EASY,IAR,NANOPB,CMSIS,HEAP,FIRST)
 if len(calls)!=435 or sum(y in starts for x,y in calls)!=12 or c._pair_digest(calls)!="b51e9e900b78b9838e35b878f8d8398ef9a054e332b6e0126eb77a285546a053" or set(ext)!=set().union(*providers):raise c.AuditError("call closure changed")
 if tuple(sum(ext[x] for x in s) for s in providers)!=(165,94,37,9,49,69):raise c.AuditError("provider accounting changed")
 instruction_entries=set(ins)-starts;entries=[];strict=[];noncode=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in instruction_entries:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:noncode.append((a,y))
 if len(entries)!=45 or c._pair_digest(entries)!="307d0588efb5cdb70626ed122ec7fc324ff6ece376d87478e8d66e90b00d6480" or strict!=RAW_PSEUDO[:1] or noncode!=RAW_PSEUDO[1:]:raise c.AuditError("raw BL ingress changed")
 dec=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS)
 pseudo=[list(dec.disasm(c._slice(b,a,a+4),a,count=1))[0].mnemonic for a in (0x50566A,0x57FB56)]
 if pseudo!=['sxtab','mul']:raise c.AuditError("pseudo-BL classification changed")
 words=[(c.BASE+o,struct.unpack_from('<I',b,o)[0]) for o in range(len(b)-3)];enc=starts|{a|1 for a in starts};interior=set(ins)-starts
 if [(a,v) for a,v in words if v in enc] or [(a,v) for a,v in words if (v&1) and (v&~1) in interior]!=UNALIGNED_PSEUDO:raise c.AuditError("stored pointer closure changed")
 if cstring(b,PATH_ADDR)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_data_handler.c":raise c.AuditError("retained path changed")
 pairs=[(cell,x) for cell in PATH_CELLS for x in t.literal_references(b,cell)]
 if len(pairs)!=33 or c._pair_digest(pairs)!="5e70cb2812cf53f62cb75c391dd7ec215c00498e2b4e670c58c6ac3e5ce3d301":raise c.AuditError("path references changed")
 overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
 if any("navigation_data_handler" in x.get("path","").lower() for x in overlay['sources']):raise c.AuditError("unimplemented object routed")
 return {"schema_version":1,"identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\navigation\navigation_data_handler.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":22,"ghidra_discovered_functions":21,"restored_functions":1,"path_anchored_functions":7,"function_interval_bytes":8140,"body_bytes":8076,"physical_bytes":8556,"noncode_bytes":480,"inline_literal_pool_bytes":64,"reachable_instructions":2926,"direct_body_calls":435,"internal_direct_body_calls":12,"external_direct_body_calls":423,"indirect_body_calls":0,"direct_bl_entry_sites":45,"stored_function_entry_pointers":0,"raw_overlapping_pseudo_bl_sites":2,"unaligned_word_pseudo_pointers":2,"strict_interior_ingress":0},"behavior":{"protobuf_navigation_record_construction":True,"navigation_data_dispatch":True,"role_sensitive_notification":True,"navigation_icon_mapping":True,"named_resource_lookup_and_apply":True},"provider_boundary":{"easylogger_calls":165,"iar_dlib_calls":94,"nanopb_calls":37,"cmsis_freertos_calls":9,"source_owned_heap_calls":49,"first_party_calls":69,"easylogger_commit":"a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24","nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","freertos_kernel_commit":"def7d2df2b0506d3d249334974f51e427c17a41c","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))

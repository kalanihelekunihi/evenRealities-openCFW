#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for page_manager.c."""
import csv,hashlib,json,struct,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from analyze_g2_thread_ble_production import wide_branch_target
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-page-manager-function-map.tsv';PM=ROOT/'tools/manifests/g2-page-manager-provider-map.tsv';CL=ROOT/'tools/manifests/g2-page-manager-closure.tsv'
PINS={FM:'5e3b97904f73fc4adb3f418894a7f0f06e4184ec505638a8cf24e752f9cbf954',PM:'a073d80f49479baae39cde7f23065dcff99f32353f8ce3684800010a26ed1a87',CL:'8b2a236655ecb74d7c3b27d48c2cd15e4ec1e0aebce44d65a50d6b034159313e'}
PHYS=(0x45EC7C,0x45FEAC);PATH=0x6F4F38;CELLS=(0x45F684,0x45FE94)
EASY={0x43CE9E,0x43D0CE,0x43D574};IAR={0x439C04,0x43C0E4,0x44B0AE};HEAP={0x474CD2,0x474D16};CLOSED={0x44228A,0x45BBB6,0x45BBD2}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43F0E0,0x43F142,0x43F4C0,0x43F66C,0x43FC70,0x43FCE0,0x43FD9E,0x43FDDA,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x44131C,0x44133A,0x441378,0x441386,0x441394,0x4413A2,0x4413B0,0x44146A,0x441488,0x44D7B8,0x44D94C,0x44DCA2,0x44FA1A,0x44FE0E,0x450286,0x4503D6,0x450408,0x450500,0x4506CE,0x451670,0x451740,0x451862,0x487022,0x488290}
STORED=[(0x45F690,0x45ECBE),(0x45F694,0x45ED4E),(0x45F698,0x45EE34),(0x45F69C,0x45ECCA),(0x45F6A0,0x45ED90),(0x45F6A4,0x45ECAE),(0x45FA74,0x45ECB6)]
RAW=[(0x4418A8,0x45F994),(0x4418B4,0x45F884),(0x555042,0x45F880),(0x55509A,0x45F880),(0x555102,0x45F880),(0x591462,0x45F88C),(0x591570,0x45F89C),(0x5E954C,0x45F88C),(0x5E9554,0x45F88C),(0x5E9560,0x45F89C),(0x5E9794,0x45F89C),(0x5E9830,0x45F89C),(0x643077,0x45ECFE)]
IND=[0x45ECF2,0x45ED76,0x45EE0E,0x45EE22,0x45EEFE,0x45EF12,0x45F1FC,0x45F482,0x45F5E6,0x45FA38,0x45FA52,0x45FA6E]
def sh(x):return hashlib.sha256(x).hexdigest()
def cstr(b,a):
 o=a-c.BASE;e=b.find(b'\0',o)
 if o<0 or e<0:raise c.AuditError('unterminated string')
 return b[o:e].decode('ascii')
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text());lvgl=json.loads((ROOT/'third_party/lvgl/PROVENANCE.json').read_text())
 if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or lvgl['upstream']['selected_commit']!='344c7c318047b7348e1be8572a9fd4260c251cfa' or 'deff9ab509341f264addbd3c8ada533678591905' not in (ROOT/'third_party/tlsf/README.openCFW.md').read_text():raise c.AuditError('provider provenance changed')
 if 'physical_interval\t[0x0045A578,0x0045EC7C)' not in (ROOT/'tools/manifests/g2-sync-framework-closure.tsv').read_text():raise c.AuditError('preceding sync-framework boundary regressed')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 F=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
 if len(F)!=45 or sum(r['source_path_anchor']=='yes' for r in rows)!=3 or sum(r['ghidra_discovered']=='yes' for r in rows)!=36:raise c.AuditError('function inventory changed')
 starts={a for a,_ in F};ins={};calls=[];ind=[];body=b''
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii,cc,dd=q._recover_function(b,a,z)
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or c._uncovered((a,z),ii):raise c.AuditError('function body changed')
  ins.update(ii);calls+=cc;ind+=dd;body+=raw
 calls.sort();code=b''.join(c._slice(b,a,a+i.size) for a,i in sorted(ins.items()))
 if len(body)!=4510 or sh(body)!='964a88ac7da964bb23c197bf7b849684183d2774716ffa0ea25c1a8a87bb3402' or code!=body or len(ins)!=1925 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='5718ec385e62a97a5f34062b3774bf0531629fb97c233f1be22f8f0985e52c1a' or sorted(ind)!=IND:raise c.AuditError('instruction closure changed')
 covered=set()
 for a,i in ins.items():covered.update(range(a,a+i.size))
 non=bytes(v for a,v in zip(range(PHYS[0],PHYS[1]),c._slice(b,*PHYS)) if a not in covered)
 if len(non)!=146 or sh(non)!='47ffb1138d753d2694c70c9034f67992a50ea3e8206bdb2d3bf63c834ecb5ab4' or sh(c._slice(b,*PHYS))!='93a1da621e2cfd10269342cb8859e8975bc543e25c4abf0c9cb3651ed314d538':raise c.AuditError('physical closure changed')
 if sh(c._slice(b,PHYS[0]-16,PHYS[0]))!='56fe93d1a7740a56fa731fd3d5efef237b630a464579949592913915c6d5efb1' or sh(c._slice(b,PHYS[1],PHYS[1]+16))!='6669b5e8ebf638a8dab4ccd24bdcf9d8cc12161d08e90b3f92eea21c2564d627':raise c.AuditError('object boundary changed')
 ext=Counter(y for _,y in calls if y not in starts);providers=(EASY,LVGL,HEAP,CLOSED,IAR)
 if len(calls)!=199 or sum(y in starts for _,y in calls)!=60 or c._pair_digest(calls)!='b1edf988dc5ef8863bfcc0aac406f227b59160a3f069d66215c65cb7ba1f4418' or set(ext)!=set().union(*providers) or tuple(sum(ext[x] for x in s) for s in providers)!=(27,96,5,7,4):raise c.AuditError('provider closure changed')
 entries=[];strict=[];non_bl=[];wide=[];wstrict=[];inter_i=set(ins)-starts
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter_i:strict.append((a,y))
  elif y is not None and PHYS[0]<=y<PHYS[1]:non_bl.append((a,y))
  x,z=struct.unpack('<HH',c._slice(b,a,a+4));y=wide_branch_target(a,x,z)
  if y in starts:wide.append((a,y))
  elif y in inter_i:wstrict.append((a,y))
 if len(entries)!=112 or c._pair_digest(entries)!='7b2e999fb9bc4809cee2fa6897e401d22eb66007983338df18fb802ab1a32ade' or strict or non_bl or wide or wstrict:raise c.AuditError('branch ingress changed')
 stored=[];raw_p=[]
 for off in range(len(b)-3):
  v=struct.unpack_from('<I',b,off)[0]
  if v&1 and (v&~1) in starts:stored.append((c.BASE+off,v&~1))
  elif v&1 and (v&~1) in inter_i:raw_p.append((c.BASE+off,v&~1))
 if stored!=STORED or c._pair_digest(stored)!='cb23d22641eb0217358ecb1466f5ea448d2dcdf31e7326934a8d70bd6dfa4b37' or raw_p!=RAW or c._pair_digest(raw_p)!='d4c5d9361564a588329af188aa8c7bb08a21fd644f6b703c4ba619e0bb30d785':raise c.AuditError('stored ingress changed')
 expected=r'D:\01_workspace\s200_ap510b_iar_git\framework\page_manager\page_manager.c'
 if cstr(b,PATH)!=expected or any(struct.unpack('<I',c._slice(b,x,x+4))[0]!=PATH for x in CELLS):raise c.AuditError('retained path changed')
 refs=sorted((x,y) for x in CELLS for y in t.literal_references(b,x))
 if len(refs)!=7 or c._pair_digest(refs)!='e1772cc65c5b75a8f86876af8df80a156b8e25eaeff6fbbf338eca82423c2d75':raise c.AuditError('path references changed')
 routed=any('page_manager' in x.get('path','').lower() for x in json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())['sources'])
 if routed:raise c.AuditError('unimplemented page manager entered production overlay')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure; corpus-independent','identity':{'image_sha256':c.IMAGE_SHA256,'retained_path':r'framework\page_manager\page_manager.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':45,'ghidra_discovered_functions':36,'restored_functions':9,'path_anchored_functions':3,'raw_path_references':7,'body_bytes':4510,'physical_bytes':4656,'noncode_bytes':146,'reachable_instructions':1925,'direct_body_calls':199,'internal_direct_body_calls':60,'external_direct_body_calls':139,'indirect_body_calls':12,'bounded_indirect_body_calls':12,'direct_bl_entry_sites':112,'stored_entry_pointers':7,'raw_interior_word_collisions':13,'strict_interior_ingress':0},'behavior':{'page_registration_tables':True,'page_stack_and_state_getters':True,'lvgl_backed_page_transitions':True,'kernel_wrapped_page_locking':True},'provider_boundary':{'easylogger_calls':27,'lvgl_calls':96,'source_owned_heap_wrapper_calls':5,'closed_first_party_calls':7,'iar_dlib_calls':4,'easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','tlsf_commit':'deff9ab509341f264addbd3c8ada533678591905','historical_page_manager_commit':None,'new_version_discriminator':False,'private_generating_commit_recoverable':False},'production':{'production_routed':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))

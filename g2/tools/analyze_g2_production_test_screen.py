#!/usr/bin/env python3
"""Fail-closed linked-object audit for the G2 generic production-test screen."""
from __future__ import annotations
import csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BASE=0x437FE0
IMAGE_SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';FM=ROOT/'tools/manifests/g2-production-test-screen-function-map.tsv';CLOSURE=ROOT/'tools/manifests/g2-production-test-screen-closure.tsv'
PINS={FM:'12b58892f1f3d950204bbec61f3a2e477ba50f2ae455d4504890ebe63c1abcb3',CLOSURE:'923e8412ee9dfca08cc9475290feb5485dcc15bd1a88864b4f45bc80725d1fdc'}
PHYS=(0x5CF7A8,0x5CF8E4);PHYS_SHA='93ffdf985efdeae31d82e22ab419652833f94ab3692d162f34534ab84afbb1bb';BODY_SHA='0b94d5465cc85f336d3f2a57079e2dd3f2fe9f8cc1db9292be575b2db2ca9c9e';POOL=(0x5CF8C8,0x5CF8E4);POOL_SHA='1880fd5bd60cb1b80b7e4f8cc18ed54280611c09a0c9bd81ff06cd82b4ad980d';DESC=(0x6A45E0,0x6A45F0);DESC_SHA='f00a33eac72fa423435d2995efba89dbfb3a92f6b2ff726d6f46dec7e8ed624c';CALL_SHA='7d7f9db0822842b940c7387b1742c90747de3058d781fe2a9591f002b3bfebc4';RAW_SHA='e8f67daf551b694577dabef7eb380b9938d8809b557f4f682f448a76affbf15a';STORED_SHA='7dc860ccfb4d024218dd969ea788c72b2afed50f78d6b7fe805b819ff2f50ca6'
PATH=0x6EEE68;RETAINED=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\ProductionTest\production_test.c';WORDS={0x5CF8C8:0x758160,0x5CF8CC:0x75813C,0x5CF8D0:PATH,0x5CF8D4:0x787F90,0x5CF8D8:0x72BEFC,0x5CF8DC:0x20074894,0x5CF8E0:0x200030A0,0x6A45E0:0x10B,0x6A45E4:0x5CF7A9,0x6A45E8:0x5CF7F3,0x6A45EC:0x200030A0,0x793748:0x5CF7EF};STRINGS={PATH:RETAINED,0x758160:'ProductionTest recv data len = %d',0x75813C:'ProductionTest_common_data_handler',0x787F90:'production_test',0x72BEFC:'[production_test]ProductionTest recv data len = %d'};STORED=[(0x6A45E4,0x5CF7A9),(0x6A45E8,0x5CF7F3),(0x793748,0x5CF7EF)]
class AuditError(RuntimeError):pass
def sha(x):return hashlib.sha256(x).hexdigest()
def sl(b,a,z):return b[a-BASE:z-BASE]
def pd(xs):return sha(b''.join(struct.pack('<II',*x) for x in xs))
def cstr(b,a):
 o=a-BASE;e=b.find(b'\0',o)
 if e<0:raise AuditError('unterminated string')
 return b[o:e].decode('ascii')
def bw(b,a):
 f,s=struct.unpack_from('<HH',b,a-BASE)
 if f&0xf800!=0xf000 or s&0xd000!=0x9000:return None
 S=(f>>10)&1;j1=(s>>13)&1;j2=(s>>11)&1;i1=(~(j1^S))&1;i2=(~(j2^S))&1;imm=(S<<24)|(i1<<23)|(i2<<22)|((f&0x3ff)<<12)|((s&0x7ff)<<1)
 if imm&(1<<24):imm-=1<<25
 return a+4+imm
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=3523396 or sha(b)!=IMAGE_SHA:raise AuditError('official image changed')
 for p,h in PINS.items():
  if sha(p.read_bytes())!=h:raise AuditError(f'pinned input changed: {p.name}')
 with FM.open(newline='') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 starts=set();inside=set();iv=[];bodies=[]
 for r in rows:
  a=int(r['stock_start'],0);z=int(r['stock_end_exclusive'],0);x=sl(b,a,z)
  if len(x)!=int(r['stock_bytes']) or sha(x)!=r['stock_sha256']:raise AuditError('body changed')
  starts.add(a);inside.update(range(a+2,z,2));iv.append((a,z));bodies.append(x)
 if len(rows)!=3 or sum(map(len,bodies))!=286 or sha(b''.join(bodies))!=BODY_SHA:raise AuditError('inventory changed')
 if sha(sl(b,*PHYS))!=PHYS_SHA or sha(sl(b,*POOL))!=POOL_SHA or sha(sl(b,*DESC))!=DESC_SHA:raise AuditError('physical boundary changed')
 if sha(sl(b,0x5CF8E4,0x5CF938))!='068e1f402040f5ae9e1e397160147c42acacb0c75d7a4441a2fe19806004dde4':raise AuditError('following parser changed')
 for a,v in WORDS.items():
  if struct.unpack('<I',sl(b,a,a+4))[0]!=v:raise AuditError(f'word changed at {a:#x}')
 for a,v in STRINGS.items():
  if cstr(b,a)!=v:raise AuditError(f'string changed at {a:#x}')
 needle=struct.pack('<I',PATH);hits=[];q=b.find(needle)
 while q>=0:hits.append(BASE+q);q=b.find(needle,q+1)
 if hits!=[0x5CF8D0]:raise AuditError('path pointer topology changed')
 sys.path.insert(0,str(ROOT/'tools'));import recover_apollo_embedded_source_paths as d
 entry=[];inter=[];eb=[];ib=[]
 for o in range(0,len(b)-3,2):
  a=BASE+o;t=d._thumb_bl_target(b,a)
  if t in starts:entry.append((a,t))
  elif t in inside:inter.append((a,t))
  t=bw(b,a)
  if t in starts:eb.append((a,t))
  elif t in inside:ib.append((a,t))
 if entry or inter or eb or ib:raise AuditError('direct ingress changed')
 calls=[]
 for a,z in iv:
  for q in range(a,z-3,2):
   t=d._thumb_bl_target(b,q)
   if t is not None:calls.append((q,t))
 if len(calls)!=20 or pd(calls)!=CALL_SHA:raise AuditError('callee closure changed')
 enc=starts|inside|{v|1 for v in starts|inside};raw=[]
 for o in range(len(b)-3):
  v=struct.unpack_from('<I',b,o)[0]
  if v in enc:raw.append((BASE+o,v))
 if len(raw)!=92 or pd(raw)!=RAW_SHA:raise AuditError('raw lookalike census changed')
 authentic=[x for x in raw if x[0] in {0x6A45E4,0x6A45E8,0x793748}]
 if authentic!=STORED or pd(authentic)!=STORED_SHA:raise AuditError('stored roots changed')
 overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text());routed=any('production_test' in x.get('path','').lower() for x in overlay['sources'])
 if routed:raise AuditError('analysis-only screen entered overlay')
 return {'surface':{'linked_functions':3,'body_bytes':286,'owned_noncode_bytes':30,'physical_bytes':316,'descriptor_bytes':16,'direct_bl_entry_sites':0,'direct_body_calls':20,'stored_entry_pointers':3,'raw_entry_or_interior_values':92,'excluded_instruction_byte_lookalikes':89,'strict_interior_ingress':0},'registration':{'screen_id':'0x0000010b','data_handler':'0x005cf7a9','screen_event_handler':'0x005cf7f3','predicate':'0x005cf7ef','state_address':'0x200030a0'},'behavior':{'construct_event':2,'recognized_noop_event':3,'root_dimensions':[640,480],'grid_dimensions':[3,3],'dot_dimensions':[10,10],'x_positions':[66,266,466],'y_positions':[21,121,221],'dot_rgb':[255,255,255],'root_global':'0x20074894','registry_root_field':'0x200030a4'},'boundary':{'next_function':'0x005cf8e4','next_function_role':'unrelated delimiter parser'},'production':{'candidate':None,'production_routed':routed,'ownership_bytes':0,'historical_source_available':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True));print('G2 production-test screen audit: PASS')

#!/usr/bin/env python3
"""Verify selector 3 DATA relocation and natural/direct stock comparisons."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
BINDINGS=HERE/'native-selector-bindings.json'
MANIFEST=Path('/tmp/opencfw-root-pcm22-relocated/handler3-integrated/input-manifest.json')
BASE_SHA='687b0a4e3ce6aef856d19738977a8285033a36110c629d73b0b3cc7306da187d'
MANIFEST_SHA='3ad80cceb776fc772035b5f4d529f0d3c06b8720d17cf571a9afbd27c9b86d2d'
IMAGE_SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
DATA_SHA='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
BASE=0x410000; RECORD=0x433104; TABLE=0x20000158; STOP=0x08000000; EVENT=0x42a878
spec=importlib.util.spec_from_file_location('selector3_verify',HERE.parent/'pcm2_2-handler3/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

def digest(data):return hashlib.sha256(data).hexdigest()
def p32(x):return struct.pack('<I',int(x)&0xffffffff)
def r(u,p,n=4):return bytes(u.mem_read(p,n))
def r32(u,p):return struct.unpack('<I',r(u,p,4))[0]
def make_uc():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0,0x1000),(STOP,0x20000),(0x10000,0x40000),(0x20000000,0x40000),(0x40000000,0x100000),(0x410000,0x25000),(0xe0000000,0x200000),(0x47ff0000,0x1000)]:u.mem_map(lo,sz)
 return u
def install(u,stock,image,segments,symbols):
 if stock:u.mem_write(BASE,image)
 else:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 guard=None
 if not stock:
  adapter=symbols['opencfw_boot_expand_adapter']&~1
  assert adapter==0x415326
  def source_guard(cpu,pc,size,_):
   if BASE<=pc<0x435000:
    assert adapter<=pc<adapter+6,('source installer executed locked bytes',hex(pc))
  guard=u.hook_add(UC_HOOK_CODE,source_guard)
 try:raw=v.init_image(u,stock,image,segments,symbols)
 finally:
  if guard is not None:u.hook_del(guard)
 assert len(raw)==1371
 return raw
def seed_natural(u,installed):
 vddc=struct.unpack_from('<21I',installed,0xa4);vddf=struct.unpack_from('<21I',installed,0xf4)
 profile=bytearray(0x80);struct.pack_into('<I',profile,0,0x1f01600d)
 for i in range(21):
  core=(i*37+11)&0x3ff;tempco=(i*3+5)&0xf
  word=(vddf[i]&0x7f)|(core<<7)|(tempco<<17)|((vddc[i]&0x7f)<<21)
  struct.pack_into('<I',profile,4+4*i,word)
 struct.pack_into('<I',profile,0x64,0x0a654321);u.mem_write(0x20026ba0,bytes(profile))
 for p,val in [(0x40021108,0x30),(0x40021000,0),(0x40008800,0),(0x400204d8,0),(0x40008010,0),
               (0x40021008,0x00400000),(0x40021010,0),(0x40021018,0),(0x40021028,0),
               (0x400083e0,0),(0x40008064,0),(0x4002004c,0x5a5a1234),(0x40020344,0x13572468),
               (0x40020358,0x24681357),(0x40004030,0x01000000),(0x40004044,0x20)]:u.mem_write(p,p32(val))
 u.mem_write(0x2002708c,b'\0');u.mem_write(0x200271be,b'\0');u.mem_write(0x200271bd,b'\x02')
 u.mem_write(0x200271a5,b'\0');u.mem_write(0x200271af,b'\xa5');u.mem_write(0x200271b0,b'\xa5')
 u.mem_write(0x20001000,struct.pack('<III',struct.unpack('<I',struct.pack('<f',-100.0))[0],0xaaaaaaaa,0x55555555))
def natural(stock,image,segments,symbols):
 u=make_uc()
 if stock:u.mem_write(BASE,image)
 installed=install(u,stock,image,segments,symbols)
 if stock:assert digest(installed)==DATA_SHA
 assert r32(u,0x20000150)==7 and r32(u,0x20000148)==7 and r32(u,0x2000014c)==6 and r32(u,0x20000154)==255
 seed_natural(u,installed)
 targets=[r32(u,TABLE+4*i) for i in range(27)]
 if stock:assert targets[3]==0x4283e3
 else:assert targets[3]==(symbols['opencfw_spot_pcm22_transition3']|1)
 calls=[];waits=[];writes=[];unknown=[None];done=[False]
 def code(cpu,pc,size,_):
  if (pc&~1)==STOP:done[0]=True;cpu.emu_stop();return
  if pc==0x40:waits.append(cpu.reg_read(a.UC_ARM_REG_R0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if not stock and BASE<=pc<0x435000:
   adapter=symbols['opencfw_boot_expand_adapter']&~1
   assert adapter<=pc<adapter+6,('source executed stock executable bytes',hex(pc))
  for i,t in enumerate(targets):
   if pc!=(t&~1):continue
   call={'selector':i,'args':[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{k}')) for k in range(4)],
         'lr':hex(cpu.reg_read(a.UC_ARM_REG_LR)&~1),'sp':cpu.reg_read(a.UC_ARM_REG_SP),
         'primask':cpu.reg_read(a.UC_ARM_REG_PRIMASK)};calls.append(call)
   if i in (3,24,25,26):return
   unknown[0]=call;cpu.emu_stop();return
 def wr(cpu,access,addr,size,value,_):
  if 0x40000000<=addr<0x40100000:writes.append([addr,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x400fffff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_PRIMASK,0)
 u.reg_write(a.UC_ARM_REG_R0,2);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R2,0x20001000)
 entry=EVENT if stock else symbols['opencfw_boot_spotmgr_power_state_update_a']&~1
 u.emu_start(entry|1,0,count=2000000)
 return {'calls':calls,'unknown':unknown[0],'completed':done[0] or ((u.reg_read(a.UC_ARM_REG_PC)&~1)==STOP),
         'return':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],
         'state':{f'{p:08x}':r(u,p,4).hex() for p in (0x20000150,0x2000014c,0x20000154,0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4)},
         'arguments_after':r(u,0x20001000,12).hex(),'writes':writes,'waits':waits,
         'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],
         'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
def getmask(u,symbols):
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);done=[False]
 def hook(cpu,pc,size,_):
  if pc==STOP:done[0]=True;cpu.emu_stop()
 h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start((symbols['opencfw_boot_selector_source_mask']&~1)|1,0,count=10000);u.hook_del(h)
 assert done[0];return u.reg_read(a.UC_ARM_REG_R0)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--frozen-base',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 image=IMAGE.read_bytes();assert digest(image)==IMAGE_SHA
 manifest_path=args.candidate.parent/'input-hashes.json'
 manifest=json.loads(manifest_path.read_text());assert digest(args.candidate.read_bytes())==manifest['elf_sha256']
 for row in manifest['inputs']:
  assert digest((args.candidate.parent/row['path']).read_bytes())==row['sha256']
 _,segments,symbols=v.er.elf_info(args.candidate)
 for n in ('opencfw_boot_expand_adapter','opencfw_boot_selector_source_mask','opencfw_boot_spotmgr_power_state_update_a','opencfw_spot_pcm22_transition3','event_a_power_ton_adjust','opencfw_pcm22_timer_service','opencfw_hal_delay_us'):assert n in symbols,n
 bindings=json.loads(BINDINGS.read_text());assert bindings['slots']['3']=='opencfw_spot_pcm22_transition3' and bindings['source_mask']=='0x7f7ff6f'
 adapter=symbols['opencfw_boot_expand_adapter']&~1
 adapter_segment=next(s for s in segments if s['address']<=adapter and adapter+6<=s['address']+len(s['data']))
 adapter_bytes=adapter_segment['data'][adapter-adapter_segment['address']:adapter-adapter_segment['address']+6]
 assert adapter==0x415326,(hex(adapter),adapter_bytes.hex())
 stock_uc=make_uc();source_uc=make_uc();stock_raw=install(stock_uc,True,image,segments,symbols);source_raw=install(source_uc,False,image,segments,symbols)
 assert digest(stock_raw)==DATA_SHA
 normalized=bytearray(source_raw)
 for slot,name in bindings['slots'].items():
  off=0x158+4*int(slot);actual=struct.unpack_from('<I',source_raw,off)[0]
  assert actual==(symbols[name]|1),(slot,name,hex(actual),hex(symbols[name]|1))
  normalized[off:off+4]=stock_raw[off:off+4]
 for off,name in [(0x4d0,'opencfw_boot_dfu_thread_deinit_native'),(0x4f8,'opencfw_boot_manager_thread_deinit')]:
  assert struct.unpack_from('<I',source_raw,off)[0]==symbols[name]|1
  normalized[off:off+4]=stock_raw[off:off+4]
 assert bytes(normalized)==stock_raw
 assert source_raw[1370]==stock_raw[1370]
 mask_uc=make_uc()
 for seg in segments:mask_uc.mem_write(seg['address'],seg['data'])
 mask=getmask(mask_uc,symbols);assert mask==0x7f7ff6f,hex(mask)
 # Run all seven previously established selector-3 direct fixtures on this ELF.
 direct=[];coverage=set()
 for fixture in v.fixtures():
  s,vis=v.run(True,image,segments,[],symbols,symbols,fixture)
  c,_=v.run(False,image,segments,[],symbols,symbols,fixture)
  assert s==c,(fixture['name'],s,c);direct.append({'fixture':fixture,'result':s});coverage|=vis
 # Fresh machines: execute natural event callback using the source-installed slot3 pointer.
 s=natural(True,image,segments,symbols);c=natural(False,image,segments,symbols)
 assert [x['selector'] for x in s['calls']]==[3] and [x['selector'] for x in c['calls']]==[3]
 assert s['calls'][0]['args']==c['calls'][0]['args']==[19,7,6,6]
 assert s['unknown'] is None and c['unknown'] is None and s['completed'] and c['completed']
 assert s['return'][0]==c['return'][0]==0 and s['state']==c['state'] and s['arguments_after']==c['arguments_after']
 assert s['writes']==c['writes'] and s['waits']==c['waits'] and s['callee_saved']==c['callee_saved'] and s['sp']==c['sp']
 result={'status':'PASS','candidate':str(args.candidate),'candidate_sha256':digest(args.candidate.read_bytes()),
  'frozen_base':str(args.frozen_base),'frozen_base_sha256':digest(args.frozen_base.read_bytes()),'manifest_sha256':digest(manifest_path.read_bytes()),
  'link_inputs':manifest['linked_objects'],'source_mask':hex(mask),
  'scatter_data':{'stock_sha256':digest(stock_raw),'source_raw_sha256':digest(source_raw),'normalized_source_sha256':digest(bytes(normalized)),
    'slot3_stock':hex(struct.unpack_from('<I',stock_raw,0x158+12)[0]),'slot3_source':hex(struct.unpack_from('<I',source_raw,0x158+12)[0]),
    'slot3_source_symbol':hex(symbols['opencfw_spot_pcm22_transition3']|1),'all_data_equal_after_declared_relocations':True,
    'source_adapter':{'address':hex(adapter),'bytes':adapter_bytes.hex()}},
  'direct_selector3':{'count':len(direct),'stock_body_bytes_visited':len(coverage),'body_bytes':292,'comparisons':direct},
  'natural_callback':{'stock':s,'source':c,'event_entry_stock':hex(EVENT),'args':[19,7,6,6],
    'no_manual_callback_rebinding':True,'no_unknown_callback_target':True},
  'limits':['Source receives only candidate ELF segments; it executes no locked callback or handler bytes. The source-installed slot3 relocation is used as-is.','Natural callback uses deterministic offline MMIO/profile values and a synthetic immediate ROM wait at 0x40. Timer is disabled for the natural event case; the direct suite includes timer-ready state26 and uses the native timer-service provider.','Direct coverage visits 268/292 stock selector3 bytes. Unvisited conditional bytes remain unclaimed; no physical-device or byte-identity claim is made.']}
 args.output.write_text(json.dumps(result,indent=2)+'\n')
 print('PASS integrated selector3: normalized initialized DATA; 7 direct fixtures; natural [19,7,6,6] callback')
if __name__=='__main__':main()

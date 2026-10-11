#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2];im=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=im.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x43ca50-0x437fe0:0x43cb84-0x437fe0];assert hashlib.sha256(body).hexdigest()=='debf15ecef87bec0076f05cc733e9f5d59fc902f3e2e2549476bea31a244c0f5'
cc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');elfp=Path('/tmp/audio_short_log_output.elf')
providers={'audio_log_lock_state':0x20074388,'audio_log_ring_state':0x200004c8,'audio_log_lock':0x441751,'audio_log_unlock':0x441711,'audio_log_flags':0x43d0cf,'audio_log_flush_ready':0x443485,'audio_log_flush_busy':0x4487ad,'audio_log_flush_notify':0x448f7d}
flags=['-mcpu=cortex-m55','-mthumb','-O0','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,audio_log_short_output']+[f'-Wl,--defsym={k}={v:#x}' for k,v in providers.items()]
subprocess.run([str(cc),*flags,str(H/'short_log_output.c'),'-o',str(elfp)],check=True)
with elfp.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_log_short_output');segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
REG=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)
def run(source,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob);u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x800000);u.reg_write(UC_ARM_REG_SP,0x207ff000);u.reg_write(UC_ARM_REG_LR,0x10000001);u.reg_write(UC_ARM_REG_XPSR,0x01000000|c['ipsr'])
 u.mem_write(0x20074388,struct.pack('<I',c['mutex']));u.mem_write(0x200004c8,struct.pack('<4I',0x20050000,c['capacity'],c['read'],c['write']))
 u.mem_write(0x20050000,bytes((i*17+3)&255 for i in range(8192)));u.mem_write(0x20040000,bytes((i*29+7)&255 for i in range(512)))
 for reg,v in zip(REG,(0x20040000,c['length'],0)):u.reg_write(reg,v)
 calls=[]
 def ret(v=None):
  if v is not None:u.reg_write(UC_ARM_REG_R0,v&0xffffffff)
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(emu,pc,size,data):
  r=[emu.reg_read(x) for x in REG]
  if pc==0x441750:calls.append(['lock',r[0],r[1]]);ret(c['lock']);return
  if pc==0x441710:calls.append(['unlock',r[0]]);ret();return
  if pc==0x43d0ce:calls.append('flags');ret(c['flags']);return
  if pc==0x443484:calls.append('ready');ret(c['ready']);return
  if pc==0x4487ac:calls.append('busy');ret(c['busy']);return
  if pc==0x448f7c:calls.append('notify');ret();return
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x43ca50)|1,0x10000000,count=25000)
 except Exception as exc:raise RuntimeError((source,c,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return dict(calls=calls,state=bytes(u.mem_read(0x200004c8,16)).hex(),ring=bytes(u.mem_read(0x20050000,8192)).hex())
cases=[]
for cap,read,write,length in itertools.product((0,1,8,16,240,4096,4100),(0,1,7,15,235,4095),(0,1,7,15,235,4095),(0,1,4,16,239,256)):
 if len(cases)>=900:break
 cases.append(dict(capacity=cap,read=read,write=write,length=length,ipsr=0,mutex=0x20060000,lock=1,flags=0,ready=0,busy=0))
for cap,read,write,length,flags,ready,busy in itertools.product((240,4096,4100),(0,1,16),(0,1,235,4095),(1,16,240),(0,1,4,5),(0,1),(0,1)):
 cases.append(dict(capacity=cap,read=read,write=write,length=length,ipsr=0,mutex=0x20060000,lock=1,flags=flags,ready=ready,busy=busy))
for ipsr,mutex,lock in itertools.product((0,3,15),(0,0x20060000),(0,1,2)):
 cases.append(dict(capacity=16,read=0,write=0,length=4,ipsr=ipsr,mutex=mutex,lock=lock,flags=1,ready=1,busy=0))
rows=[]
for c in cases:
 a=run(False,c);b=run(True,c)
 if a!=b:
  print('DIFF',c,{'calls':a['calls'],'state':a['state']},{'calls':b['calls'],'state':b['state']})
  for i,(x,y) in enumerate(zip(bytes.fromhex(a['ring']),bytes.fromhex(b['ring']))):
   if x!=y:print('ring first diff',i,x,y);break
  raise SystemExit(1)
 rows.append(c)
(H/'short-log-output-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'body_sha256':hashlib.sha256(body).hexdigest(),'source_sha256':hashlib.sha256((H/'short_log_output.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elfp.read_bytes()).hexdigest(),'providers':{k:hex(v) for k,v in providers.items()},'cases_data':rows,'limits':'Synthetic ring RAM state, lock/flags/flush callbacks intercepted; physical output and concurrent producer/consumer state not established.'},indent=2)+'\n');print('PASS',len(rows))

#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[3];im=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=im.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');elfp=Path('/tmp/audio_simple_log.elf')
providers={'audio_log_policy':0x44a9af,'audio_log_lock':0x441751,'audio_log_format':0x43cb85,'audio_log_unlock':0x441711,'audio_log_lock_state':0x20074388}
flags=['-mcpu=cortex-m55','-mthumb','-O0','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,compressed_log_output']+[f'-Wl,--defsym={k}={v:#x}' for k,v in providers.items()]
subprocess.run([str(cc),*flags,str(R/'g2/components/audio/audio_log_entries_source_candidate/compressed.c'),'-o',str(elfp)],check=True)
with elfp.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='compressed_log_output');segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
REG=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
def run(source,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob);u.mem_map(0x10000000,0x100000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_map(0x20000000,0x800000);u.mem_write(0x20074388,struct.pack('<I',case['state']));u.reg_write(UC_ARM_REG_SP,0x207ff000);u.reg_write(UC_ARM_REG_LR,0x10000001)
 for reg,v in zip(REG,(case['mask'],0x20040000,0x20040100,0x12345678)):u.reg_write(reg,v)
 u.mem_write(0x20040000,b'format %08x %d\0');u.mem_write(0x20040100,b'copy %08x %d\0');u.mem_write(0x207ff000,struct.pack('<3I',0xabcddcba,0x31323334,0x55667788));u.reg_write(UC_ARM_REG_XPSR,0x01000000|case['ipsr'])
 calls=[]
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def ret(v=None):
  if v is not None:u.reg_write(UC_ARM_REG_R0,v&0xffffffff)
  u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def hook(emu,pc,size,data):
  r=[emu.reg_read(x) for x in REG]
  if pc==0x44a9ae:calls.append(['policy',r[0]]);ret(case['policy']);return
  if pc==0x441750:calls.append(['lock',r[0],r[1]]);ret(case['lock']);return
  if pc==0x43cb84:calls.append(['format',r[0],r[1],[word(r[2]+4*i) for i in range(3)]]);ret();return
  if pc==0x441710:calls.append(['unlock',r[0]]);ret();return
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((entry if source else 0x43ce9e)|1,0x10000000,count=3000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return dict(return_value=u.reg_read(UC_ARM_REG_R0),calls=calls)
rows=[]
for mask,policy,state,lock,ipsr in itertools.product((0,0x04800000,0xffffffff),(0,1,-1),(0,0x20050000),(0,1,2),(0,3,15)):
 case=dict(mask=mask,policy=policy,state=state,lock=lock,ipsr=ipsr)
 a=run(False,case);b=run(True,case)
 if a!=b:print('DIFF',case,a,b);break
 rows.append(case)
else:
 (H/'compressed-log-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'body_sha256':hashlib.sha256(blob[0x43ce9e-0x437fe0:0x43cf02-0x437fe0]).hexdigest(),'source_sha256':hashlib.sha256((R/'g2/components/audio/audio_log_entries_source_candidate/compressed.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elfp.read_bytes()).hexdigest(),'providers':{k:hex(v) for k,v in providers.items()},'fixtures':rows,'limits':'IPSR 0/3/15; policy/lock/formatter/unlock intercepted; shared state synthetic. Logger formatting and output not source owned.'},indent=2)+'\n');print('PASS',len(rows))

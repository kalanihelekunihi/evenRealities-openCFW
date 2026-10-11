#!/usr/bin/env python3
from pathlib import Path
import hashlib, itertools, json, struct, subprocess
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H = Path(__file__).resolve().parent
R = H.parents[2]
im = R / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob = im.read_bytes()
assert hashlib.sha256(blob).hexdigest() == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body = blob[0x43ce9e-0x437fe0:0x43cf02-0x437fe0]
cc = '/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc'
elf = H / 'short_log_wrapper.elf'
defs = {'audio_log_policy':0x44a9af,'audio_lock_take':0x441751,
        'audio_lock_give':0x441711,'audio_log_short_format':0x43cb85,
        'audio_log_lock_state':0x20074388}
cmd = [cc,'-mcpu=cortex-m55','-mthumb','-mfloat-abi=hard','-mfpu=fpv5-d16',
       '-O0','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
       '-Wl,-e,g2_flashdb_candidate_compress',
       *[f'-Wl,--defsym={k}={v:#x}' for k,v in defs.items()],
       str(H/'short_log_wrapper.c'),'-o',str(elf)]
subprocess.run(cmd,check=True)
with elf.open('rb') as f:
 e=ELFFile(f)
 entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_candidate_compress')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
source_mrs = 0x10001022
source_mrs_reg = UC_ARM_REG_R3

def run(source,case):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
 u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
 u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x800000)
 u.mem_write(0x20074388,struct.pack('<I',case['lock']))
 u.reg_write(UC_ARM_REG_SP,0x207ff000)
 u.reg_write(UC_ARM_REG_LR,0x10000001)
 u.reg_write(UC_ARM_REG_IPSR,case['ipsr'])
 for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                  (case['token'],case['category'],0x20041000,0x12345678)):
  u.reg_write(reg,v)
 u.mem_write(0x20041000,b'x=%d y=%x\0')
 u.mem_write(0x207ff000,struct.pack('<4I',0xaabbccdd,0x99887766,0x1234,0x5678))
 calls=[]
 def hook(emu,pc,size,data):
  if pc in (0x43ceb4,source_mrs):
   emu.reg_write(UC_ARM_REG_R0 if pc==0x43ceb4 else source_mrs_reg,case['ipsr'])
   emu.reg_write(UC_ARM_REG_PC,(pc+4)|1)
   return
  if pc not in (0x44a9ae,0x441750,0x441710,0x43cb84):return
  r0=emu.reg_read(UC_ARM_REG_R0);r1=emu.reg_read(UC_ARM_REG_R1);r2=emu.reg_read(UC_ARM_REG_R2)
  if pc==0x44a9ae:calls.append(['policy',r0]); ret=case['policy']
  elif pc==0x441750:calls.append(['take',r0,r1]);ret=case['take']
  elif pc==0x441710:calls.append(['give',r0]);ret=0
  else:
   args=struct.unpack('<4I',bytes(emu.mem_read(r2,16)))
   calls.append(['format',r0,r1,list(args)]);ret=0
  emu.reg_write(UC_ARM_REG_R0,ret)
  emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x43ce9e)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,case,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return {'calls':calls,'return':u.reg_read(UC_ARM_REG_R0),'lock':struct.unpack('<I',u.mem_read(0x20074388,4))[0]}

cases=[]
for policy,ipsr,lock,take,token,category in itertools.product((0,1,255),(0,3),(0,0x20050000),(0,1,2),(0,0xffffffff,0x04800000),(0,0x3fffff,0xabcdef01)):
 case=dict(policy=policy,ipsr=ipsr,lock=lock,take=take,token=token,category=category)
 a,b=run(False,case),run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 cases.append(case)
receipt={'status':'PASS','cases':len(cases),'stock_body_sha256':hashlib.sha256(body).hexdigest(),
         'source_sha256':hashlib.sha256((H/'short_log_wrapper.c').read_bytes()).hexdigest(),
         'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),
         'image_sha256':hashlib.sha256(blob).hexdigest(),'compile':cmd,
         'limits':'Lower policy, lock and formatter are ABI interceptions; caller has valid format and four varargs; interrupt and lock state are synthetic.'}
(H/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(cases))

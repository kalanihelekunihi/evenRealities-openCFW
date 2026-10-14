#!/usr/bin/env python3
"""Real variadic logger/formatter/callback/UART graph, synthetic ready/BUSY inputs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn.arm_const import *
import struct,json,hashlib,itertools
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;E=H.parent/'case-wave022-logging-stack/final/case.elf';F=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert E.exists()
assert sha(F)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
with E.open('rb') as f:
 e=ELFFile(f);sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
SP=0x20008000;STOP=0x2000f000;FMT=0x20005000;STRING=0x20005200;OUT=0x20005300
rows=[]
def run(native,length,toggle,busy,quiet):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
 if native:u.mem_write(0x08000000,F.read_bytes()[32:])
 else:
  for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_map(0x40013000,0x1000);u.mem_write(FMT,bytes((i*37+13)&255 for i in range(512)));u.mem_write(STRING,b'abcdef\0');u.mem_write(OUT,b'\xa5'*8)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 w(0x20000e24,0x40013800);w(0x20000e24+0x88,0 if busy else 0x20);w(0x4001381c,0xc0)
 u.mem_write(0x200000bf,bytes([quiet]))
 regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
 for reg,v in zip(regs,[FMT,length,0x2222,0x3333]):u.reg_write(reg,v)
 saved=[0x45670000+i for i in range(8)]
 for reg,v in zip(range(UC_ARM_REG_R4,UC_ARM_REG_R11+1),saved):u.reg_write(reg,v)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1);writes=[];attempts=[];low=SP;callbacks=0
 def code(uc,address,size,data):
  nonlocal low,callbacks
  low=min(low,uc.reg_read(UC_ARM_REG_SP))
  if address==(0x0800a380 if native else sy['case_log_output_char']&~1):callbacks+=1
  if address==(0x080066ac if native else sy['case_write_controller_blocking']&~1):
   assert uc.reg_read(UC_ARM_REG_R0)==0x20000e24 and uc.reg_read(UC_ARM_REG_R2)==1 and uc.reg_read(UC_ARM_REG_R3)==65535
   attempts.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1))[0])
 def write(uc,access,address,size,value,data):
  if address==0x40013828:
   writes.append(value)
   if len(writes)==toggle:u.mem_write(0x200000bf,b'\1')
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((0x080067c8 if native else sy['log_hex_buffer'])|1,STOP,count=300000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP and u.reg_read(UC_ARM_REG_SP)==SP
 assert [u.reg_read(r) for r in range(UC_ARM_REG_R4,UC_ARM_REG_R11+1)]==saved
 return {'return':u.reg_read(UC_ARM_REG_R0),'ram':bytes(u.mem_read(0x20000000,0x3000)).hex(),'n_output':bytes(u.mem_read(OUT,8)).hex(),'attempts':attempts,'writes':writes,'callbacks':callbacks,'stack_bytes':SP-low}
cases=[(n,t,b,0) for n,t,b in itertools.product([0,1,2,5,16],[None,1,2,3,5,8],[False,True])]+[(n,None,b,1) for n,b in itertools.product([0,1,65535,65536,0xffffffff],[False,True])]
for length,toggle,busy,quiet in cases:
 a=run(True,length,toggle,busy,quiet);b=run(False,length,toggle,busy,quiet)
 fields=[k for k in a if k not in ['stack_bytes','return'] and a[k]!=b[k]]
 if fields:
  (H/'failure.json').write_text(json.dumps({'length':length,'toggle':toggle,'busy':busy,'quiet':quiet,'different_fields':fields,'native':a,'source':b},indent=2)+'\n');raise AssertionError((length,toggle,busy,quiet,fields))
 assert a['callbacks']==len(a['attempts'])
 assert a['writes']==([] if busy else a['attempts'])
 rows.append({'length':length,'disable_after_TDR_write':toggle,'busy':busy,'initial_quiet':quiet,'output_hex':bytes(a['attempts']).hex(),'native_stack_bytes':a['stack_bytes'],'source_stack_bytes':b['stack_bytes']})
r={'status':'PASS_FULL_LIVE_HEX_LOG_DISABLE_GRAPH','cases':len(rows),'ELF_sha256':sha(E),'firmware_sha256':sha(F),'comparisons':rows,'limits':['Synthetic READY/BUSY and explicitly injected external RAM disable change after chosen actual TDR write; no provider interception','Only initially disabled paths test oversized lengths; native/source16bit loop counter would not terminate for enabled length>=65536; retained stock behavior','Valid enabled buffers cover0/1/2/5/16bytes; physical asynchronous timing and wire not validated']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])

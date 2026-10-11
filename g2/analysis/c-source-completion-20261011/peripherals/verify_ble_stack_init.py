"""Actual compiled-C/native BLE startup child order and authenticated arguments.

All deep Cordio children are cut identically; this tests source order, pool
setup and callback bindings, not their execution or hardware initialization.
"""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_stack_init.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
native={}
for line in (ROOT/'symbols/apollo_main.tsv').read_text().splitlines():
 p=line.split('\t')
 if len(p)>3 and p[3] and p[3] not in native:
  try:native[p[3]]=int(p[0],16)
  except ValueError:pass
overrides={'audio_wsf_os_initialize':0x52b9b2,'audio_wsf_buffer_init':0x530364,
 'audio_wsf_product_pool_arena':0x2004fa98,'audio_wsf_product_pool_config':0x200003b0,
 'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,
 'compressed_log_output':0x43ce9e,'audio_ble_comm_handler_init':0x4b7e74,
 'audio_ble_hci_driver_handler_init':0x4b4a7c}
with tempfile.TemporaryDirectory() as td:
 obj=Path(td)/'source.o';elf=Path(td)/'source.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(SRC),'-o',str(obj)],check=True)
 undefined=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(obj)],text=True).splitlines()]
 mapping={}
 for s in undefined:
  if s in overrides:addr=overrides[s]
  elif s.startswith('audio_ble_stack_lower_') or s.startswith('audio_ble_handler_'):addr=int(s.rsplit('_',1)[1],16)
  elif s in native:addr=native[s]
  else:raise RuntimeError('unmapped '+s)
  mapping[s]=addr if addr>=0x20000000 else addr|1
 args=['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_ble_exactle_stack_initialize','-o',str(elf),str(obj)]
 args += ['--defsym='+s+'='+hex(a) for s,a in mapping.items()]
 subprocess.run(args,check=True,capture_output=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segs=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD']
  source=next(x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name=='audio_ble_exactle_stack_initialize')
 call_targets={a&~1 for s,a in mapping.items() if a<0x20000000 and not s.startswith('audio_ble_handler_')}
 def run(c):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  events=[];handlers=[0]
  def hook(uc,a,size,_):
   if a not in call_targets:return
   regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if a==0x530364:events.append((a,regs[:4]));uc.reg_write(UC_ARM_REG_R0,0x2930)
   elif a==0x52b980:
    events.append((a,regs[0]));handlers[0]+=1;uc.reg_write(UC_ARM_REG_R0,handlers[0])
   elif a==0x52acce:events.append((a,regs[0]));uc.reg_write(UC_ARM_REG_R0,0)
   else:events.append((a,None));uc.reg_write(UC_ARM_REG_R0,0)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  try:u.emu_start((source if c else 0x4b7f64)|1,0x600000,count=30000)
  except Exception:
   print('failed',c,'pc',hex(u.reg_read(UC_ARM_REG_PC)),'last',events[-6:]);raise
  return events
 a,b=run(False),run(True)
 assert a==b,(len(a),len(b),next(((i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y),None))
 print('PASS BLE stack init children',len(a),'handlers',sum(x[0]==0x52b980 for x in a))

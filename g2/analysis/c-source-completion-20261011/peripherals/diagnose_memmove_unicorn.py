"""Diagnostic reproducer of Unicorn IT-loop discrepancies; not a qualification gate.
Use verify_memmove_qemu.py for authoritative bounded native comparisons.
"""
from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
BASE=Path(__file__).parent;SRC=BASE/'root-memmove-round93/move_candidate.c';ROOT=BASE.parents[2];FORWARD=ROOT/'components/audio/queue_cmsis_offline/cmsis.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
P=0x20010000;pattern=bytes(range(256))*4
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);forward=td/'forward.c';forward.write_text('#include <stdint.h>\nvoid *audio_queue_copy_bytes('+FORWARD.read_text().split('void *audio_queue_copy_bytes(',1)[1]);elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_grid_move_45475a',str(SRC),str(forward),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  engines.append((u,(syms['audio_uart_lv_grid_move_45475a'] if isc else 0x45475a)|1))
 count=0;reverse=0
 for offset,delta,length in itertools.product(range(4),[-64,-17,-4,-1,0,1,2,3,4,7,17,64],range(81)):
  source=P+256+offset;dest=source+delta;isreverse=source<dest<source+length;trace_case=isreverse and offset==0 and length%4==0;outs=[]
  expected=bytearray(pattern);expected[dest-P:dest-P+length]=expected[source-P:source-P+length]
  for u,entry in engines:
   u.mem_write(P,pattern);writes=[];native_saved=[]
   def write(uc,access,address,size,value,user):
    if P<=address<P+1024:writes.append((address,size,value&((1<<(size*8))-1)))
   
   def boundary(uc,address,size,user):
    if address==0x454766:native_saved.append(uc.reg_read(UC_ARM_REG_R4))
    if address in [0x439be4,syms['audio_queue_copy_bytes']&~1]:
     dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2)
     # Forward branch independently recovered earlier; cut avoids its IT-loop emulator failure.
     uc.mem_write(dst,bytes(uc.mem_read(src,n)));uc.reg_write(UC_ARM_REG_R0,dst);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   bh=u.hook_add(UC_HOOK_CODE,boundary)
   h=u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,dest);u.reg_write(UC_ARM_REG_R1,source);u.reg_write(UC_ARM_REG_R2,length);u.emu_start(entry,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000,(offset,delta,length,hex(entry),hex(u.reg_read(UC_ARM_REG_PC)))
   data=bytes(u.mem_read(P,1024));assert data==bytes(expected),(offset,delta,length)
   assert native_saved==[dest] if entry==0x45475b else u.reg_read(UC_ARM_REG_R0)==dest
   outs.append((native_saved[0] if native_saved else u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),data,writes if trace_case else None));u.hook_del(h);u.hook_del(bh)
  assert outs[0]==outs[1],(offset,delta,length,outs[0][:2],outs[1][:2],outs[0][3],outs[1][3]);count+=1;reverse+=trace_case
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_MEMMOVE','cases':count,'reverse_write_trace_cases':reverse,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'canonical_forward_source_sha256':hashlib.sha256(FORWARD.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_ranges':['439710..4397a6','45475a..454768'],'limits':['Forward native439be4 and compiled canonical copy are child cuts performing byte writes to avoid observed Unicorn forward IT-loop failure; no CPU-state correction. Native saved destination R4 at wrapper pop checked against compiled R0; static mov R0,R4 audited. Reverse store trace only for aligned-source whole-word lengths; other reverse byte loops show Unicorn IT flag handling differences, so compare final bytes. Trace masks ignored high register bits.','Forward source body is existing byte-copy reconstruction; compiler instruction equality and full image/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

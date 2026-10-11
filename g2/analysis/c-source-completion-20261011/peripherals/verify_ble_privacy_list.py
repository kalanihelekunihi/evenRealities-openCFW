"""Compiled-C/native privacy-list no-log row and six-argument call comparisons."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_privacy_rows[2000];uint32_t audio_log_level(void){return 0;}
void audio_log_extended(void){} uint32_t compressed_log_output(void){return 0;}
const uint8_t *DmSecGetLocalIrk(void){return (void *)0x20071000;}
void DmPrivAddDevToResList(void){} void DmPrivSetAddrResEnable(void){}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_subsystem_child_479418',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_list.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for active,policy in (((),0),((1,),0),((0,3),0),((1,),1),((1,),2),((1,),4)):
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   base=syms['audio_ble_privacy_rows'] if c else 0x20067a30
   u.mem_write(base,b'\x00'*2000)
   for idx in active:
    row=base+idx*200;u.mem_write(row+0x2f,b'\x01');u.mem_write(row+0x30,b'\x01')
    u.mem_write(row+7,b'\x01'+b'\x00'*15);u.mem_write(row+0x1d,bytes([idx+2]))
   if not c:u.mem_write(0x20004543,bytes([policy]))
   cuts={syms['DmSecGetLocalIrk']&~1:'irk',syms['DmPrivAddDevToResList']&~1:'add',syms['DmPrivSetAddrResEnable']&~1:'enable',syms['audio_log_level']&~1:'policy',syms['audio_log_extended']&~1:'extended',syms['compressed_log_output']&~1:'compressed'} if c else {0x4d2524:'irk',0x4d282e:'add',0x4d28cc:'enable',0x43d574:'extended',0x43ce9e:'compressed'}
   calls=[]
   def cstr(uc,a):
    out=bytearray()
    for _ in range(256):
     ch=uc.mem_read(a,1)[0]
     if ch==0:break
     out.append(ch);a+=1
    return bytes(out)
   def hook(uc,a,size,_):
    if a in cuts:
     kind=cuts[a]
     if kind=='irk':uc.reg_write(UC_ARM_REG_R0,0x20071000)
     elif kind=='policy':uc.reg_write(UC_ARM_REG_R0,policy)
     elif kind=='add':
      sp=uc.reg_read(UC_ARM_REG_SP);extra=struct.unpack('<II',uc.mem_read(sp,8))
      calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)-base,uc.reg_read(UC_ARM_REG_R2)-base,uc.reg_read(UC_ARM_REG_R3),extra))
     elif kind=='extended':
      sp=uc.reg_read(UC_ARM_REG_SP);line,msg=struct.unpack('<II',uc.mem_read(sp,8))
      calls.append((kind,uc.reg_read(UC_ARM_REG_R0),cstr(uc,uc.reg_read(UC_ARM_REG_R1)),cstr(uc,uc.reg_read(UC_ARM_REG_R2)),cstr(uc,uc.reg_read(UC_ARM_REG_R3)),line,cstr(uc,msg)))
     elif kind=='compressed':calls.append((kind,uc.reg_read(UC_ARM_REG_R0),cstr(uc,uc.reg_read(UC_ARM_REG_R1)),cstr(uc,uc.reg_read(UC_ARM_REG_R2)),uc.reg_read(UC_ARM_REG_R3)))
     else:calls.append((kind,uc.reg_read(UC_ARM_REG_R0)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_subsystem_child_479418'] if c else 0x479418)|1,0x600000,count=30000)
   obs.append(([u.mem_read(base+i*200+0x2e,1)[0] for i in range(10)],calls))
  assert obs[0]==obs[1],(active,policy,obs)
  print('PASS privacy list active rows/policy',active,policy)

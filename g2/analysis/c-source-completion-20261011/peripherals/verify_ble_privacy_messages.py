"""Actual C/native DM privacy 44-byte message construction and failure paths."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
const void *audio_ble_dm_security_state[2]; uint8_t audio_ble_dm_privacy_state[16];
void *audio_wsf_msg_alloc(uint16_t n){(void)n;return 0;}
void audio_wsf_msg_send(uint8_t h,void *p){(void)h;(void)p;}
void *audio_queue_copy_bytes(void *d,const void *s,uint32_t n){(void)s;(void)n;return d;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmPrivAddDevToResList',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_privacy_messages.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for name,native,args in [('DmPrivAddDevToResList',0x4d282e,(3,0x20081000,0x20081020,0x20081040,1,0x1234)),('DmPrivSetAddrResEnable',0x4d28cc,(1,))]:
  for alloc in (False,True):
   obs=[]
   for c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.mem_map(0x20000000,0x100000)
    state=syms['audio_ble_dm_privacy_state'] if c else 0x20073b78
    u.mem_write(state+0xc,b'\x07')
    for addr,n in ((0x20081000,6),(0x20081020,16),(0x20081040,16)):
     u.mem_write(addr,bytes((i+1 for i in range(n))))
    u.mem_write(0x20080000,b'\xaa'*44)
    cuts={syms['audio_wsf_msg_alloc']&~1:'alloc',syms['audio_wsf_msg_send']&~1:'send',syms['audio_queue_copy_bytes']&~1:'copy'} if c else {0x4bf99e:'alloc',0x4bf9ba:'send',0x439be4:'copy'}
    calls=[]
    def hook(uc,a,size,_):
     if a in cuts:
      kind=cuts[a]
      if kind=='alloc':calls.append((kind,uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0x20080000 if alloc else 0)
      elif kind=='copy':
       dst,src,n=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
       uc.mem_write(dst,bytes(uc.mem_read(src,n)));calls.append((kind,dst-0x20080000,src,n));uc.reg_write(UC_ARM_REG_R0,dst)
      else:calls.append((kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,arg in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,arg)
    if len(args)>4:u.mem_write(0x200ff000,struct.pack('<II',*args[4:]))
    u.emu_start((syms[name] if c else native)|1,0x600000,count=1500)
    obs.append((bytes(u.mem_read(0x20080000,44)),calls))
   assert obs[0]==obs[1],(name,alloc,obs)
   print('PASS privacy message',name,'allocation',alloc)
 for value in (0,0x20081040):
  obs=[]
  for c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   cell=syms['audio_ble_dm_security_state'] if c else 0x20074114
   u.mem_write(cell,struct.pack('<I',value))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['DmSecGetLocalIrk'] if c else 0x4d2524)|1,0x600000,count=100)
   obs.append(u.reg_read(UC_ARM_REG_R0))
  assert obs[0]==obs[1],(value,obs)
  print('PASS local IRK cell',value)

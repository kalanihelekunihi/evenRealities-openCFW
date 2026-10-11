"""Actual compiled-C/native BLE communication handler state and ordered calls."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_ble_comm_state[0x60],audio_ble_comm_mode;
uint8_t audio_ble_comm_registration_table[1],audio_ble_comm_profile_table[1];
const uint8_t *audio_ble_comm_registration_slot,*audio_ble_comm_profile_slot;
void audio_ble_app_slave_handler_init(uint8_t h,uint8_t *s,uint8_t *m){(void)h;(void)s;(void)m;}
void audio_ble_profile_handler_init(uint8_t h,uint8_t *s,uint8_t *m){(void)h;(void)s;(void)m;}
void audio_ble_app_master_handler_init(uint8_t h,uint8_t *s,uint8_t *m){(void)h;(void)s;(void)m;}
void audio_ble_subsystem_init(void){}
''')
 elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_comm_handler_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_comm_handler_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for handler in (0,7,255):
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000)
   state=syms['audio_ble_comm_state'] if compiled else 0x200727f0
   mode=syms['audio_ble_comm_mode'] if compiled else 0x200737b0
   reg=syms['audio_ble_comm_registration_slot'] if compiled else 0x200004b8
   prof=syms['audio_ble_comm_profile_slot'] if compiled else 0x20074358
   u.mem_write(state,b'\xaa'*0x60);u.mem_write(mode,b'\xaa')
   cuts={0x46ed94:'slave',0x535488:'profile',0x4a19f4:'master',0x4b7478:'subsystem'} if not compiled else {
    syms['audio_ble_app_slave_handler_init']&~1:'slave',syms['audio_ble_profile_handler_init']&~1:'profile',
    syms['audio_ble_app_master_handler_init']&~1:'master',syms['audio_ble_subsystem_init']&~1:'subsystem'}
   calls=[]
   def hook(uc,a,size,_):
    if a in cuts:
     calls.append((cuts[a],uc.reg_read(UC_ARM_REG_R0)&255,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)) if cuts[a]!='subsystem' else ('subsystem',))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_R0,handler);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_comm_handler_init'] if compiled else 0x4b7e74)|1,0x600000,count=2000)
   rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
   mappings={syms['audio_ble_comm_registration_table']:0x774d44,syms['audio_ble_comm_profile_table']:0x78c9a4} if compiled else {}
   normalized=[(c[0],c[1],0x200727f0,0x200737b0) if len(c)>1 else c for c in calls]
   obs.append((u.mem_read(state+0x56,1),u.mem_read(mode,1),mappings.get(rd(reg),rd(reg)),mappings.get(rd(prof),rd(prof)),normalized))
  assert obs[0]==obs[1],(handler,obs)
  print('PASS BLE comm handler',handler)

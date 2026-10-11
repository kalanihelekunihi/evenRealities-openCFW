"""Compiled-C/native central handler initialization with real child ABI cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
const uint8_t audio_ble_master_registration_table[16]={0};
const uint8_t *audio_ble_master_registration_slot;
uint8_t *audio_ble_master_state_slot,*audio_ble_master_mode_slot,*audio_ble_master_state_shadow,*audio_ble_master_payload_slot;
void audio_ble_set_ring_link_state(uint8_t a,const char*b){(void)a;(void)b;}
void audio_ble_ring_handler_init(uint8_t a,uint8_t*b){(void)a;(void)b;}
uint8_t audio_uart_device_role_get(void){return 0;}
uint32_t audio_uart_ring_mac_ready(void){return 0;}
void audio_ble_status_reply(uint8_t a){(void)a;}
uint32_t audio_uart_ring_active(void){return 0;}
void audio_event_loop_push_delayed(void(*a)(void),uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_ble_master_start_try_connect_ring(void){}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_app_master_handler_init',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_master_handler_init.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for role,active,mac in ((0,0,0),(1,0,1),(2,1,0),(1,1,1)):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cuts={syms['audio_ble_set_ring_link_state']&~1:'link',syms['audio_ble_ring_handler_init']&~1:'ring_init',syms['audio_uart_device_role_get']&~1:'role',syms['audio_uart_ring_mac_ready']&~1:'mac',syms['audio_ble_status_reply']&~1:'status',syms['audio_uart_ring_active']&~1:'active',syms['audio_event_loop_push_delayed']&~1:'delayed',syms['audio_log_level']&~1:'level'} if compiled else {0x49f870:'link',0x4c4810:'ring_init',0x45a568:'role',0x4a2fdc:'mac',0x47d870:'status',0x4a2914:'active',0x47697e:'delayed',0x43d0ce:'level'}
   calls=[]
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if not kind:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if kind=='role':uc.reg_write(UC_ARM_REG_R0,role)
    elif kind=='mac':uc.reg_write(UC_ARM_REG_R0,mac)
    elif kind=='active':uc.reg_write(UC_ARM_REG_R0,active)
    elif kind=='level':uc.reg_write(UC_ARM_REG_R0,0)
    elif kind=='link':calls.append((kind,r0,bytes(uc.mem_read(r1,32)).split(b'\0')[0]))
    elif kind=='ring_init':calls.append((kind,r0,r1-0x20090000))
    elif kind=='status':calls.append((kind,r0))
    elif kind=='delayed':calls.append((kind,r1,uc.reg_read(UC_ARM_REG_R2),r0==((syms['audio_ble_master_start_try_connect_ring'] if compiled else 0x4a23ac)|1)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0x20090000);u.reg_write(UC_ARM_REG_R2,0x20091000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_app_master_handler_init'] if compiled else 0x4a19f4)|1,0x600000,count=1000)
   addresses=(('audio_ble_master_registration_slot',0x20074354),('audio_ble_master_state_slot',0x200742fc),('audio_ble_master_mode_slot',0x20074300),('audio_ble_master_state_shadow',0x20074304),('audio_ble_master_payload_slot',0x20074308))
   cells=[]
   for name,native in addresses:
    val=struct.unpack('<I',u.mem_read(syms[name] if compiled else native,4))[0]
    cells.append('table' if name=='audio_ble_master_registration_slot' and val==(syms['audio_ble_master_registration_table'] if compiled else 0x78c9e4) else val-0x20090000 if name not in ('audio_ble_master_mode_slot','audio_ble_master_registration_slot') else val-0x20091000 if name=='audio_ble_master_mode_slot' else val)
   observations.append((calls,cells))
  assert observations[0]==observations[1],(role,active,mac,observations)
  print('PASS master handler init',role,active,mac)

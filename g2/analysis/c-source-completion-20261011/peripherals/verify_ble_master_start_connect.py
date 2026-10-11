"""Compiled-C/native delayed master-connect callback with source children cut."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
const volatile uint8_t *const audio_uart_hand_context=(void*)0x20090000;
volatile uint8_t audio_ble_ring_link_state;
volatile uint16_t audio_ble_master_connect_wait;
uint32_t audio_uart_ring_active(void){return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
void audio_dump_hex(const char*a,uint32_t b,const uint8_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
void audio_ble_master_set_target(const uint8_t*a,const char*b,uint8_t c){(void)a;(void)b;(void)c;}
uint32_t audio_ble_master_auth_mode_set(uint8_t a){(void)a;return 0;}
void audio_ble_master_schedule_connect(uint32_t a,uint8_t b){(void)a;(void)b;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_start_try_connect_ring',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_master_start_connect.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for case in ('not_owner','mac_unset','disconnecting','connect'):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_ring_link_state'] if compiled else 0x20074f85
   wait=syms['audio_ble_master_connect_wait'] if compiled else 0x20074f18
   u.mem_write(state,bytes([3 if case=='disconnecting' else 0]));u.mem_write(wait,b'\x34\x12')
   context=bytearray(32);context[12:18]=b'\xff'*6 if case=='mac_unset' else b'ABCDEF';u.mem_write(0x20090000,bytes(context))
   cuts={syms['audio_uart_ring_active']&~1:'active',syms['audio_queue_copy_bytes']&~1:'copy',syms['audio_dump_hex']&~1:'dump',syms['audio_ble_master_set_target']&~1:'target',syms['audio_ble_master_auth_mode_set']&~1:'auth',syms['audio_ble_master_schedule_connect']&~1:'schedule',syms['audio_log_level']&~1:'level'} if compiled else {0x4a2914:'active',0x466010:'context',0x439be4:'copy',0x43dacc:'dump',0x4a2068:'target',0x4a2168:'auth',0x4a2618:'schedule',0x43d0ce:'level'}
   calls=[]
   def hook(uc,a,size,_):
    kind=cuts.get(a)
    if not kind:return
    r0,r1,r2,r3=(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    if kind=='active':uc.reg_write(UC_ARM_REG_R0,0 if case=='not_owner' else 1)
    elif kind=='context':uc.reg_write(UC_ARM_REG_R0,0x20090000)
    elif kind=='level':uc.reg_write(UC_ARM_REG_R0,0)
    elif kind=='copy':calls.append(('copy',r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
    elif kind=='dump':calls.append(('dump',bytes(uc.mem_read(r2,r3))))
    elif kind=='target':calls.append(('target',bytes(uc.mem_read(r0,6)),bytes(uc.mem_read(r1,15)),r2))
    elif kind=='auth':calls.append(('auth',r0));uc.reg_write(UC_ARM_REG_R0,1)
    elif kind=='schedule':calls.append(('schedule',r0,r1))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_master_start_try_connect_ring'] if compiled else 0x4a23ac)|1,0x600000,count=10000)
   observations.append((calls,bytes(u.mem_read(wait,2))))
  assert observations[0]==observations[1],(case,observations)
  print('PASS delayed master connect',case)

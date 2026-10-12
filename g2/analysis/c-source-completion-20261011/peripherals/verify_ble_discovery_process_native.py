#!/usr/bin/env python3
"""Actual ARM C/native discovery processor dispatch on three defined states."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_discovery_process.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_rows_200733fc[48],audio_ble_discovery_connection_records_200717b0[0x100];uintptr_t audio_ble_service_dispatch_20074348;volatile uint8_t audio_ble_trace_level_cell;
void audio_ble_service_discovery_restart_531f20(uint8_t a){(void)a;}void audio_ble_service_discovery_start(uint8_t a){(void)a;}void audio_ble_service_discovery_step_531bd4(uint8_t a,uint8_t b){(void)a;(void)b;}
uint8_t *audio_ble_pair_record(uint8_t a){(void)a;return 0;}uint8_t *audio_ble_pair_record_create_47a71c(uint8_t a,const uint8_t*b,uint8_t c){(void)a;(void)b;(void)c;return 0;}void audio_ble_pair_record_update_name_47b3ae(uint8_t*a,const uint8_t*b){(void)a;(void)b;}void audio_ble_pair_record_clear_b(uint8_t*a,uint8_t b){(void)a;(void)b;}
uint8_t audio_dm_conn_role(uint8_t a){(void)a;return 0;}const uint8_t *DmConnPeerAddr(uint8_t a){(void)a;return 0;}uint8_t DmConnPeerAddrType(uint8_t a){(void)a;return 0;}uint8_t audio_ble_dm_sec_level_4b71b2(uint8_t a){(void)a;return 0;}void audio_ble_dm_conn_set_idle(uint8_t a,uint8_t b,uint8_t c){(void)a;(void)b;(void)c;}
uint8_t audio_ble_discovery_service_complete_56bf32(uint8_t*a,const uint8_t*b){(void)a;(void)b;return 0;}void audio_ble_discovery_char_start_56c1b8(uint8_t a,uint8_t*b){(void)a;(void)b;}uint8_t audio_ble_discovery_char_complete_56c1f8(uint8_t*a,const uint8_t*b){(void)a;(void)b;return 0;}uint8_t audio_ble_discovery_config_complete_56c396(uint8_t a,uint8_t*b){(void)a;(void)b;return 0;}
void audio_ble_discovery_print_characteristics_5322f6(uint8_t*a,const uint8_t*b){(void)a;(void)b;}void audio_ble_discovery_print_descriptors_532644(uint8_t*a,const uint8_t*b){(void)a;(void)b;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}int32_t g2_lfs_memcmp(const void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_log_flags(void){return 0;}void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return 1;}void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_discovery_process_532924',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('stage3_error','service_start','config_restart','config_error'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   row=sym['audio_ble_subsystem_rows_200733fc'] if compiled else 0x200733fc;context=0x20080200;message=0x20080300
   data=bytearray(16);data[0:4]=context.to_bytes(4,'little');data[11]=3 if kind=='stage3_error' else (1 if kind=='service_start' else 2);data[14]=1 if kind=='config_restart' else 0;u.mem_write(row,bytes(data));u.mem_write(context,b'\0'*64)
   m=bytearray(16);m[0]=1;m[2]=4 if kind=='stage3_error' else (3 if kind=='service_start' else (5 if kind=='config_restart' else 6));m[3]=1 if kind in ('stage3_error','config_error') else 0;u.mem_write(message,bytes(m))
   callback_cell=sym['audio_ble_service_dispatch_20074348'] if compiled else 0x20074348;u.mem_write(callback_cell,(0x100f01).to_bytes(4,'little'))
   trace=[]
   for name,cs,stock in [('dispatch',None,0x100f00),('service','audio_ble_discovery_service_complete_56bf32',0x56bf32),('charstart','audio_ble_discovery_char_start_56c1b8',0x56c1b8),('start','audio_ble_service_discovery_start',0x531d60),('idle','audio_ble_dm_conn_set_idle',0x4b71dc),('level','audio_log_flags',0x43d0ce)]:
    target=(sym[cs] if compiled else stock) if cs else stock
    def hook(uc,pc,n,user,name=name):
     if name=='level':uc.reg_write(UC_ARM_REG_R0,0)
     else:trace.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     if name=='service':uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_discovery_process_532924'] if compiled else 0x532924)|1,0x600000,count=5000)
   pair.append((bytes(u.mem_read(row,16)),[(n,a,b if n=='dispatch' else 0) for n,a,b in trace]))
  assert pair[0]==pair[1],(kind,pair)
print('PASS_BLE_DISCOVERY_PROCESS_NATIVE 4')

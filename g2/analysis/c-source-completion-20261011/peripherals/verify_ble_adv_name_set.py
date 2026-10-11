"""Actual compiled-C/native advertising name and address path with helper cuts."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
uint8_t audio_ble_adv_name_buffer[64],audio_ble_adv_config_state[16];uint8_t *audio_ble_slave_mode_context;
uint32_t audio_uart_service_mode(void){return 0;}void audio_ble_adv_format_data(uint8_t a){(void)a;}
uint8_t audio_ble_adv_set_scan_response(uint8_t*a){(void)a;return 0;}void audio_ble_psn_into_advertisement(uint8_t*a){(void)a;}
void audio_ble_slave_adv_handler_prepare(void){}uint32_t audio_wsf_interrupt_mask_set(void){return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}void audio_ble_hci_set_custom_bdaddr(uint8_t*a){(void)a;}
uint32_t audio_log_level(void){return 0;}void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'s.c';p.write_text(shim);elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_adv_name_set',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_adv_name_set.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names=[('audio_uart_service_mode',0x45a570),('audio_ble_adv_format_data',0x46dc74),('audio_ble_adv_set_scan_response',0x46dca4),('audio_ble_psn_into_advertisement',0x46dc14),('audio_ble_slave_adv_handler_prepare',0x46dccc),('audio_queue_copy_bytes',0x439be4),('audio_ble_hci_set_custom_bdaddr',0x4b4cd2),('audio_log_level',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
 for mode in (0,1):
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   config=syms['audio_ble_adv_config_state'] if compiled else 0x20003838;namebuf=syms['audio_ble_adv_name_buffer'] if compiled else 0x200003ec;slot=syms['audio_ble_slave_mode_context'] if compiled else 0x20074330
   u.mem_write(config+4,struct.pack('<III',0x20004000,0x20004100,0x20004200));u.mem_write(0x20004001,b'\x11');u.mem_write(0x20004101,b'\x22');u.mem_write(0x20004201,b'ABCDEF');u.mem_write(slot,struct.pack('<I',0x20005000));calls=[]
   cuts={(syms[n]&~1 if compiled else a):n for n,a in names}
   def hook(uc,a,size,_):
    n=cuts.get(a)
    if n is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
    if n=='audio_uart_service_mode':uc.reg_write(UC_ARM_REG_R0,mode);calls.append(('mode',))
    elif n=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,0)
    elif n=='audio_queue_copy_bytes':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));calls.append(('copy',r2))
    elif n=='audio_ble_adv_format_data':calls.append(('format',r0))
    elif n=='audio_ble_adv_set_scan_response':calls.append(('scan',r0==0x20004201))
    elif n=='audio_ble_psn_into_advertisement':calls.append(('psn',r0==0x20004001))
    elif n=='audio_ble_slave_adv_handler_prepare':calls.append(('prepare',))
    elif n=='audio_ble_hci_set_custom_bdaddr':calls.append(('hci',r0==0x2000500f))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms['audio_ble_adv_name_set'] if compiled else 0x46dd44)|1,0x600000,count=500)
   obs.append((calls,u.mem_read(namebuf+11,1),u.mem_read(0x2000500f,6)))
  assert obs[0]==obs[1],(mode,obs);print('PASS adv name',mode)

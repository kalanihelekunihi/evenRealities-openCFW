#!/usr/bin/env python3
"""Bounded actual C/native L2CAP master/slave signaling effect comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
uint8_t audio_ble_l2c_slave_state[0x100];volatile uint8_t audio_l2c_log_enabled_cell;
uint8_t DmConnIdByHandle(uint16_t h){(void)h;return 0;}
void WsfTimerStop(void*p){(void)p;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_hci_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
void audio_ble_l2c_send_cmd_reject_530ae0(uint16_t a,uint8_t b,uint16_t c){(void)a;(void)b;(void)c;}
void audio_ble_l2c_dm_conn_update_rsp_537230(uint8_t a,uint16_t b,uint8_t c){(void)a;(void)b;(void)c;}
void audio_ble_dm_l2c_conn_update_ind_55bc96(uint8_t a,uint16_t b,const uint16_t*c){(void)a;(void)b;(void)c;}
void audio_ble_dm_l2c_conn_update_cnf_56e580(uint16_t a,uint16_t b){(void)a;(void)b;}
void audio_ble_dm_l2c_cmd_rej_ind_56e5a4(uint16_t a,uint16_t b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'role.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_l2c_master_rx_536fbc',str(D/'l2c_signaling_role_handlers.c'),str(D/'l2c_log_helpers.c'),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 native={'audio_ble_l2c_master_rx_536fbc':0x536fbc,'audio_ble_l2c_slave_rx_536c5c':0x536c5c,'DmConnIdByHandle':0x4b6e96,'WsfTimerStop':0x52a4d2,'audio_ble_hci_vendor_log_enabled_4c9c50':0x4c9c50,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'audio_ble_hci_wsf_trace':0x52a63c,'audio_ble_l2c_send_cmd_reject_530ae0':0x530ae0,'audio_ble_l2c_dm_conn_update_rsp_537230':0x537230,'audio_ble_dm_l2c_conn_update_ind_55bc96':0x55bc96,'audio_ble_dm_l2c_conn_update_cnf_56e580':0x56e580,'audio_ble_dm_l2c_cmd_rej_ind_56e5a4':0x56e5a4}
 def run(c,master,code,ident,cmd_len,l2c_len,conn,prior,matched,params,enabled,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_ble_l2c_slave_state'] if c else 0x20073bd8
  u.mem_write(base+conn+0x10,bytes([prior]));u.mem_write(base+conn+0x13,bytes([ident if matched else ident^0xff]))
  p=0x20080000;packet=bytearray(32);packet[8]=code;packet[9]=ident;struct.pack_into('<H',packet,10,cmd_len)
  for i,v in enumerate(params):struct.pack_into('<H',packet,12+2*i,v)
  u.mem_write(p,bytes(packet));effects=[]
  addrs={((sy[k]&~1) if c else v):k for k,v in native.items() if k not in ('audio_ble_l2c_master_rx_536fbc','audio_ble_l2c_slave_rx_536c5c')}
  def txt(ptr):return bytes(u.mem_read(ptr,160)).split(b'\0')[0].decode('ascii')
  def hook(uc,addr,size,user):
   k=addrs.get(addr)
   if k is None:return
   r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   if k=='DmConnIdByHandle':effects.append(('conn_lookup',r0));uc.reg_write(UC_ARM_REG_R0,conn)
   elif k=='audio_ble_hci_vendor_log_enabled_4c9c50':uc.reg_write(UC_ARM_REG_R0,enabled)
   elif k=='audio_log_flags':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='audio_log_extended':
    sp=uc.reg_read(UC_ARM_REG_SP);a=struct.unpack('<IIIII',bytes(uc.mem_read(sp,20)))
    effects.append(('log',r0,a[0],txt(a[1]),a[2],a[3],a[4]))
   elif k=='audio_ble_hci_wsf_trace':
    sp=uc.reg_read(UC_ARM_REG_SP);v=struct.unpack('<I',bytes(uc.mem_read(sp,4)))[0]
    effects.append(('trace',txt(r0),txt(r1),r2,uc.reg_read(UC_ARM_REG_R3),v))
   elif k=='WsfTimerStop':effects.append(('timer',r0-base))
   elif k=='audio_ble_dm_l2c_conn_update_ind_55bc96':effects.append(('ind',r0,r1,struct.unpack('<6H',bytes(uc.mem_read(r2,12)))))
   elif k in ('audio_ble_dm_l2c_conn_update_cnf_56e580','audio_ble_dm_l2c_cmd_rej_ind_56e5a4'):
    effects.append((k,r0,r1))
   else:effects.append((k,r0,r1,r2))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((UC_ARM_REG_R0,0x1234),(UC_ARM_REG_R1,l2c_len),(UC_ARM_REG_R2,p),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  name='audio_ble_l2c_master_rx_536fbc' if master else 'audio_ble_l2c_slave_rx_536c5c'
  u.emu_start((((sy[name]&~1) if c else native[name])|1),0x600000,count=150000)
  return effects,bytes(u.mem_read(base+conn+0x10,4))
 cases=0
 scenarios=[
  (True,0x12,3,8,12,1,0,True,(6,8,10,20),0,0),
  (True,0x12,3,8,12,1,0,True,(1,8,10,20),0,0),
  (True,0x12,3,7,11,1,0,True,(6,8,10,20),0,0),
  (True,1,3,8,12,1,0,True,(6,8,10,20),0,0),
  (False,0x13,3,2,6,1,0x12,True,(0,0,0,0),0,0),
  (False,1,3,2,6,1,0x12,True,(0,0,0,0),0,0),
  (False,0x13,3,2,6,1,0x14,True,(0,0,0,0),0,0),
  (False,0x13,3,2,6,1,0x12,False,(0,0,0,0),0,0),
  (False,0x13,3,2,6,0,0x12,True,(0,0,0,0),0,0),
 ]
 for scenario in scenarios:
  a=run(False,*scenario);b=run(True,*scenario)
  assert a==b,(scenario,a,b)
  cases+=1
 for master,code,matched in ((True,2,True),(True,1,True),(False,2,True),(False,1,False)):
  for enabled in (0,1):
   for flags in (0,2):
    scenario=(master,code,3,7,11,1,0x12,matched,(0,0,0,0),enabled,flags)
    a=run(False,*scenario);b=run(True,*scenario)
    assert a==b,(scenario,a,b)
    cases+=1
 print('PASS_L2C_ROLE_HANDLERS_NATIVE',cases)

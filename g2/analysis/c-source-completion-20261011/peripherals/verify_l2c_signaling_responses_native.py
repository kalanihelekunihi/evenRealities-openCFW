#!/usr/bin/env python3
"""Original/C allocated command rejection and conn-update response effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/l2c_signaling_responses.c'
SHIM='''#include <stdint.h>
uint8_t *WsfMsgDataAlloc(uint16_t n,uint8_t o){(void)n;(void)o;return 0;}
void L2cDataReq(uint16_t c,uint16_t h,uint16_t n,uint8_t*p){(void)c;(void)h;(void)n;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'r.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_l2c_send_cmd_reject_530ae0',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,reply,allocated,handle,id,result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  alloc=(sy['WsfMsgDataAlloc']&~1) if c else 0x4bf990
  send=(sy['L2cDataReq']&~1) if c else 0x530bbc
  p=0x20080000;u.mem_write(p,b'\xa5'*16);effects=[]
  def hook(uc,addr,size,user):
   if addr==alloc:
    effects.append(('alloc',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_R0,p if allocated else 0)
   elif addr==send:
    r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    effects.append(('send',r0,r1,r2,r3==p,bytes(uc.mem_read(r3+8,6))))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  values=(id,handle,result) if reply else (handle,id,result)
  for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),values):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  name='audio_ble_l2c_dm_conn_update_rsp_537230' if reply else 'audio_ble_l2c_send_cmd_reject_530ae0'
  entry=(sy[name]&~1) if c else (0x537230 if reply else 0x530ae0)
  u.emu_start(entry|1,0x600000,count=20000)
  return effects
 cases=0
 for reply in (False,True):
  for allocated in (False,True):
   for handle,id,result in ((0x1234,3,0),(0xffff,255,0xabcd),(0,0,1)):
    a=run(False,reply,allocated,handle,id,result);b=run(True,reply,allocated,handle,id,result)
    assert a==b,(reply,allocated,handle,id,result,a,b)
    cases+=1
 print('PASS_L2C_SIGNALING_RESPONSES_NATIVE',cases)

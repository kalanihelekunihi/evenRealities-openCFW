"""Actual ARM C/native revision request comparison at exchange/log cuts."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_read_revision.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nint32_t audio_ble_radio_exchange_52e612(void*a,const void*b,uint32_t c,void*d,uint32_t*e){return 0;}\nvoid audio_ble_hci_boot_log_4733ee(const void*a,...){(void)a;}\nconst uint8_t audio_ble_hci_radio_command_error_75d590[4]={0};\nvoid *memset(void *p,int c,unsigned n){for(unsigned i=0;i<n;i++)((unsigned char*)p)[i]=c;return p;}\nvoid *memcpy(void *p,const void *q,unsigned n){for(unsigned i=0;i<n;i++)((unsigned char*)p)[i]=((const unsigned char*)q)[i];return p;}\nvoid __aeabi_memclr(void *p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memclr4(void *p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memcpy(void *p,const void *q,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=((const volatile unsigned char*)q)[i];}\n''')
 e=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_read_command_52ea28',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 cases=[('null_context',0,0,0),('null_output',1,0,0),('exchange_fail',1,3,0),('success',1,0,0),('status_fail',1,0,5)]
 for name,ctx,xret,status in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20001000,b'\xaa'*8);calls=[]
   cut_x=(syms['audio_ble_radio_exchange_52e612']&~1) if is_c else 0x52e612
   cut_l=(syms['audio_ble_hci_boot_log_4733ee']&~1) if is_c else 0x4733ee
   def hook(uc,a,size,_):
    if a==cut_x:
     cmd=bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),9));resp=uc.reg_read(UC_ARM_REG_R3)
     uc.mem_write(resp+6,bytes([status]));uc.mem_write(resp+7,b'WXYZ');calls.append(('exchange',cmd,uc.reg_read(UC_ARM_REG_R2)))
     uc.reg_write(UC_ARM_REG_R0,xret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif a==cut_l:
     calls.append(('log',uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20002000 if ctx else 0);u.reg_write(UC_ARM_REG_R1,0x00402000);u.reg_write(UC_ARM_REG_R2,0 if name=='null_output' else 0x20001000);u.reg_write(UC_ARM_REG_R3,4)
   entry=syms['audio_ble_radio_read_command_52ea28'] if is_c else 0x52ea28
   u.emu_start(entry|1,0x600000,count=5000)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20001000,8))))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0][0:2])

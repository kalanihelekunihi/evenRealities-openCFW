"""Actual ARM C/native recovery command packet and output comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_recover_commands.c'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nuint64_t audio_ble_radio_exchange_52e612(void*a,const void*b,uint32_t c,void*d,uint32_t*e){return 0;}\nuint32_t codec_crc32(const uint8_t*p,uint32_t n,const uint32_t*q){return 0;}\nvoid __aeabi_memclr(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memclr4(void*p,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=0;}\nvoid __aeabi_memcpy(void*p,const void*q,unsigned n){for(unsigned i=0;i<n;i++)((volatile unsigned char*)p)[i]=((const volatile unsigned char*)q)[i];}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_recover_read_52f094',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 entries={'read':('audio_ble_radio_recover_read_52f094',0x52f094),'set':('audio_ble_radio_recover_set_52ef74',0x52ef74),'special':('audio_ble_radio_recover_special_52efba',0x52efba),'commit':('audio_ble_radio_recover_commit_52efec',0x52efec)}
 for kind in entries:
  for status in (0,7):
   results=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.mem_write(0x20001000,b'\x11\x22\x33\x44\x55\x66\x77\x88');calls=[]
    cut_x=(syms['audio_ble_radio_exchange_52e612']&~1) if is_c else 0x52e612
    cut_crc=(syms['codec_crc32']&~1) if is_c else 0x4d34f8
    def hook(uc,a,size,_):
     if a==cut_crc:
      calls.append(('crc',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),8)),uc.reg_read(UC_ARM_REG_R1)))
      uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     if a==cut_x:
      n=uc.reg_read(UC_ARM_REG_R2);cmd=bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),n));calls.append(('exchange',cmd))
      response=uc.reg_read(UC_ARM_REG_R3);uc.mem_write(response+7,b'ABCDEFGH')
      uc.reg_write(UC_ARM_REG_R0,status);uc.reg_write(UC_ARM_REG_R1,response);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,0x20001000)
    entry=syms[entries[kind][0]] if is_c else entries[kind][1]
    u.emu_start(entry|1,0x600000,count=5000)
    results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(0x20001000,8))))
   assert results[0]==results[1],(kind,status,results)
   print('PASS',kind,status,results[0])

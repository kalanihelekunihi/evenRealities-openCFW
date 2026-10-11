"""Actual ARM compiled-C/native comparisons for nonzero ATT record paths."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
uint8_t audio_ble_connection_records[0x100];
uint8_t audio_ble_registration_records[0x400];
uint8_t audio_ble_connection_state_table[0x100];
uint8_t *audio_ble_att_registration_invalid(uint8_t a,uint8_t b){(void)a;(void)b;return 0;}
uint32_t audio_ble_att_zero_connection_assert(uint16_t a){(void)a;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_att_registration_lookup',str(SRC/'display_ble_att_registration_valid.c'),str(SRC/'display_ble_att_connection_valid.c'),str(p),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for kind in ('active','lookup','valid'):
      for connection in (1,2,7):
       for active in (0,1) if kind=='active' else (1,):
        for state in (0,3) if kind=='valid' else (0,):
         for attr in (0x12,0x824) if kind=='valid' else (0x12,):
          rows=[]
          for compiled in (False,True):
           u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
           u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
           for a,d in segs:u.mem_write(a,d)
           conn=(syms['audio_ble_connection_records'] if compiled else 0x200712a4)
           reg=(syms['audio_ble_registration_records'] if compiled else 0x2006e5f0)
           table=(syms['audio_ble_connection_state_table'] if compiled else 0x20073e04)
           u.mem_write(conn+connection*0x30-0x1a,bytes([active]))
           u.mem_write(table+(connection-1)*2,bytes([1,state]))
           u.reg_write(UC_ARM_REG_R0,connection)
           u.reg_write(UC_ARM_REG_R1,attr if kind=='valid' else 2)
           u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
           start=(syms[{'active':'audio_ble_connection_record_active','lookup':'audio_ble_att_registration_lookup','valid':'audio_ble_att_connection_valid'}[kind]] if compiled else {'active':0x4b6ec6,'lookup':0x534f14,'valid':0x52c928}[kind])|1
           u.emu_start(start,0x600000,count=1500)
           value=u.reg_read(UC_ARM_REG_R0)
           rows.append(value-reg if kind=='lookup' else value)
          assert rows[0]==rows[1],(kind,connection,active,state,attr,rows)
          print('PASS',kind,connection,active,state,hex(attr),rows[0])

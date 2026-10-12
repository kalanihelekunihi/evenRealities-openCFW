#!/usr/bin/env python3
"""Compare defined ATT callback packet bytes and operation gate."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
S=[D/'display_ble_attc_exec_callback.c',D/'display_ble_att_exec_callback.c']
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text('#include <stdint.h>\nuint8_t audio_ble_att_common_state[0x64];\n');elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_attc_exec_callback_531ad6',*map(str,S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for operation in (1,4):
  for callback in (False,True):
   pair=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    state=sym['audio_ble_att_common_state'] if compiled else 0x200610ac
    u.mem_write(state+0x58,struct.pack('<I',0x100500|1 if callback else 0))
    trace=[]
    def receive(uc,pc,size,user):
     p=uc.reg_read(UC_ARM_REG_R0);data=bytes(uc.mem_read(p,16));trace.append(data[:4]+data[8:13]+data[14:16]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,receive,begin=0x100500,end=0x100500)
    u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_R1,operation);u.reg_write(UC_ARM_REG_R2,0x1234);u.reg_write(UC_ARM_REG_R3,0x77)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sym['audio_ble_attc_exec_callback_531ad6'] if compiled else 0x531ad6)|1,0x600000,count=1000)
    pair.append(trace)
   assert pair[0]==pair[1],(operation,callback,pair)
print('PASS_BLE_ATT_CALLBACK_NATIVE 4')

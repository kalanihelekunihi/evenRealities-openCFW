#!/usr/bin/env python3
"""Stock/C Cordio command packet effects through allocate/send ABI cuts."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_init_commands.c'
entries=[('HciLeRandCmd',0x52b304,None),('HciLeReadBufSizeCmd',0x52b31e,None),('HciLeReadLocalSupFeatCmd',0x52b338,None),('HciLeReadSupStatesCmd',0x52b37c,None),('HciLeReadWhiteListSizeCmd',0x52b396,None),('HciLeReadResolvingListSize',0x52b7dc,None),('HciLeReadMaxDataLen',0x52b24c,None),('HciReadBdAddrCmd',0x52b606,None),('HciLeSetEventMaskCmd',0x52b492,0x20010000),('HciSetEventMaskCmd',0x52b6bc,0x20010000),('HciSetEventMaskPage2Cmd',0x52b6e4,0x20010000),('HciLeWriteDefDataLen',0x52b1bc,(0x1234,0x5678)),('HciVscSetRfPowerLevelEx',0x4b4cb2,6),('HciVscSetRfPowerLevelEx',0x4b4cb2,100),('HciVscUpdateNvdsParam',0x4b4c8a,None)]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_ble_hci_cmd_alloc_52ae38(uint16_t a,uint16_t b){(void)a;(void)b;return 0;}
void audio_ble_hci_cmd_send(void*a){(void)a;}
''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,HciLeRandCmd',str(S),str(shim),'-o',str(e)],check=True)
 with e.open('rb') as f:
  x=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native,arg in entries:
  for alloc_ok in (False,True):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x20010000,bytes(range(8)));u.mem_write(0x20020000,b'\xa5'*24);u.mem_write(0x20074150,b'\xa5'*8)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if isinstance(arg,tuple):u.reg_write(UC_ARM_REG_R0,arg[0]);u.reg_write(UC_ARM_REG_R1,arg[1])
    elif arg is not None:u.reg_write(UC_ARM_REG_R0,arg)
    mapping=({sym['audio_ble_hci_cmd_alloc_52ae38']&~1:'alloc',sym['audio_ble_hci_cmd_send']&~1:'send'} if is_c else {0x52ae38:'alloc',0x52ae5e:'send'})
    events=[]
    def hook(uc,a,size,_):
     k=mapping.get(a)
     if k is None:return
     if k=='alloc':
      op=uc.reg_read(UC_ARM_REG_R0)&0xffff;length=uc.reg_read(UC_ARM_REG_R1)&0xffff
      events.append((k,op,length));ret=0x20020000 if alloc_ok else 0
      if ret:uc.mem_write(ret,struct.pack('<H',op)+bytes([length&0xff]))
     else:events.append((k,uc.reg_read(UC_ARM_REG_R0)));ret=0
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym[name] if is_c else native)|1,0x600000,count=3000)
    pair.append((events,bytes(u.mem_read(0x20020000,16)),bytes(u.mem_read(0x20074150,8)),u.reg_read(UC_ARM_REG_R0) if name=='HciVscSetRfPowerLevelEx' else None))
   assert pair[0]==pair[1],(name,arg,alloc_ok,pair)
   cases+=1
 for name,native in (('audio_ble_hci_read_max_data_len',0x569b2a),('audio_ble_hci_read_resolving_list_size',0x569b04)):
  for feature,capability in ((0,0),(0x20,0x20),(0x40,0x40),(0x60,0x60),(0x60,0)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segments:u.mem_write(a,d)
    u.mem_write(0x20071500,bytes([feature]));u.mem_write(0x20000028,bytes([capability]));u.mem_write(0x20071509,b'\xa5')
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    amap={sym['audio_ble_hci_cmd_alloc_52ae38']&~1:'alloc',sym['audio_ble_hci_cmd_send']&~1:'send'} if is_c else {0x52ae38:'alloc',0x52ae5e:'send'}
    events=[]
    def hook(uc,a,size,_):
     k=amap.get(a)
     if k is None:return
     if k=='alloc':events.append((k,uc.reg_read(UC_ARM_REG_R0)&0xffff));ret=0x20020000
     else:events.append((k,));ret=0
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym[name] if is_c else native)|1,0x600000,count=3000)
    pair.append((events,bytes(u.mem_read(0x20071509,1))))
   assert pair[0]==pair[1],(name,feature,capability,pair)
   cases+=1
 print('PASS_HCI_INIT_COMMANDS_NATIVE',cases)

"""Actual compiled-C/native 0x48162c target modes, slot writes and status."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_register.c'
SHIM='''#include <stdint.h>
volatile uint32_t audio_ble_hci_radio_dispatch_handlers_20068228[1024];
volatile uint32_t audio_ble_hci_radio_dispatch_contexts_20068928[1024];'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_register_48162c',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    h=syms['audio_ble_hci_radio_dispatch_handlers_20068228']
    c=syms['audio_ble_hci_radio_dispatch_contexts_20068928']
    for target in (0,1,2,3,255):
        for event in (0,1,31,32,0x75,0xff,0x100):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),
                               (target,event,0x12345678,0x87654321)):u.reg_write(r,v)
                writes=[]
                def hook(uc,access,addr,size,value,_):
                    if is_c:
                        if h<=addr<h+4096:addr=0x20068228+(addr-h)
                        elif c<=addr<c+4096:addr=0x20068928+(addr-c)
                        else:return
                    elif not (0x20068228<=addr<0x20069728):return
                    writes.append((addr,size,value&0xffffffff))
                u.hook_add(UC_HOOK_MEM_WRITE,hook)
                start=syms['audio_ble_hci_radio_register_48162c'] if is_c else 0x48162c
                u.emu_start(start|1,0x600000,count=100)
                traces.append((u.reg_read(UC_ARM_REG_R0),writes))
            assert traces[0]==traces[1],(target,event,traces)
    print('PASS 35 compiled-C/native dispatch-table registration cases')

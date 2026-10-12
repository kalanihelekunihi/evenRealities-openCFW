"""Bounded actual compiled ARM C/native 0x4b47cc return and log arguments."""
from pathlib import Path
import subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_revision_mismatch.c'
SHIM='''int audio_ble_hci_boot_log_4733ee(const char *s,...){(void)s;return 0;}'''

with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c'; stub.write_text(SHIM)
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_revision_mismatch_4b47cc',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(
        ['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:
        segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cases=[(0x01020304,0x01020304),(0x02000000,0x01000000),
           (0x01000000,0x02000000),(0x03000000,0x0200ffff),
           (0x00000100,0x00000200),(0x00000001,0x00000002)]
    for i in range(4):
        for j in range(4):
            cases.append((0x01020304 ^ (0xff<<(8*i)),
                          0x01020304 ^ (0x7f<<(8*j))))
    for radio,required in cases:
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000)
            u.mem_map(0x20000000,0x100000)
            for addr,data in segs:u.mem_write(addr,data)
            u.reg_write(UC_ARM_REG_SP,0x200ff000)
            u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,radio)
            u.reg_write(UC_ARM_REG_R1,required)
            logaddr=(syms['audio_ble_hci_boot_log_4733ee']&~1) if is_c else 0x4733ee
            calls=[]
            def hook(uc,addr,size,_):
                if addr!=logaddr:return
                p=uc.reg_read(UC_ARM_REG_R0)
                raw=bytes(uc.mem_read(p,80)).split(b'\0',1)[0]
                calls.append((raw,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            entry=syms['audio_ble_hci_radio_revision_mismatch_4b47cc'] if is_c else 0x4b47cc
            u.emu_start(entry|1,0x600000,count=300)
            traces.append((u.reg_read(UC_ARM_REG_R0),calls))
        assert traces[0]==traces[1],(hex(radio),hex(required),traces)
    print('PASS',len(cases),'compiled-C/native revision decisions and exact logger arguments')

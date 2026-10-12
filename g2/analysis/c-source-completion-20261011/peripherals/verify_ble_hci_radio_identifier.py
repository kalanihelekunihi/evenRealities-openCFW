"""Actual ARM compiled-C/native identifier dispatch and mode-zero byte effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_identifier.c'
SHIM='''void audio_ble_hci_radio_identifier_details_480874(void*p){(void)p;}
void audio_ble_hci_radio_identifier_caps_480c7c(void*p){(void)p;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_identifier_480d72',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cases=[(mode,word) for mode in (0,1,2,255) for word in (0,1,2,3,0x1fffff,0x555555,0xaaaaaa)]
    for mode,word in cases:
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            u.mem_map(0x40020000,0x10000);u.mem_write(0x40020014,struct.pack('<I',word))
            for a,d in segs:u.mem_write(a,d)
            out=0x20001000;u.mem_write(out,b'\xa5'*64)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,mode);u.reg_write(UC_ARM_REG_R1,out)
            calls=[]
            cuts={0x480874:'details',0x480c7c:'caps'} if not is_c else {
                syms['audio_ble_hci_radio_identifier_details_480874']&~1:'details',
                syms['audio_ble_hci_radio_identifier_caps_480c7c']&~1:'caps'}
            def hook(uc,a,size,_):
                if a not in cuts:return
                calls.append((cuts[a],uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_ble_hci_radio_identifier_480d72'] if is_c else 0x480d72
            u.emu_start(start|1,0x600000,count=400)
            traces.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(out,64)),calls))
        assert traces[0]==traces[1],(mode,hex(word),traces)
    print('PASS',len(cases),'compiled-C/native identifier dispatch and byte effects')

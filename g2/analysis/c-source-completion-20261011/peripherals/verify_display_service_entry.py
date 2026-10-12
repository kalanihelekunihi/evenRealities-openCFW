"""Actual compiled ARM C/native display service entry and framebuffer getter."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_service_entry.c'
SHIM='''void audio_uart_efs_service_init_458c48(void){}
void audio_uart_logger_cancel_ble_transmit_458e48(void){}'''
FUNCS={'service':(0x44227e,'audio_uart_display_service_prepare'),
       'framebuffer':(0x46ca6e,'audio_uart_display_pixel_format')}
NATIVE={'efs':0x458c48,'cancel':0x458e48}
NAMES={'efs':'audio_uart_efs_service_init_458c48',
       'cancel':'audio_uart_logger_cancel_ble_transmit_458e48'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_service_prepare',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for name,(native,csym) in FUNCS.items():
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                calls.append(mapping[a]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            u.emu_start((syms[csym] if is_c else native)|1,0x600000,count=40)
            traces.append((calls,u.reg_read(UC_ARM_REG_R0) if name=='framebuffer' else None))
        assert traces[0]==traces[1],(name,traces)
    print('PASS 2 compiled-C/native display service entry cases')

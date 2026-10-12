"""Connected actual compiled ARM C/native logger BLE cancellation effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_logger_ble_cancel.c'
SHIM='''#include <stdint.h>
volatile uint8_t audio_uart_logger_ble_enabled;
volatile uint32_t audio_uart_logger_ble_timeout;
uint8_t audio_uart_ble_logger_descriptor[20];
void audio_uart_logger_ble_handler_5bf972(void){}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}'''
NATIVE={'flags':0x43d0ce,'log':0x43d574,'compressed':0x43ce9e}
NAMES={'flags':'audio_log_flags','log':'audio_log_extended','compressed':'compressed_log_output'}
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_logger_cancel_ble_transmit_458e48',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for enabled,flags in ((0,7),(1,0),(1,1),(1,2),(1,4),(1,7)):
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            en=syms['audio_uart_logger_ble_enabled'] if is_c else 0x20074fe2
            timeout=syms['audio_uart_logger_ble_timeout'] if is_c else 0x200746b0
            pointer=syms['audio_uart_ble_logger_descriptor'] if is_c else 0x20073b90
            u.mem_write(en,bytes([enabled]));u.mem_write(timeout,struct.pack('<I',13))
            u.mem_write(pointer,b'\x00'*20)
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            mapping={((syms[NAMES[n]]&~1) if is_c else a):n for n,a in NATIVE.items()}
            calls=[]
            def hook(uc,a,size,_):
                if a not in mapping:return
                n=mapping[a]
                calls.append((n,uc.reg_read(UC_ARM_REG_R0) if n!='flags' else None))
                uc.reg_write(UC_ARM_REG_R0,flags if n=='flags' else 0)
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms['audio_uart_logger_cancel_ble_transmit_458e48'] if is_c else 0x458e48
            u.emu_start(start|1,0x600000,count=220)
            desc=bytes(u.mem_read(pointer,20))
            traces.append((calls,bytes(u.mem_read(en,1)),bytes(u.mem_read(timeout,4)),
                           desc[8],bool(struct.unpack_from('<I',desc,12)[0])))
        assert traces[0]==traces[1],(enabled,flags,traces)
    print('PASS 6 compiled-C/native logger BLE cancellation cases')

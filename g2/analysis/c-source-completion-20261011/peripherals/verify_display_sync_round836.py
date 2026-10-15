#!/usr/bin/env python3
"""Compare selected Apollo sync leaves against authenticated Thumb under Unicorn."""
from pathlib import Path
import hashlib, struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

root = Path(__file__).resolve().parents[3]
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
source = root / 'components/audio/uart_thread_source_candidate/display_sync_state.c'
stubs = '''#include <stdint.h>
volatile uint32_t audio_uart_lcd_status_cell;
volatile uint32_t audio_uart_display_audio_lock_cell;
volatile uint32_t audio_uart_display_audio_flag_cell;
int32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void*a){(void)a;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as directory:
    temp = Path(directory)
    stub = temp / 'stub.c'; stub.write_text(stubs)
    elf = temp / 'fixture.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_uart_display_audio_finalize',str(source),str(stub),
                    '-o',str(elf)],check=True)
    with elf.open('rb') as f:
        obj = ELFFile(f)
        segments = [(s['p_vaddr'],s.data()) for s in obj.iter_segments() if s['p_type']=='PT_LOAD']
        symbols = {s.name:s['st_value'] for s in obj.get_section_by_name('.symtab').iter_symbols()}
    functions = [('audio_uart_lcd_status',0x49eb8e),
                 ('audio_uart_display_audio_acquire_45baf0',0x45baf0),
                 ('audio_uart_display_audio_release_45bb58',0x45bb58),
                 ('audio_uart_display_audio_finalize',0x45bbd2)]
    cases = 0
    for name,native in functions:
        for mutex in (0,0x20070000):
            for flag in (0,1,2):
                for acquire_status,release_status in ((0,0),(4,0),(0,5),(4,5)):
                    for flags in (0,1,2,4,7):
                        pair = []
                        for compiled in (False,True):
                            u = Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
                            u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
                            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                            for address,data in segments:u.mem_write(address,data)
                            cells = ([symbols['audio_uart_lcd_status_cell'],
                                      symbols['audio_uart_display_audio_lock_cell'],
                                      symbols['audio_uart_display_audio_flag_cell']] if compiled else
                                     [0x20074edc,0x200749c8,0x200749e4])
                            for address,value in zip(cells,(0x12345678,mutex,flag)):
                                u.mem_write(address,struct.pack('<I',value))
                            trace=[]
                            hooks=[('acquire','audio_file_mutex_acquire',0x4497b6),
                                   ('release','audio_file_mutex_release',0x44981c),
                                   ('flags','audio_log_flags',0x43d0ce),
                                   ('extended','audio_log_extended',0x43d574),
                                   ('compact','compressed_log_output',0x43ce9e)]
                            for kind,symbol,native_hook in hooks:
                                address=symbols[symbol] if compiled else native_hook
                                def hook(uc,pc,width,user,kind=kind):
                                    regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
                                    if kind=='acquire':
                                        trace.append((kind,regs[0],regs[1]));uc.reg_write(UC_ARM_REG_R0,acquire_status)
                                    elif kind=='release':
                                        trace.append((kind,regs[0]));uc.reg_write(UC_ARM_REG_R0,release_status)
                                    elif kind=='flags':
                                        trace.append((kind,));uc.reg_write(UC_ARM_REG_R0,flags)
                                    elif kind=='extended':
                                        strings=tuple(bytes(uc.mem_read(a,140)).split(b'\0')[0] for a in regs[1:4])
                                        line,fmt=struct.unpack('<II',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8))
                                        trace.append((kind,regs[0],*strings,line,bytes(uc.mem_read(fmt,150)).split(b'\0')[0]))
                                    else:
                                        strings=tuple(bytes(uc.mem_read(a,150)).split(b'\0')[0] for a in regs[1:3])
                                        trace.append((kind,regs[0],*strings))
                                    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                                u.hook_add(UC_HOOK_CODE,hook,begin=address&~1,end=address&~1)
                            u.reg_write(UC_ARM_REG_SP,0x200ff000)
                            u.reg_write(UC_ARM_REG_LR,0x600001)
                            start=(symbols[name] if compiled else native)|1
                            try:u.emu_start(start,0x600000,count=10000)
                            except Exception as error:
                                raise AssertionError((name,mutex,flag,acquire_status,release_status,flags,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from error
                            pair.append((u.reg_read(UC_ARM_REG_R0) if name=='audio_uart_lcd_status' else None,
                                         trace,struct.unpack('<I',u.mem_read(cells[2],4))[0]))
                        assert pair[0]==pair[1],(name,mutex,flag,acquire_status,release_status,flags,pair)
                        cases+=1
print('PASS_DISPLAY_SYNC_NATIVE',cases)

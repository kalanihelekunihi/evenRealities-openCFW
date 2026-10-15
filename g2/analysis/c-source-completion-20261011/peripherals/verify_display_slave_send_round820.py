#!/usr/bin/env python3
"""Compare compiled C and Apollo display-send entrypoints under controlled leaves."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *

root = Path(__file__).resolve().parents[3]
image = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(image).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
source = root / 'components/audio/uart_thread_source_candidate/display_slave_send.c'
stub_text = '''#include <stdint.h>
void *g2_display_queue; void *g2_display_sender_mutex; uint32_t g2_display_ring[5];
int32_t audio_file_mutex_acquire(void*a,uint32_t b){(void)a;(void)b;return 0;}
int32_t audio_file_mutex_release(void*a){(void)a;return 0;}
uint32_t audio_uart_input_ring_write(void*a,const void*b,uint32_t c){(void)a;(void)b;return c;}
int32_t audio_cmsis_queue_put(void*a,const void*b,uint8_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
int32_t audio_ble_hci_boot_log_4733ee(const void*a,...){(void)a;return 0;}
void audio_delay_scheduler_assert(void){}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
entries = [('audio_uart_slave_display_start', 0x4441ec),
           ('audio_uart_slave_display_refresh', 0x4442d0),
           ('audio_uart_slave_display_stop', 0x4443cc),
           ('audio_uart_slave_display_control', 0x4444b8)]
with tempfile.TemporaryDirectory() as temp:
    tmp = Path(temp)
    stub = tmp / 'stub.c'; stub.write_text(stub_text)
    elf = tmp / 'fixture.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb', '-O2',
                    '-nostdlib', '-Wl,-Ttext=0x100000', '-Wl,-e,audio_uart_slave_display_start',
                    str(source), str(stub), '-o', str(elf)], check=True)
    with elf.open('rb') as handle:
        parsed = ELFFile(handle)
        segments = [(s['p_vaddr'], s.data()) for s in parsed.iter_segments() if s['p_type'] == 'PT_LOAD']
        symbols = {s.name:s['st_value'] for s in parsed.get_section_by_name('.symtab').iter_symbols()}
    for name, native in entries:
        for size in (0, 1, 12, 0x2800, 0x2801, 0xffffffff):
            for level in (0, 1, 2, 4, 7):
              for queue_status in (0, 1):
                pair = []
                for compiled in (False, True):
                    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
                    u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, image)
                    u.mem_map(0x100000, 0x100000); u.mem_map(0x20000000, 0x100000)
                    for addr, data in segments: u.mem_write(addr, data)
                    queue_cell = symbols['g2_display_queue'] if compiled else 0x200744e4
                    mutex_cell = symbols['g2_display_sender_mutex'] if compiled else 0x200744e8
                    ring = symbols['g2_display_ring'] if compiled else 0x20073b60
                    u.mem_write(queue_cell, (0x20071000).to_bytes(4, 'little'))
                    u.mem_write(mutex_cell, (0x20071004).to_bytes(4, 'little'))
                    payload = 0x20080000; u.mem_write(payload, bytes(range(32)))
                    trace = []
                    cuts = [('zero','',0x43c0e4),
                            ('acquire','audio_file_mutex_acquire',0x4497b6),
                            ('release','audio_file_mutex_release',0x44981c),
                            ('ring','audio_uart_input_ring_write',0x46d8c4),
                            ('queue','audio_cmsis_queue_put',0x449abe),
                            ('level','audio_log_level',0x43d0ce),
                            ('extended','audio_log_extended',0x43d574),
                            ('compact','compressed_log_output',0x43ce9e),
                            ('failure_log','audio_ble_hci_boot_log_4733ee',0x4733ee),
                            ('assert','audio_delay_scheduler_assert',0x5fa0a4)]
                    for kind, symbol, stock_addr in cuts:
                        if compiled and kind == 'zero': continue
                        addr = symbols[symbol] if compiled else stock_addr
                        def hook(uc, pc, width, user, kind=kind):
                            r0 = uc.reg_read(UC_ARM_REG_R0)
                            r1 = uc.reg_read(UC_ARM_REG_R1)
                            r2 = uc.reg_read(UC_ARM_REG_R2)
                            r3 = uc.reg_read(UC_ARM_REG_R3)
                            if kind == 'zero': uc.mem_write(r0, bytes([r2 & 255]) * r1)
                            elif kind == 'acquire': trace.append(('acquire',r0,r1))
                            elif kind == 'release': trace.append(('release',r0))
                            elif kind == 'ring': trace.append(('ring',r0,r1,r2))
                            elif kind == 'queue':
                                trace.append(('queue',r0,bytes(uc.mem_read(r1,12)),r2,r3))
                                uc.reg_write(UC_ARM_REG_R0,queue_status)
                            elif kind == 'level': trace.append(('level',)); uc.reg_write(UC_ARM_REG_R0,level)
                            elif kind == 'extended': trace.append(('extended',r0))
                            elif kind == 'compact': trace.append(('compact',r0))
                            elif kind == 'failure_log':
                                raw=bytes(uc.mem_read(r0,96)).split(b'\0')[0]
                                trace.append(('failure_log',raw))
                            elif kind == 'assert':
                                trace.append(('assert',))
                                uc.reg_write(UC_ARM_REG_R0,0)
                                uc.reg_write(UC_ARM_REG_PC,0x600000)
                                return
                            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
                        u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
                    u.reg_write(UC_ARM_REG_SP,0x200ff000)
                    u.reg_write(UC_ARM_REG_LR,0x600001)
                    if name == 'audio_uart_slave_display_control':
                        args = (payload,size)
                    else:
                        args = (0x1234,payload,size)
                    for reg,arg in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args): u.reg_write(reg,arg)
                    try:
                        u.emu_start((symbols[name] if compiled else native)|1,0x600000,count=10000)
                    except Exception as error:
                        raise AssertionError((name,size,level,queue_status,compiled,hex(u.reg_read(UC_ARM_REG_PC)),trace)) from error
                    normalized = []
                    for item in trace:
                        if item[0] in ('acquire','release'):
                            normalized.append((item[0],0x20071004,*item[2:]))
                        elif item[0] == 'ring': normalized.append(('ring',0x20073b60,*item[2:]))
                        else: normalized.append(item)
                    result = None if queue_status and size <= 0x2800 else u.reg_read(UC_ARM_REG_R0)
                    pair.append((result,normalized))
                assert pair[0] == pair[1], (name,size,level,queue_status,pair)
print('PASS_DISPLAY_SLAVE_SEND_NATIVE', len(entries)*6*5*2)

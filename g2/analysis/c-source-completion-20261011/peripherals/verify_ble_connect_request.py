"""Compiled C/native _connectParamReq role, connection and WSF message paths."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t controller[128],msg[12];uint8_t *audio_ble_controller=controller;
volatile uint32_t conn,terminal_mode,alloc_fail,sends,send_handler;
void *audio_ble_dm_conn_params(void){return conn?(void *)0x20084000:0;}
uint32_t audio_settings_terminal_mode(void){return terminal_mode;}
void *audio_wsf_msg_alloc(uint32_t n){(void)n;return alloc_fail?0:msg;}
void audio_wsf_msg_send(uint8_t h,void *m){(void)m;sends++;send_handler=h;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_connect_param_request',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_connect_request.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,controller,handler,conn,terminal,mode,alloc_fail):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        wr(syms['audio_ble_controller'],syms['controller'] if controller else 0);u.mem_write(syms['controller']+0x56,bytes([handler]))
        wr(0x200727f0,0x20083000 if controller else 0);u.mem_write(0x20083056,bytes([handler]))
        for n,v in [('conn',conn),('terminal_mode',terminal),('alloc_fail',alloc_fail)]:wr(syms[n],v)
        u.reg_write(UC_ARM_REG_R0,mode);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                result=None
                if a==0x43d0ce:result=0
                elif a==0x4b8122:result=0x20083000 if controller else 0
                elif a==0x46efcc:result=0x20084000 if conn else 0
                elif a==0x46c630:result=terminal
                elif a==0x4bf99e:result=0 if alloc_fail else 0x20085000
                elif a==0x4bf9ba:wr(syms['sends'],rd(syms['sends'])+1);wr(syms['send_handler'],uc.reg_read(UC_ARM_REG_R0));result=0
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_ble_connect_param_request'] if c else 0x47761c)|1,0x600000,count=4000)
        return rd(syms['sends']),rd(syms['send_handler']),bytes(u.mem_read(syms['msg'] if c else 0x20085000,12))
    for case in [(False,1,1,0,0xa3,0),(True,0,1,0,0xa3,0),(True,7,0,0,0xa3,0),(True,7,1,1,0xa4,0),(True,7,1,0,0xa3,1),(True,7,1,0,0xa3,0)]:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
        print('PASS BLE connect request',case)

"""Compiled C/native ESS fast-mode throttle and delayed-event scheduling."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
volatile uint8_t audio_ble_fast_mode_throttle_enabled;
uint32_t audio_ble_fast_mode_last_reject_tick;
volatile uint32_t tick,removed,pushed,arg_event,arg_delay;
void audio_ble_fast_mode_event(void){}
uint32_t g2_flashdb_candidate_tick(void){return tick;}
void audio_event_loop_remove_delayed(void (*f)(void)){(void)f;removed++;}
void audio_event_loop_push_delayed(void (*f)(void),uint32_t a,uint32_t b){(void)f;pushed++;arg_event=a;arg_delay=b;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_set_fast_mode',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_fast_mode.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,enabled,last,tick):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v));rd=lambda a:struct.unpack('<I',u.mem_read(a,4))[0]
        u.mem_write(syms['audio_ble_fast_mode_throttle_enabled'],bytes([enabled]));wr(syms['audio_ble_fast_mode_last_reject_tick'],last);wr(syms['tick'],tick)
        u.mem_write(0x20074f90,bytes([enabled]));wr(0x20074340,last)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                result=None
                if a==0x4490cc:result=tick
                elif a==0x43d0ce:result=0
                elif a==0x476ace:wr(syms['removed'],rd(syms['removed'])+1);result=0
                elif a==0x47697e:
                    wr(syms['pushed'],rd(syms['pushed'])+1);wr(syms['arg_event'],uc.reg_read(UC_ARM_REG_R1));wr(syms['arg_delay'],uc.reg_read(UC_ARM_REG_R2));result=0
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_ble_set_fast_mode'] if c else 0x478160)|1,0x600000,count=3000)
        return tuple(rd(syms[n]) for n in ['removed','pushed','arg_event','arg_delay'])
    for case in [(0,100,150),(1,0,150),(1,100,150),(1,100,30100),(1,0xfffffff0,20)]:
        a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
        print('PASS BLE fast mode',case)

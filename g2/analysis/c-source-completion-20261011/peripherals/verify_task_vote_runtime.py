"""Actual compiled ARM C/native task-vote slot and transition effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/task_vote_runtime.c'
SHIM='''#include <stdint.h>
volatile uint8_t audio_task_vote_state_200700e0[0x105];
void *receiver_current_task(void){return (void*)0x1234;}
uint32_t g2_gpio_critical_save(void){return 0;}
void g2_power_critical_restore(uint32_t p){(void)p;}'''
with tempfile.TemporaryDirectory() as td:
    stub=Path(td)/'stub.c';stub.write_text(SHIM);elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                    '-Wl,-Ttext=0x100000','-Wl,-e,task_vote_acquire_current',
                    str(SRC),str(stub),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    funcs={'find':(0x46d67c,'task_vote_find_slot'),'free':(0x46d69a,'task_vote_find_free_slot'),
           'acquire':(0x46d70e,'task_vote_acquire_for_handle'),
           'release':(0x46d78c,'task_vote_release_for_handle'),
           'acquire_current':(0x46d816,'task_vote_acquire_current'),
           'release_current':(0x46d826,'task_vote_release_current')}
    fixtures=[]
    for kind in funcs:
        for scenario in ('disabled','empty','existing_off','existing_on','full'):
            fixtures.append((kind,scenario))
    for kind,scenario in fixtures:
        traces=[]
        for is_c in (False,True):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
            u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
            for a,d in segs:u.mem_write(a,d)
            state=syms['audio_task_vote_state_200700e0'] if is_c else 0x200700e0
            buf=bytearray(0x105);buf[0x104]=0 if scenario=='disabled' else 1
            if scenario.startswith('existing'):
                struct.pack_into('<I',buf,0,0x1234)
                buf[4]=1 if scenario=='existing_on' else 0
                struct.pack_into('<I',buf,0x100,buf[4])
            elif scenario=='full':
                for i in range(32):struct.pack_into('<I',buf,i*8,0x2000+i)
            u.mem_write(state,bytes(buf))
            u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
            u.reg_write(UC_ARM_REG_R0,0x1234)
            native_get=0x4491aa; native_save=0x473940
            c_get=syms['receiver_current_task']&~1;c_save=syms['g2_gpio_critical_save']&~1
            calls=[]
            def hook(uc,a,size,_):
                if not is_c and a in (0x46d782,0x46d7dc):
                    # Unicorn does not execute MSR PRIMASK in this Thumb setup.
                    # Source restore lower is also effect-cut; compare RAM/ABI.
                    uc.reg_write(UC_ARM_REG_PC,(a+4)|1)
                    return
                if a==(c_get if is_c else native_get):
                    calls.append('get');uc.reg_write(UC_ARM_REG_R0,0x1234)
                elif a==(c_save if is_c else native_save):
                    calls.append('save');uc.reg_write(UC_ARM_REG_R0,0)
                else:return
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook)
            start=syms[funcs[kind][1]] if is_c else funcs[kind][0]
            try:u.emu_start(start|1,0x600000,count=1500)
            except Exception as exc:
                raise RuntimeError((kind,scenario,is_c,hex(u.reg_read(UC_ARM_REG_PC)))) from exc
            result=u.reg_read(UC_ARM_REG_R0) if not kind.endswith('_current') else None
            traces.append((result,bytes(u.mem_read(state,0x105)),calls))
        assert traces[0]==traces[1],(kind,scenario,traces[0][0],traces[1][0],traces[0][2],traces[1][2])
    print('PASS',len(fixtures),'compiled-C/native task-vote lookup and transitions')

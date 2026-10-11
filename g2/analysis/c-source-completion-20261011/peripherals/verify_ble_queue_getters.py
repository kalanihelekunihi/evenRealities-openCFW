"""Compiled C/native CMSIS queue count/capacity, task and IRQ paths."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
volatile uint32_t irq,task_value,isr_value;
uint32_t audio_irq_context(void){return irq;}
uint32_t uxQueueMessagesWaiting(void *q){(void)q;return task_value;}
uint32_t uxQueueMessagesWaitingFromISR(void *q){(void)q;return isr_value;}
''')
    elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_cmsis_queue_get_count',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_queue_getters.c'),str(shim),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(c,which,nonnull,irq):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x100000);wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        wr(syms['irq'],irq);wr(syms['task_value'],5);wr(syms['isr_value'],7);wr(0x2008103c,11)
        u.reg_write(UC_ARM_REG_R0,0x20081000 if nonnull else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if not c:
            def cut(uc,a,size,_):
                result={0x44900e:irq,0x441e66:5,0x441e8a:7}.get(a)
                if result is None:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((syms['audio_cmsis_queue_get_'+which] if c else (0x449bc8 if which=='count' else 0x449bbc))|1,0x600000,count=1000)
        return u.reg_read(UC_ARM_REG_R0)
    for which in ['count','capacity']:
        for nonnull,irq in [(False,0),(True,0),(True,1)]:
            a=run(False,which,nonnull,irq);b=run(True,which,nonnull,irq)
            assert a==b,(which,nonnull,irq,a,b)
        print('PASS BLE queue',which,'3/3')

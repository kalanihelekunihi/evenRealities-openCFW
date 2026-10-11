"""Actual compiled C/native FreeRTOS timer constructor and ID bounded cases."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t alloc;volatile uint32_t calls[4];
void *pvPortMalloc(uint32_t n){calls[0]++;calls[1]=n;return (void *)alloc;}
void audio_daemon_initialize_queue(void){calls[2]++;}
void stock_enter_critical(void){calls[2]++;}
void stock_exit_critical(void){calls[3]++;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_freertos_timer_create_dynamic',str(ROOT/'components/audio/uart_thread_source_candidate/cmsis_timer_freertos.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,kind,storage,auto):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        u.mem_write(0x20071000,b'\xaa'*44);wr(symbols['alloc'],storage)
        args=[0x100900,1,auto,0x20072001]
        for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        wr(0x200ff000,0x100a01);wr(0x200ff004,0x20071000)
        if kind=='static':
            # Sixth argument lies at incoming SP+4.
            pass
        if kind=='id':u.reg_write(UC_ARM_REG_R0,0x20071000);wr(0x20071000+28,0x20072001)
        if not candidate:
            def cut(uc,address,size,_):
                out=symbols['calls'];get=lambda i:struct.unpack('<I',uc.mem_read(out+4*i,4))[0];put=lambda i,v:wr(out+4*i,v)
                if address==0x456110:put(0,get(0)+1);put(1,uc.reg_read(UC_ARM_REG_R0));result=storage
                elif address==0x47eab8:put(2,get(2)+1);result=0
                elif address==0x4420d0:put(2,get(2)+1);result=0
                elif address==0x4420e8:put(3,get(3)+1);result=0
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        native={'dynamic':0x47e6dc,'static':0x47e712,'id':0x47eb26}
        names={'dynamic':'audio_freertos_timer_create_dynamic','static':'audio_freertos_timer_create_static','id':'audio_freertos_timer_get_id'}
        u.emu_start((symbols[names[kind]] if candidate else native[kind])|1,0x600000,count=1000)
        payload=bytes(u.mem_read(0x20071000,44)) if kind!='id' and (storage or kind=='static') else b''
        return u.reg_read(UC_ARM_REG_R0),payload,bytes(u.mem_read(symbols['calls'],16))
    for case in [('dynamic',0,0),('dynamic',0x20071000,0),('dynamic',0x20071000,1),('static',0x20071000,0),('static',0x20071000,1),('id',0,0)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS timer FreeRTOS',case)

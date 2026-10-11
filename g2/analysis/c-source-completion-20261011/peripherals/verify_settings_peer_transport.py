"""Actual C/native peer packet allocation, enqueue, and cleanup paths."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void *audio_settings_peer_send_queue,*audio_settings_peer_event;
uint32_t alloc_index,node_alloc,payload_alloc;int32_t queue_result;volatile uint32_t calls[8];
void *audio_uart_alloc_retry(uint32_t n){uint32_t i=alloc_index++;calls[i]=n;return (void *)(i?payload_alloc:node_alloc);}
void audio_file_heap_free(void *p){calls[2]++;calls[3]=(uint32_t)p;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){volatile uint8_t *d=p;for(uint32_t i=0;i<n;i++)d[i]=(uint8_t)v;}
void *audio_queue_copy_bytes(void *p,const void *s,uint32_t n){volatile uint8_t *d=p;const volatile uint8_t *a=s;for(uint32_t i=0;i<n;i++)d[i]=a[i];return p;}
int32_t audio_cmsis_queue_put(void *q,const void *p,uint8_t pr,uint32_t timeout){(void)q;(void)pr;calls[4]++;calls[5]=timeout;calls[6]=*(uint32_t *)p;return queue_result;}
uint32_t g2_log_event_set_task(uint32_t h,uint32_t mask){calls[7]++;(void)h;return mask;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_send_peer_packet',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_peer_transport.c'),str(shim),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,queue,node,payload,queue_result):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,data in segments:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        wr=lambda a,v:u.mem_write(a,struct.pack('<I',v))
        values={'audio_settings_peer_send_queue':queue,'audio_settings_peer_event':0x20077000,'node_alloc':node,'payload_alloc':payload,'queue_result':queue_result&0xffffffff}
        for name,value in values.items():wr(symbols[name],value)
        wr(0x200749cc,queue);wr(0x20074b10,0x20077000)
        u.mem_write(0x20081000,bytes(range(48)));u.mem_write(0x20082000,b'\xaa'*12);u.mem_write(0x20083000,b'\xbb'*56)
        for reg,value in [(UC_ARM_REG_R0,9),(UC_ARM_REG_R1,0x20081000),(UC_ARM_REG_R2,48),(UC_ARM_REG_R3,0),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,value)
        wr(0x200ff000,5)
        if not candidate:
            def cut(uc,address,size,_):
                c=symbols['calls'];read=lambda i:struct.unpack('<I',uc.mem_read(c+4*i,4))[0];put=lambda i,v:wr(c+4*i,v)
                r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
                if address==0x43d0ce:result=0
                elif address==0x4646f0:
                    i=struct.unpack('<I',uc.mem_read(symbols['alloc_index'],4))[0];wr(symbols['alloc_index'],i+1);put(i,r0);result=payload if i else node
                elif address==0x474d16:put(2,read(2)+1);put(3,r0);result=0
                elif address==0x43c0e4:uc.mem_write(r0,bytes([r2&255])*r1);result=r0
                elif address==0x439be4:uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));result=r0
                elif address==0x449abe:put(4,read(4)+1);put(5,uc.reg_read(UC_ARM_REG_R3));put(6,struct.unpack('<I',uc.mem_read(r1,4))[0]);result=queue_result&0xffffffff
                elif address==0x4495e4:put(7,read(7)+1);result=r1
                else:return
                uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,cut)
        u.emu_start((symbols['audio_settings_send_peer_packet'] if candidate else 0x465480)|1,0x600000,count=2000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20082000,12)),bytes(u.mem_read(0x20083000,56)),bytes(u.mem_read(symbols['calls'],32))
    cases=[(0,0,0,0),(0x20076000,0,0,0),(0x20076000,0x20082000,0,0),
           (0x20076000,0x20082000,0x20083000,0),(0x20076000,0x20082000,0x20083000,-2)]
    for case in cases:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS peer transport',case)

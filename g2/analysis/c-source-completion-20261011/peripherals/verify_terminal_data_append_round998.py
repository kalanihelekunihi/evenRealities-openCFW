#!/usr/bin/env python3
"""Native/C agent-content append branch and ring-state parity."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-data-append-round998';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_data_append_agent_content.c'
base=root/'build/c-firmware/terminal-agent-content-round997/apollo-main-terminal-agent-content.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'terminal_data_append_agent_content.o';linked=out/'apollo-main-terminal-data-append.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
                '-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_td_state[0xa1dc];
void audio_td_session_ring_reset(void){}
uint32_t audio_td_session_find_by_id(uint8_t*a,uint32_t b,uint16_t*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_td_ring_index_wrap(uint8_t*a,uint16_t b){(void)a;(void)b;return 0;}
uint32_t audio_td_record_build_from_event(uint8_t*a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;return d;}
uint8_t *audio_td_session_ring_append(uint8_t a,uint8_t*b){(void)a;(void)b;return 0;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_terminal_data_append_agent_content',
                    str(src),str(shim),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def one(compiled,present,out_present,initialized,session,is_new,append_ptr,kind,found,log_flags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x200000)
        state=syms['audio_td_state'] if compiled else 0x2010fd20
        ring=state+0x1054;row=ring+3*0x214;append_row=ring+0x100
        u.mem_write(ring+0x8504,(1 if initialized else 0).to_bytes(4,'little'))
        u.mem_write(ring+0x8500,(4).to_bytes(2,'little'))
        u.mem_write(row,bytes([0xa5])*0x214)
        u.mem_write(append_row,bytes([0x3c])*0x214)
        payload=0x2001f000;packet=bytearray(0x214)
        packet[0x204]=1 if is_new else 0
        packet[0x208:0x20c]=session.to_bytes(4,'little')
        u.mem_write(payload,bytes(packet))
        out_ptr=0x2001f300;u.mem_write(out_ptr,b'\x44\x44')
        names={'reset':'audio_td_session_ring_reset','find':'audio_td_session_find_by_id',
               'wrap':'audio_td_ring_index_wrap','build':'audio_td_record_build_from_event',
               'append':'audio_td_session_ring_append','zero':'audio_uart_buffer_zero',
               'flags':'audio_log_flags','extended':'audio_log_extended','compact':'compressed_log_output'}
        native={'reset':0x5970c0,'find':0x59726e,'wrap':0x5970a8,'build':0x5972ce,
                'append':0x5979ce,'zero':0x43c0e4,'flags':0x43d0ce,
                'extended':0x43d574,'compact':0x43ce9e}
        trace=[]
        for kind_name,address in native.items():
            addr=syms[names[kind_name]] if compiled else address
            def hook(cpu,at,size,user,kind_name=kind_name):
                r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
                r2=cpu.reg_read(A.UC_ARM_REG_R2)
                if kind_name=='reset':
                    trace.append(('reset',));cpu.mem_write(ring+0x8504,(1).to_bytes(4,'little'))
                elif kind_name=='find':
                    trace.append(('find',r1));cpu.mem_write(r2,(2).to_bytes(2,'little'))
                    cpu.reg_write(A.UC_ARM_REG_R0,1 if found else 0)
                elif kind_name=='wrap':trace.append(('wrap',r1));cpu.reg_write(A.UC_ARM_REG_R0,3)
                elif kind_name=='append':
                    trace.append(('append',r0));cpu.mem_write(r1,bytes([kind]))
                    cpu.reg_write(A.UC_ARM_REG_R0,append_row if append_ptr else 0)
                elif kind_name=='build':
                    trace.append(('build',r0-ring,r2));cpu.mem_write(r0,b'\x55')
                elif kind_name=='zero':
                    trace.append(('zero',r0-ring,r1));cpu.mem_write(r0,b'\0'*r1)
                elif kind_name=='flags':cpu.reg_write(A.UC_ARM_REG_R0,log_flags)
                elif kind_name=='extended':
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    line=int.from_bytes(cpu.mem_read(sp,4),'little')
                    fmt=int.from_bytes(cpu.mem_read(sp+4,4),'little')
                    value=int.from_bytes(cpu.mem_read(sp+8,4),'little')
                    message=bytes(cpu.mem_read(fmt,90)).split(b'\0')[0]
                    trace.append(('extended',r0,line,message,value))
                elif kind_name=='compact':
                    message=bytes(cpu.mem_read(r1,100)).split(b'\0')[0]
                    trace.append(('compact',r0,message,cpu.reg_read(A.UC_ARM_REG_R3)))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
        u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        u.reg_write(A.UC_ARM_REG_R0,payload if present else 0)
        u.reg_write(A.UC_ARM_REG_R1,out_ptr if out_present else 0)
        u.emu_start((syms['audio_terminal_data_append_agent_content'] if compiled else 0x597a96)|1,
                    0x600000,count=3000)
        return (u.reg_read(A.UC_ARM_REG_R0)&0xff,trace,bytes(u.mem_read(out_ptr,2)),
                bytes(u.mem_read(row,0x214)),bytes(u.mem_read(append_row,0x214)))
    cases=0
    for present in (False,True):
     for out_present in (False,True):
      for initialized in (False,True):
       for session in (0,0x1234):
        for is_new in (False,True):
         for append_ptr in (False,True):
          for kind in (1,3):
           for found in (False,True):
            for log_flags in (0,1,2,4,7):
             pair=[one(c,present,out_present,initialized,session,is_new,append_ptr,kind,found,log_flags) for c in (False,True)]
             assert pair[0]==pair[1],(present,out_present,initialized,session,is_new,append_ptr,kind,found,log_flags,pair[:2])
             cases+=1
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_data_append_agent_content'}
new={'audio_td_session_find_by_id','audio_td_ring_index_wrap','audio_td_record_build_from_event','audio_td_session_ring_append'}
assert after-before==new,(after-before)
receipt={'round':998,'status':'PASS_TERMINAL_DATA_APPEND_LOGGING','component':'Apollo terminal agent data append 0x597a96',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cases':cases,
         'validation':'M55 strict compile and native/C ring, index, return, child-call and absent-session logging parity',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Four lower ring/session providers remain open',
                  'Absolute RAM placement and whole image/hardware remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases,len(before),len(after),receipt['linked_sha256'])

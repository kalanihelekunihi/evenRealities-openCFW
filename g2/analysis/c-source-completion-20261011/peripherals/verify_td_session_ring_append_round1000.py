#!/usr/bin/env python3
"""Native/C terminal session ring append and overwrite parity."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/td-session-ring-append-round1000';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/td_session_ring_append.c'
wrap=root/'components/audio/uart_thread_source_candidate/td_session_find_by_id.c'
base=root/'build/c-firmware/td-session-find-round999/apollo-main-td-session-find.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'td_session_ring_append.o';linked=out/'apollo-main-td-session-ring-append.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
                '-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_td_state[0xa1dc];
void audio_td_session_ring_reset(void){}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_td_session_ring_append',
                    str(src),str(wrap),str(shim),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def one(compiled,sequence,count,head,next_id,continue_last,out_present):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x200000)
        state=syms['audio_td_state'] if compiled else 0x2010fd20
        ring=state+0x1054
        u.mem_write(ring,bytes([0xa5])*0x850c)
        u.mem_write(ring+0x8500,count.to_bytes(2,'little'))
        u.mem_write(ring+0x8502,head.to_bytes(2,'little'))
        u.mem_write(ring+0x8504,sequence.to_bytes(4,'little'))
        u.mem_write(ring+0x8508,next_id.to_bytes(4,'little'))
        output=0x2001f000;u.mem_write(output,b'\xee')
        trace=[]
        names={'reset':'audio_td_session_ring_reset','zero':'audio_uart_buffer_zero'}
        native={'reset':0x5970c0,'zero':0x43c0e4}
        for kind,addr in native.items():
            address=syms[names[kind]] if compiled else addr
            def hook(cpu,at,size,user,kind=kind):
                r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
                if kind=='reset':
                    trace.append(('reset',))
                    cpu.mem_write(ring,b'\0'*0x850c)
                    cpu.mem_write(ring+0x8504,(1).to_bytes(4,'little'))
                    cpu.mem_write(ring+0x8508,(1).to_bytes(4,'little'))
                else:
                    trace.append(('zero',r0-ring,r1))
                    cpu.mem_write(r0,b'\0'*r1)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook,begin=address&~1,end=address&~1)
        u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        u.reg_write(A.UC_ARM_REG_R0,continue_last)
        u.reg_write(A.UC_ARM_REG_R1,output if out_present else 0)
        u.emu_start((syms['audio_td_session_ring_append'] if compiled else 0x5979ce)|1,
                    0x600000,count=2000)
        row=u.reg_read(A.UC_ARM_REG_R0)
        return (row-ring,trace,bytes(u.mem_read(output,1)),
                bytes(u.mem_read(ring+0x8500,12)),bytes(u.mem_read(row,0x214)))
    cases=0
    for sequence in (0,1,0x1234):
     for count in (0,1,63,64,65):
      for head in (0,1,63):
       for next_id in (0,1,0xffffffff):
        for continue_last in (0,1):
         for out_present in (False,True):
            pair=[one(c,sequence,count,head,next_id,continue_last,out_present) for c in (False,True)]
            assert pair[0]==pair[1],(sequence,count,head,next_id,continue_last,out_present,pair)
            cases+=1
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_td_session_ring_append'} and not after-before
receipt={'round':1000,'status':'PASS_TD_SESSION_RING_APPEND','component':'Apollo session ring append 0x5979ce',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cases':cases,
         'validation':'M55 strict compile and native/C append, continue, overwrite, reset, row and output parity',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Record builder 0x5972ce and full image/RAM placement remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases,len(before),len(after),receipt['linked_sha256'])

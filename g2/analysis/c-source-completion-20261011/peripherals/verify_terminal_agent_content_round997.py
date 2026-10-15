#!/usr/bin/env python3
"""Bounded native/C terminal agent-content state and child-call parity."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-agent-content-round997';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_command_5e9390.c'
base=root/'build/c-firmware/terminal-agent-tokens-round996/apollo-main-terminal-agent-tokens.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'terminal_command_5e9390.o';linked=out/'apollo-main-terminal-agent-content.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
                '-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_terminal_ui_mode;
struct audio_terminal_output_tracking {uint8_t active;uint8_t reserved[3];uint32_t count;};
struct audio_terminal_output_tracking audio_terminal_output_tracking;
uint32_t audio_terminal_message_session_matches(uint32_t a,const char*b){(void)a;(void)b;return 0;}
uint8_t audio_terminal_data_append_agent_content(const void*a,uint16_t*b){(void)a;(void)b;return 0;}
uint32_t audio_terminal_agent_text_token(uint8_t a,uint16_t b){(void)a;(void)b;return 0;}
uint32_t audio_terminal_agent_trigger_token(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_terminal_request_display(uint8_t a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t g2_flashdb_candidate_tick(void){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
''')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_terminal_command_5e9390',
                    str(src),str(shim),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def one(compiled,present,match,text_len,append,event,mode,session,active,previous,now,log_flags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x200000)
        state=syms['audio_terminal_ui_mode'] if compiled else 0x2006e345
        tracking=syms['audio_terminal_output_tracking'] if compiled else 0x2006e364
        u.mem_write(state,bytes([mode]));u.mem_write(tracking,bytes([active])+b'\0'*3+previous.to_bytes(4,'little'))
        payload=0x2001f000;packet=bytearray(0x214)
        packet[0]=0;packet[2:4]=text_len.to_bytes(2,'little')
        packet[0x204]=0x41;packet[0x208:0x20c]=session.to_bytes(4,'little')
        packet[0x20c]=event;packet[0x210:0x214]=(0x12345678).to_bytes(4,'little')
        u.mem_write(payload,bytes(packet))
        native={'match':0x5e818a,'append':0x597a96,'text':0x5e5166,'trigger':0x5e51b0,
                'request':0x5e43d2,'tick':0x4490cc,'flags':0x43d0ce,
                'extended':0x43d574,'compact':0x43ce9e}
        names={'match':'audio_terminal_message_session_matches',
               'append':'audio_terminal_data_append_agent_content',
               'text':'audio_terminal_agent_text_token',
               'trigger':'audio_terminal_agent_trigger_token',
               'request':'audio_terminal_request_display','tick':'g2_flashdb_candidate_tick',
               'flags':'audio_log_flags','extended':'audio_log_extended',
               'compact':'compressed_log_output'}
        trace=[]
        for kind,address in native.items():
            addr=syms[names[kind]] if compiled else address
            def hook(cpu,at,size,user,kind=kind):
                r0=cpu.reg_read(A.UC_ARM_REG_R0);r1=cpu.reg_read(A.UC_ARM_REG_R1)
                if kind=='match':trace.append(('match',r0));cpu.reg_write(A.UC_ARM_REG_R0,match)
                elif kind=='append':
                    trace.append(('append',bytes(cpu.mem_read(r0,4))))
                    cpu.mem_write(r1,(0x31).to_bytes(2,'little'))
                    cpu.reg_write(A.UC_ARM_REG_R0,append)
                elif kind=='text':trace.append(('text',r0,r1));cpu.reg_write(A.UC_ARM_REG_R0,0xa123)
                elif kind=='trigger':trace.append(('trigger',r0,r1));cpu.reg_write(A.UC_ARM_REG_R0,0xb456)
                elif kind=='request':trace.append(('request',r0,r1));cpu.reg_write(A.UC_ARM_REG_R0,0)
                elif kind=='tick':trace.append(('tick',));cpu.reg_write(A.UC_ARM_REG_R0,now)
                elif kind=='flags':cpu.reg_write(A.UC_ARM_REG_R0,log_flags)
                elif kind in ('extended','compact'):
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    def cstr(ptr):return bytes(cpu.mem_read(ptr,320)).split(b'\0')[0]
                    if kind=='extended':
                        line=int.from_bytes(cpu.mem_read(sp,4),'little')
                        message=cstr(int.from_bytes(cpu.mem_read(sp+4,4),'little'))
                        count=(15 if b'recv terminal agent content:' in message else
                               4 if b'skip terminal agent text append:' in message else
                               3 if b'ignore terminal agent text content:' in message or b'drop content trigger event' in message else
                               2 if b'drop tool_start' in message or b'len: ' in message else 1)
                        args=tuple(int.from_bytes(cpu.mem_read(sp+8+i*4,4),'little') for i in range(count))
                        trace.append(('extended',r0,line,message,args))
                    else:
                        message=cstr(r1)
                        count=(15 if b'recv terminal agent content:' in message else
                               4 if b'skip terminal agent text append:' in message else
                               3 if b'ignore terminal agent text content:' in message or b'drop content trigger event' in message else
                               2 if b'drop tool_start' in message or b'len: ' in message else 1)
                        args=(cpu.reg_read(A.UC_ARM_REG_R3),)+tuple(
                            int.from_bytes(cpu.mem_read(sp+i*4,4),'little') for i in range(count-1))
                        trace.append(('compact',r0,message,args))
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
        u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        u.reg_write(A.UC_ARM_REG_R0,payload if present else 0);u.reg_write(A.UC_ARM_REG_R1,0)
        u.emu_start((syms['audio_terminal_command_5e9390'] if compiled else 0x5e9390)|1,
                    0x600000,count=3000)
        return u.reg_read(A.UC_ARM_REG_R0),trace,bytes(u.mem_read(tracking,8))
    cases=0
    for present in (False,True):
      for match in (0,1):
       for text_len in (0,3):
        for append in (0,1):
         for event in (0,1,2,3,4):
          for mode in (6,7):
           for session in (0,17):
            for active in (0,1):
             previous,now=100,2200
             for log_flags in (0,1,2,4,7):
              pair=[one(c,present,match,text_len,append,event,mode,session,active,previous,now,log_flags) for c in (False,True)]
              assert pair[0]==pair[1],(present,match,text_len,append,event,mode,session,active,log_flags,pair)
              cases+=1
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_command_5e9390'}
assert after-before=={'audio_terminal_data_append_agent_content'}
receipt={'round':997,'status':'PASS_TERMINAL_AGENT_CONTENT_LOGGING','component':'Apollo terminal agent content callback 0x5e9390',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cases':cases,
         'validation':'M55 strict compile and native/C state, return, token, display and enabled logging payload parity',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Append child 0x597a96 remains a lower selected provider',
                  'Absolute RAM placement and whole image/hardware remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases,len(before),len(after),receipt['linked_sha256'])

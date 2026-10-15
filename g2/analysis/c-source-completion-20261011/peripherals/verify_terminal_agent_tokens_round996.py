#!/usr/bin/env python3
"""Native/C parity for terminal agent token constructors."""
from pathlib import Path
import hashlib, json, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/terminal-agent-tokens-round996';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/terminal_agent_tokens.c'
base=root/'build/c-firmware/terminal-tx-pb-descriptor-round995/apollo-main-terminal-tx-pb-descriptor.o'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj=out/'terminal_agent_tokens.o';linked=out/'apollo-main-terminal-agent-tokens.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'shim.c';shim.write_text('int audio_uart_lv_obj_y_44e498(void*p){(void)p;return 0;}\n')
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-O2','-nostdlib','-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_terminal_agent_text_token',str(src),str(shim),'-o',str(elf)],check=True)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    cases=0
    def run(compiled,kind,length,present,y,flag,trigger=False):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for a,d in segs:u.mem_write(a,d)
        u.mem_map(0x20000000,0x200000)
        ptr=syms['audio_terminal_agent_session_ptr'] if compiled else 0x2006e0d4
        special=syms['audio_terminal_agent_special_flag'] if compiled else 0x2006e35c
        u.mem_write(ptr,(0x20010000 if present else 0).to_bytes(4,'little'))
        u.mem_write(special,bytes([flag]))
        if not trigger:
            child=syms['audio_uart_lv_obj_y_44e498'] if compiled else 0x44e498
            def hook(cpu,address,size,user):
                cpu.reg_write(A.UC_ARM_REG_R0,y&0xffffffff)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE,hook,begin=child&~1,end=child&~1)
        u.reg_write(A.UC_ARM_REG_SP,0x201ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        u.reg_write(A.UC_ARM_REG_R0,kind);u.reg_write(A.UC_ARM_REG_R1,length)
        entry=(syms['audio_terminal_agent_trigger_token'] if compiled else 0x5e51b0) if trigger else (syms['audio_terminal_agent_text_token'] if compiled else 0x5e5166)
        u.emu_start(entry|1,0x600000,count=200)
        return u.reg_read(A.UC_ARM_REG_R0)
    for kind in (0,1,15,16,255):
        for length in (0,1,63,64,65535):
            for present in (False,True):
                for y in (-1,0,12345,65536):
                    for flag in (0,1):
                        pair=[run(c,kind,length,present,y,flag) for c in (False,True)]
                        assert pair[0]==pair[1],(kind,length,present,y,flag,pair)
                        cases+=1
    for flags in (0,1,15,16,255,0xffffffff):
        for tick in (0,1,0x12345678,0xffffffff):
            pair=[run(c,flags,tick,False,0,0,True) for c in (False,True)]
            assert pair[0]==pair[1],(flags,tick,pair)
            cases+=1
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(p):return {line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(p)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before==after
receipt={'round':996,'status':'PASS_TERMINAL_AGENT_TOKENS','component':'Apollo agent content token helpers 0x5e5166 and 0x5e51b0',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cases':cases,
         'validation':'M55 strict compile and native/C packed token parity including callback child return',
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,
         'gates':['Absolute RAM placement of terminal state cells remains open','Agent content callback and append child remain unresolved']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases,len(before),len(after),receipt['linked_sha256'])

#!/usr/bin/env python3
"""Compare the query session-name lookup against the pinned Apollo payload."""
import hashlib, itertools, json, struct, subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]; G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_session_name_5ec7f0.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-session-name-5ec7f0'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STATE=0x2006e0d0; ACTIVE=0x20080000
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    blob=PAYLOAD.read_bytes()[32:]; assert hashlib.sha256(blob).hexdigest()==PIN
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/'oracle.o'; elf=OUT/'oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_terminal_ui_state_base=0x2006e0d0','--defsym=audio_td_active_session=0x59732b',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f)
        seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(compiled,count,match,nonzero,available):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
        u.mem_map(0x100000,0x100000)
        for addr,data in seg:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(STATE,bytes(0x2a0));u.mem_write(STATE+0x288,struct.pack('<I',0x1234))
        u.mem_write(ACTIVE,bytes(0x1000));u.mem_write(ACTIVE+8,struct.pack('<I',count))
        for i in range(count):
            p=ACTIVE+0x9c+0x90*i
            u.mem_write(p,struct.pack('<IH',0x1234 if i==match else 0x8000+i,5 if i==match and nonzero else 0)+b'name\0')
        calls=[]
        def hook(cpu,pc,size,_):
            if pc==0x59732a:
                calls.append(pc)
                cpu.reg_write(A.UC_ARM_REG_R0,ACTIVE if available else 0)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
        u.emu_start((sym['audio_terminal_query_session_name_5ec7f0'] if compiled else 0x5ec7f0)|1,0x600000,count=400)
        return u.reg_read(A.UC_ARM_REG_R0),calls
    cases=list(itertools.product(range(5),(-1,0,1,2,3,4),(False,True),(False,True)))
    for i,case in enumerate(cases):
        stock=run(False,*case); rebuilt=run(True,*case)
        if stock!=rebuilt:raise RuntimeError(f'case {i} {case}: stock={stock} rebuilt={rebuilt}')
    receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SESSION_NAME_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Active-session absence, entry search and name length/pointer','limits':['Active-session provider effect isolated; count bounded to four entries; final RAM placement and malformed count remain open.']}
    path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Stock/C oracle for Case in-case input event wrapper 0x5130a6."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_in_case_5130a6_20261017.c'
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT=ROOT/'g2/build/c-firmware/20261017/main-case-in-case/oracle-receipt.json'
PAYLOAD=STOCK.read_bytes()[32:]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'event.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
        '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin',
        '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_case_in_case_side_effect_5130a6',
        '-Wl,--defsym=audio_input_message_send_record=0x120001',str(SOURCE),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    with elf.open('rb') as f:
        e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
        syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    def run(native):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,PAYLOAD)
        u.mem_map(0x100000,0x40000)
        for addr,data in segs:u.mem_write(addr,data)
        u.mem_map(0x20000000,0x100000)
        calls=[];hookaddr=0x51301c if native else 0x120000
        def hook(uc,addr,size,_):
            if addr==hookaddr:
                calls.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),12)))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x130001)
        entry=0x5130a6 if native else syms['audio_uart_case_in_case_side_effect_5130a6']&~1
        u.emu_start(entry|1,0x130000,count=1000)
        return calls
    stock=run(True);rebuilt=run(False)
    assert stock==rebuilt==[bytes((3,0,0,0,0,0,0,0,0,0,0,0))]
    rec={'status':'PASS_BOUNDED_MAIN_CASE_IN_CASE_C','cases':1,
         'source_sha256':sha(SOURCE),'stock_package_sha256':sha(STOCK),
         'scope':'exact 12-byte input event record and single lower call',
         'remaining_gate':'Input event queue and hardware behavior remain outside this wrapper proof.'}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n')
    print(rec['status'],sha(OUT))

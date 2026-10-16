#!/usr/bin/env python3
"""Controlled stock/C comparison for text-stream common-prefix count."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP, UC_CPU_ARM_CORTEX_M4
ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/text_stream_prefix_match_552ecc.c'
OUT = G2 / 'build/c-firmware/20261016/main-text-stream-prefix-match'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(payload, segments, symbols, compiled, left, right):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x400000, 0x400000); cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x100000, 0x100000)
    cpu.mem_map(0x20000000, 0x100000)
    for addr, blob in segments: cpu.mem_write(addr, blob)
    if left is not None: cpu.mem_write(0x20004000, left+b'\0')
    if right is not None: cpu.mem_write(0x20005000, right+b'\0')
    cpu.reg_write(UC_ARM_REG_R0, 0 if left is None else 0x20004000)
    cpu.reg_write(UC_ARM_REG_R1, 0 if right is None else 0x20005000)
    cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR, 0x600001)
    strlen_addr = (symbols['strlen'] & ~1) if compiled else 0x44a43c
    calls=[]
    def hook(machine, pc, width, unused):
        if pc != strlen_addr: return
        addr=machine.reg_read(UC_ARM_REG_R0); length=0
        while machine.mem_read(addr+length, 1)[0]: length += 1
        calls.append(length)
        machine.reg_write(UC_ARM_REG_R0, length)
        machine.reg_write(UC_ARM_REG_PC, machine.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE, hook)
    entry = symbols['audio_text_stream_prefix_match_552ecc'] if compiled else 0x552ecc
    cpu.emu_start(entry | 1, 0x600000, count=1000)
    return cpu.reg_read(UC_ARM_REG_R0), calls

def main():
    payload=PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest()!=PINNED: raise RuntimeError('Apollo payload changed')
    OUT.mkdir(parents=True,exist_ok=True)
    stub=OUT/'prefix-oracle-stub.c'; stub.write_text('#include <stddef.h>\nsize_t strlen(const char *s){size_t n=0;while(s[n])++n;return n;}\n')
    elf_path=OUT/'prefix-oracle.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_text_stream_prefix_match_552ecc',str(SOURCE),str(stub),'-o',str(elf_path)],check=True)
    with elf_path.open('rb') as f:
        elf=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    values=[None,b'',b'a',b'ab',b'abc',b'abd',b'abcdef',b'xyz',b'\x80a',b'\x80b',b'aaaaaa']
    cases=0
    for left in values:
        for right in values:
            args=(left,right)
            stock=run(payload,segments,symbols,False,*args)
            actual=run(payload,segments,symbols,True,*args)
            if stock!=actual: raise RuntimeError(f'prefix mismatch {args}: {stock} != {actual}')
            cases+=1
    receipt={'status':'PASS_EXPERIMENTAL_TEXT_STREAM_PREFIX_MATCH_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PINNED,'oracle_elf':str(elf_path.relative_to(ROOT)),'oracle_elf_sha256':sha(elf_path),'cases':cases,'scope':'Null guards, both string lengths and bytewise common prefix over controlled inputs','limits':['Full caller state and whole-image integration remain open.']}
    path=OUT/'oracle-receipt.json'; path.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(receipt['status'],cases,sha(path))
if __name__=='__main__': main()

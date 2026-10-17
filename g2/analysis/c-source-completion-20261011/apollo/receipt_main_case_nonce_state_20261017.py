#!/usr/bin/env python3
"""Bind exact initialized Case nonce bytes from authenticated low-RAM startup."""
import hashlib,json,subprocess,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'g2/build/c-firmware/20261017'
HERE=BASE/'main-case-nonce-state'
PRIOR=BASE/'main-case-send-response/candidate.o'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_case_nonce_state_200036d8_20261017.c'
DECODE=ROOT/'g2/analysis/c-source-completion-20261011/apollo/decode_main_low_ram_20261016.py'
OBJECT,CURRENT,OUT=HERE/'nonce-state.o',HERE/'candidate.o',HERE/'receipt.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
def symbols(path,option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm',option,str(path)],text=True).splitlines() if line.strip()})
def main():
    sys.path.insert(0,str(DECODE.parent))
    from decode_main_low_ram_20261016 import decode
    initial=decode()[0x36d8:0x36dc]
    assert initial==bytes.fromhex('ff ff 02 02')
    HERE.mkdir(parents=True,exist_ok=True)
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                    '-std=c11','-O2','-Wall','-Wextra','-Werror','-ffreestanding',
                    '-fno-builtin','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
    with OBJECT.open('rb') as f:
        elf=ELFFile(f);section=elf.get_section_by_name('.g2_ram_200036d8')
        assert section is not None and section['sh_size']==4 and section.data()==initial
    subprocess.run(['arm-none-eabi-ld','-r',str(PRIOR),str(OBJECT),'-o',str(CURRENT)],check=True)
    prior,current=symbols(PRIOR,'-u'),symbols(CURRENT,'-u')
    removed,added=sorted(set(prior)-set(current)),sorted(set(current)-set(prior))
    assert removed==['audio_uart_case_nonce_state_200036d8']
    assert added==[] and len(prior)==96 and len(current)==95
    assert set(removed).issubset(symbols(CURRENT,'--defined-only'))
    record={'status':'PASS_MAIN_CASE_NONCE_STATE_C_INTEGRATION',
            'prior_candidate':ref(PRIOR),'candidate_object':ref(CURRENT),
            'source':ref(SOURCE),'low_ram_decoder':ref(DECODE),
            'stock_initial_bytes':initial.hex(),'stock_ram_address':'0x200036d8',
            'unresolved_before':96,'unresolved_after':95,
            'removed_imports':removed,'new_imports':added,
            'remaining_gate':'Case nonce state now has stock-matched initialized C bytes. Final linker address, startup copy order, mutations beyond the bounded updater and hardware behavior remain open.',
            'source_complete':False,'flashable':False,'hardware_proof':False}
    OUT.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(record['status'],len(current),sha(OUT))
if __name__=='__main__':main()

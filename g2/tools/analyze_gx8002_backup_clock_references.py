# SPDX-License-Identifier: MIT
"""Classify bounded clock-reference candidates using authenticated bytes."""
import json
import subprocess
from analyze_gx8002_double_wrapper_references import analyze
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode


def verify():
    census=analyze(0x3bbd4,0x3be14)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def disassemble(a,b):return subprocess.check_output([tool,'-D',f'--start-address={a:#x}',f'--stop-address={b:#x}',str(wrapper)],text=True)
    assert census['external_branches']==[{'pc':0x3bad4,'target':0x3bbd4,'entry':True}]
    assert census['external_literal_pools']==[{'pc':0x3ba60,'pool':0x3bd5c},{'pc':0x3bbd2,'pool':0x3bbd4}]
    pools=[]
    for false_pc,pool,reader,value in ((0x3ba60,0x3ba60,0x3ba40,0x80000200),(0x3bbd2,0x3bbd0,0x3bbae,0x10012940)):
        assert int.from_bytes(stock[pool:pool+4],'little')==value
        asm=disassemble(reader,reader+4);code=decode(asm)
        assert code[reader][:2]==('lrw',f'r0, {value:#x}')
        assert f'// {pool:x} ' in asm
        pools.append({'candidate_pc':false_pc,'containing_literal_word':pool,'actual_reader':reader,'literal_value':value,'classification':'linear decoding of an authenticated literal word, not a clock-pool read'})
    words=[]
    assert [w['offset'] for w in census['stored_address_words']]==[0x47d55,0x47f69]
    current_dir=ROOT/'build/gx8002-fft-q15-uart-cluster-integration-experiment'
    current=(current_dir/'firmware_codec.unadmitted.bin').read_bytes()
    report=json.loads((current_dir/'build-report.json').read_text());assert sha(current)==report['firmware_sha256']
    for word,start in zip(census['stored_address_words'],(0x47d54,0x47f68)):
        instructions=decode(disassemble(start,start+8))
        assert instructions[start]==('addu','r19, r18, r1',4)
        assert instructions[start+4]==('movi','r16, 0',4)
        assert word['offset']==start+1 and word['value']==0x100033c4
        words.append({**word,'containing_instruction':start,'classification':'unaligned byte window spanning addu and movi encodings','still_present_at_offset_in_current_image':current[start+1:start+5]==stock[start+1:start+5]})
    return {'census':census,'literal_classifications':pools,'stored_word_classifications':words,'current_firmware_sha256':sha(current),'bounded_candidates_resolved':True,'limits':['Classification establishes literal/data and instruction encodings for the enumerated scan candidates. It is not proof against arbitrary computed jumps or data reinterpretation. Clock firmware integration remains pending.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-clock-references.json').write_text(json.dumps(r,indent=2)+'\n');print('Clock bounded reference candidates classified')

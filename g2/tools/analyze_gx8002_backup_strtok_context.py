# SPDX-License-Identifier: MIT
"""Bounded tokenizer caller/state evidence and unaligned instruction-word artifact."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode

def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    raw=analyze(0x49c14,0x49c84)
    assert [r['pc'] for r in raw['external_branches']]==[0x44c5e,0x44c6c,0x44c7a,0x44c88]
    assert not raw['external_literal_pools']
    assert raw['stored_address_words']==[{'offset':0x478f1,'value':0x200112e0,'entry':False}]
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code={}
    for start,end in [(0x44c50,0x44c8c),(0x478e0,0x478fa)]:
        code.update(decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True)))
    assert code[0x44c54][:2]==('mov','r0, r14')
    for pc in (0x44c68,0x44c76,0x44c84):assert code[pc][:2]==('movi','r0, 0')
    assert int.from_bytes(stock[0x44d30:0x44d34],'little')==0x2e302e30
    assert int.from_bytes(stock[0x44d34:0x44d38],'little')==0x00332e32
    assert code[0x478f0]==('bsr','0x47b14',4)
    assert code[0x478f4][:2]==('ld.w','r1, (r5, 0x0)')
    assert stock[0x478f1:0x478f5]==(0x200112e0).to_bytes(4,'little')
    assert int.from_bytes(stock[0x49c80:0x49c84],'little')==0x2002d3e0
    result={'stock_sha256':IMAGE_SHA,'raw':raw,'caller_sequence':{'first_input':'stack buffer containing 0.0.2.3','entry_calls':[0x44c5e,0x44c6c,0x44c7a,0x44c88],'continuation_zero_setters':[0x44c68,0x44c76,0x44c84],'saved_cursor':0x2002d3e0},'artifact':{'offset':0x478f1,'containing_call':0x478f0,'next_instruction':0x478f4},'source_admitted':False,'limits':['Direct caller path initializes tokenizer with a nonnull string; arbitrary initial-state sequence tests are separate. Global reset initialization and computed-call closure are not proved. Unaligned address pattern crosses an actual call and load.']}
    (ROOT/'docs/research/gx8002-backup-strtok-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze_context()['artifact'])

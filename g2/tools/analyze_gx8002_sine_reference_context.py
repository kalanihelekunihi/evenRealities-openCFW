# SPDX-License-Identifier: MIT
"""Classify bounded sine references using consumed literals and generated FFT data."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode


def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    raw=analyze(0x49890,0x499ac,require_entry_only=False)
    assert len(raw['external_branches'])==5 and all(r['entry'] for r in raw['external_branches'])
    assert not raw['external_literal_pools']
    assert raw['stored_address_words']==[{'offset':0x184ee,'value':0x10011020,'entry':False},{'offset':0x4cdab,'value':0x20011004,'entry':False}]
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    text=subprocess.check_output([pre,'-D','--start-address=0x1849a','--stop-address=0x184a0',str(wrapper)],text=True)
    assert decode(text)[0x1849a][:2]==('lrw','r0, 0x1020b250') and '// 184ec ' in text
    assert int.from_bytes(stock[0x184ec:0x184f0],'little')==0x1020b250
    next_text=subprocess.check_output([pre,'-D','--start-address=0x184f0','--stop-address=0x184f4',str(wrapper)],text=True)
    instructions=decode(next_text)
    assert instructions[0x184f0]==('lrw','r0, 0x2002e79c',2)
    assert instructions[0x184f2]==('rts','',2)
    entries=[]
    for i in range(256):
        reverse=int(f'{i:08b}'[::-1],2)
        if i<reverse:entries.extend((i*8,reverse*8))
    table=b''.join(v.to_bytes(2,'little') for v in entries)
    assert len(table)==480 and table==stock[0x4cd34:0x4cf14]
    result={'stock_sha256':IMAGE_SHA,'raw':raw,'classifications':[{'finding':0x184ee,'literal_start':0x184ec,'literal_value':0x1020b250,'consumer':0x1849a,'next_instruction':instructions[0x184f0],'meaning':'Upper two bytes of consumed literal followed by first two-byte instruction of the next routine; not a stored pointer at this offset.'},{'finding':0x4cdab,'table_start':0x4cd34,'table_bytes':480,'table_sha256':sha(table),'meaning':'Unaligned cross-element bytes in fully regenerated bit-reversal swap table.'}],'unresolved_bounded_findings':[],'source_admitted':False,'limits':['Classifies all findings from this bounded scan only. Computed references and alternate mappings remain unqualified. Does not copy stock data into firmware.']}
    (ROOT/'docs/research/gx8002-sine-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__': print(analyze_context()['classifications'])

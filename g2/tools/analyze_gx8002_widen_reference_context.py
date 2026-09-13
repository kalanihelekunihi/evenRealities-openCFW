# SPDX-License-Identifier: MIT
"""Explain the widening-entry apparent pool reference using authenticated bytes."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode

def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    raw=analyze(0x4a434,0x4a460)
    assert raw['external_literal_pools']==[{'pc':0x4a432,'pool':0x4a434}]
    assert all(r['entry'] for r in raw['external_branches']) and not raw['stored_address_words']
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock')
    assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    assert int.from_bytes(stock[0x4a430:0x4a434],'little')==0x100155d4
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    text=subprocess.check_output([pre,'-D','--start-address=0x4a216','--stop-address=0x4a220',str(wrapper)],text=True)
    code=decode(text)
    assert code[0x4a216][:2]==('lrw','r2, 0x100155d4')
    assert '4a430' in text and code[0x4a21c][:2]==('ldr.b','r3, (r2, r3 << 0)')
    result={'stock_sha256':IMAGE_SHA,'raw':raw,'classification':{'apparent_instruction':0x4a432,'containing_literal':0x4a430,'literal_value':0x100155d4,'actual_consumer':0x4a216,'indexed_byte_load':0x4a21c},'source_admitted':False,'limits':['Apparent entry pool reference decodes the upper half of an actual pointer literal. This explains the raw scan finding, not computed-path closure or full preceding division-function recovery.']}
    (ROOT/'docs/research/gx8002-widen-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze_context()['classification'])

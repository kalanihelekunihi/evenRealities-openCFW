# SPDX-License-Identifier: MIT
"""Explain log reference census artifacts with literal and mathematical-table evidence."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode

def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    raw=analyze(0x490a8,0x49300,require_entry_only=False)
    assert raw['external_branches']==[{'pc':0x489ee,'target':0x490a8,'entry':True}]
    assert raw['external_literal_pools']==[{'pc':0x48eb2,'pool':0x49238}]
    assert raw['stored_address_words']==[{'offset':0x4cda7,'value':0x20010807,'entry':False}]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    text=subprocess.check_output([pre,'-D','--start-address=0x48bfc','--stop-address=0x48c04',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    assert decode(text)[0x48bfc][:2]==('lrw','r3, 0x5db3d6') and '// 48eb0 ' in text
    assert int.from_bytes(stock[0x48eb0:0x48eb4],'little')==0x005db3d6
    entries=[]
    for index in range(256):
        reverse=int(f'{index:08b}'[::-1],2)
        if index<reverse:entries.extend((index*8,reverse*8))
    table=b''.join(x.to_bytes(2,'little') for x in entries)
    assert len(table)==480 and table==stock[0x4cd34:0x4cf14]
    result={'stock_sha256':IMAGE_SHA,'raw':raw,'classifications':[{'finding':0x48eb2,'literal_offset':0x48eb0,'literal_value':0x005db3d6,'consumer':0x48bfc,'meaning':'Upper halfword of consumed power constant, not a load instruction.'},{'finding':0x4cda7,'table_offset':0x4cd34,'table_sha256':sha(table),'meaning':'Cross-element byte sequence in fully regenerated bit-reversal swap table.'}],'source_admitted':False,'limits':['All bounded scan findings explained. Computed targets and alternate mappings remain outside scope. No stock table bytes inserted into output.']}
    (ROOT/'docs/research/gx8002-logf-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze_context()['classifications'])

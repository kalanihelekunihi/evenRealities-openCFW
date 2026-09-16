# SPDX-License-Identifier: MIT
"""Classify exponential's apparent interior reference from a consumed literal."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode

def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    raw=analyze(0x49300,0x4950c,require_entry_only=False)
    assert raw['external_branches']==[{'pc':0x489f6,'target':0x49300,'entry':True},{'pc':0x49092,'target':0x493d6,'entry':False}]
    assert not raw['external_literal_pools'] and not raw['stored_address_words']
    text=subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x48fc4','--stop-address=0x48fcc',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    assert decode(text)[0x48fc4][:2]==('lrw','r2, 0xda24260') and '// 49090 ' in text
    assert int.from_bytes(stock[0x49090:0x49094],'little')==0x0da24260
    result={'stock_sha256':IMAGE_SHA,'raw':raw,'classification':{'apparent_branch':0x49092,'numeric_literal':0x49090,'literal_value':0x0da24260,'consumer':0x48fc4},'source_admitted':False,'limits':['Bounded scan findings explained; computed references, other mappings and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-expf-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze_context()['classification'])

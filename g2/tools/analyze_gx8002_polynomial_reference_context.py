# SPDX-License-Identifier: MIT
"""Explain the apparent pool reference inside fmod's signed-zero address."""
import json, subprocess
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha
from analyze_gx8002_double_wrapper_references import analyze
from verify_gx8002_memcpy_source import decode


def analyze_context():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    raw=analyze(0x49828,0x49890,require_entry_only=False)
    assert raw['external_literal_pools']==[{'pc':0x49826,'pool':0x49828}]
    assert not raw['external_branches'] and not raw['stored_address_words']
    text=subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x49710','--stop-address=0x49712',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    assert decode(text)[0x49710][:2]==('lrw','r2, 0x100155b0') and '// 49824 ' in text
    assert int.from_bytes(stock[0x49824:0x49828],'little')==0x100155b0
    result={'stock_sha256':IMAGE_SHA,'raw':raw,'classification':{'apparent_instruction':0x49826,'literal_start':0x49824,'literal_value':0x100155b0,'consumer':0x49710},'source_admitted':False,'limits':['Bounded finding is the upper half of a consumed address literal, not a polynomial reference. No callers found by this scan; computed entry paths and other mappings remain unqualified.']}
    (ROOT/'docs/research/gx8002-polynomial-reference-context.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(analyze_context())

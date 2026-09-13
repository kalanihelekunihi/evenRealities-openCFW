# SPDX-License-Identifier: MIT
"""Admit named playback dispatch table with complete evidence."""
import json,shutil
from pathlib import Path
from build_gx8002_audio_output_dispatch import build,ROOT,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification={"candidate":build()};rows=[]
    for item in qualification['candidate']['functions']:
        if not item['fits']:raise ValueError('Dispatch envelope')
        row={key:item[key] for key in ('symbol','section_name','compiled_bytes','compiled_sha256')}
        row['ownership_kind']=item.get('ownership_kind','compiled_c')
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_dram_data' if item['section_name'].startswith('.data.') else 'image_a_xip_rodata'}]
        rows.append(row)
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-output-dispatch/bits.elf',output/'bits.elf')
    evidence=('build_gx8002_audio_output_dispatch.py','verify_gx8002_audio_output_dispatch_source.py')
    return {'functions':rows,'qualification':qualification,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},'source_admitted':True,'hardware_qualified':False,'limits':['Named dispatch references match stock and SDK relocations; all20 targets require source-admission records. Full public-caller ABI/lifecycle composition, boot copy and whole-firmware closure remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-dispatch-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Playback dispatch source admission passed')

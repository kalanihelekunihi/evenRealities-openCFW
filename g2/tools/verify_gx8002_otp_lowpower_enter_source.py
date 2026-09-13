# SPDX-License-Identifier: MIT
"""Experimental admission of recovered otp-lowpower-enter."""
import json,re,shutil
from verify_gx8002_otp_lowpower_configuration import verify as compare
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();candidate=json.loads((ROOT/'docs/research/gx8002-otp-lowpower-enter-candidate.json').read_text())
    path=ROOT/'build/gx8002-board/otp-lowpower-enter.elf';elf=Elf32(path.read_bytes(),str(path))
    expected={'.text':(0x168e0,116)}
    rows=[];stock=IMAGE.read_bytes()
    for section in elf.sections:
        if not section['flags']&2 or not section['size']:continue
        name=section['name']
        if name not in expected:raise ValueError('Unexpected allocation')
        offset,size=expected[name];data=elf.contents(section)
        if section['address']!=offset+0x1000dfec or len(data)>size or elf.relocations(section['index']):raise ValueError('Placement')
        if name!='.text' and data!=stock[offset:offset+size]:raise ValueError('Diagnostic mismatch')
        symbol='open_cfw_gx8002_otp_lowpower_enter'+('' if name=='.text' else '_'+name.split('.')[-1])
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':'compiled_c' if name=='.text' else 'generated_source_data','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_sram'}]})
    if len(rows)!=1 or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Missing/unresolved section')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-otp-lowpower-enter-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');size=occurrence.get('bytes')
                if start is not None and size is not None and any(start<o+n and o<start+size for o,n in expected.values()):raise ValueError(('Ownership overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'otp-lowpower-enter.elf')
    files=sorted({p.name for pattern in ('*gx8002_flash_otp_configuration*.py','*gx8002_otp_lowpower*.py') for p in (ROOT/'tools').glob(pattern)}|{'execute_gx8002_otp_interface.py','verify_gx8002_flash_probe_callback_owner.py','execute_gx8002_clock_source_select.py','verify_gx8002_power_initialize.py','verify_gx8002_memcpy_source.py'})
    return {'functions':rows,'evidence':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':evidence['limits']+['C compilation includes visible architectural or address-forming inline assembly; no firmware byte extraction.']+['Experimental hybrid admission only; complete source-only firmware unfinished.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-otp-lowpower-enter-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('otp-lowpower-enter experimental admission passed')

# SPDX-License-Identifier: MIT
"""Experimental admission of the recovered Persistent application callback."""
import json,re,shutil
from verify_gx8002_app_command_callback_persistent import verify as compare
from verify_gx8002_app_command_callback_persistent_mutations import verify as mutations
from verify_gx8002_callback_persistent_payload_lifetime import verify as lifetime
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();candidate=evidence['candidate'];mutation_evidence=mutations();lifetime_evidence=lifetime()
    path=ROOT/'build/gx8002-app-command-callback-persistent/candidate.elf';elf=Elf32(path.read_bytes(),str(path))
    expected={'.text': (76220, 716), '.rodata.delay_response': (76132, 1), '.rodata.mic': (85185, 23), '.rodata.gsensor': (85208, 26), '.rodata.version': (85234, 21), '.rodata.delimiter': (85255, 2), '.rodata.beamforming': (85257, 23), '.rodata.vad_open': (85280, 20), '.rodata.vad_close': (85300, 21), '.rodata.byte': (85321, 7), '.rodata.gain_ok': (85328, 25), '.rodata.gain_fail': (85353, 22), '.rodata.gain_range': (85375, 40), '.rodata.dmic_open': (85415, 23), '.rodata.dmic_init': (85438, 18), '.rodata.dmic_close': (85456, 24), '.rodata.dmic_stop': (85480, 19), '.rodata.delay': (85499, 30), '.rodata.i2s': (85529, 28), '.rodata.mode': (85557, 19)}
    rows=[];stock=IMAGE.read_bytes()
    for section in elf.sections:
        if not section['flags']&2 or not section['size']:continue
        name=section['name']
        if name not in expected:raise ValueError('Unexpected allocation')
        offset,size=expected[name];data=elf.contents(section)
        if section['address']!=offset+0x101f6a74 or len(data)>size or elf.relocations(section['index']):raise ValueError('Placement')
        if name=='.rodata.delay_response':
            if data!=b'\x01':raise ValueError('Persistent byte')
        elif name!='.text' and data!=stock[offset:offset+size]:raise ValueError('Diagnostic mismatch')
        symbol='open_cfw_gx8002_app_command_callback_persistent'+('' if name=='.text' else '_'+name.split('.')[-1])
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':'compiled_c' if name=='.text' else 'generated_source_data','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_xip_text'}]})
    if len(rows)!=20 or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Missing/unresolved section')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-app-command-callback-persistent-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        r=json.loads(p.read_text())
        for row in r.get('functions',[r]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');size=occurrence.get('bytes')
                if start is not None and size is not None and any(start<o+n and o<start+size for o,n in expected.values()):raise ValueError(('Ownership overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'app-command-callback-persistent.elf')
    files=('verify_gx8002_app_command_callback_persistent_source.py','verify_gx8002_app_command_callback_persistent.py','execute_gx8002_app_command_callback.py','build_gx8002_app_command_callback_persistent.py','verify_gx8002_app_command_callback_persistent_mutations.py','verify_gx8002_callback_persistent_payload_lifetime.py','oracle_gx8002_app_command_callback.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':rows,'evidence':evidence,'mutation_evidence':mutation_evidence,'lifetime_evidence':lifetime_evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':evidence['limits']+['Experimental hybrid admission only; complete source-only firmware unfinished.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-app-command-callback-persistent-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Persistent application callback experimental admission passed')

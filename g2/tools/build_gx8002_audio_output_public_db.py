# SPDX-License-Identifier: MIT
"""Build public volume and its source-defined diagnostics."""
import json,subprocess
from analyze_gx8002_audio_output_public import analyze,ROOT,IMAGE,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    identities=analyze();identity=next(x for x in identities['functions'] if x['section']=='.text.gx_audio_out_set_db')
    if [m['package_offset'] for m in identity['matches']]!=[0xea4c] or identity['bytes']!=56:raise ValueError('Public volume identity')
    stock=IMAGE.read_bytes();out=ROOT/'build/gx8002-audio-output-public-db';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_output_public_db.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-I'+str(ROOT/'build/upstream-nationalchip-lvp-kws/include/driver'),'-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'bits.o')],check=True)
    entries=(('audio_out_set_db','.text.',0xea4c,56,'compiled_c'),('aout_db_label','.rodata.',0x14098,20,'generated_source_data'))
    script='SECTIONS {\n'+''.join(f'{section}{name} {offset+0x101f6a74:#x} : {{ *({section}open_cfw_gx8002_{name}) }}\n' for name,section,offset,size,kind in entries)+'}\nprintf_ = 0x10206c24;\nopen_cfw_gx8002_aout_error_format = 0x1020abfa;\n'
    (out/'bits.ld').write_text(script);subprocess.run([pre+'ld','-T',str(out/'bits.ld'),str(out/'bits.o'),'-o',str(out/'bits.elf')],check=True);elf=Elf32((out/'bits.elf').read_bytes(),'bits.elf');rows=[]
    allowed={section+name for name,section,o,z,k in entries}
    if any(s['size'] and s['flags']&2 and s['name'] not in allowed for s in elf.sections):raise ValueError('Public volume unaccounted section')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Public volume unresolved link')
    for name,section,offset,size,kind in entries:
        section+=name;payload=elf.contents(next(s for s in elf.sections if s['name']==section))
        if kind=='generated_source_data' and payload!=stock[offset:offset+size]:raise ValueError('Public volume diagnostic mismatch')
        rows.append({'symbol':'open_cfw_gx8002_'+name,'section_name':section,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'ownership_kind':kind,'fits':len(payload)<=size})
    (out/'bits.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'bits.elf')],text=True))
    return {'functions':rows,'source_sha256':sha(source.read_bytes()),'identity':identity,'sdk_commit':identities['sdk_commit'],'oracle':identities['oracle'],'source_admitted':False,'hardware_qualified':False,'limits':['Global dispatch slot uses original RAM address; BSS initialization and callback composition not qualified. Reuses admitted source error format; label generated from source.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-output-public-db-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(f['compiled_bytes'],f['fits']) for f in r['functions']])

# SPDX-License-Identifier: MIT
"""Native linked KWS flash-loader candidate, without binary code imports."""
import json,subprocess
from analyze_gx8002_kws_flash_load import analyze,ROOT,IMAGE,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={
 'LvpModelGetCmdSize':0x10208bf4,'LvpModelGetWeightSize':0x10208bfc,
 'LvpModelGetOpsSize':0x10208c04,'LvpModelGetDataSize':0x10208c08,
 'LvpModelGetTmpSize':0x10208c10,'LvpSetSnpuTask':0x10208c14,
 'gx_get_time_ms':0x10025930,'gx_spi_flash_probe':0x1002475c,
 'gx_spi_flash_readdata':0x100247b8,'printf_':0x10206c24}

def build():
    attribution=analyze();stock=IMAGE.read_bytes()
    if set(BINDINGS.values())!={x['runtime_target'] for x in attribution['calls']}:raise ValueError('Call bindings differ')
    out=ROOT/'build/gx8002-kws-flash-load';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_kws_flash_load.c'
    labels=('init_error','elapsed','read_error');entries=[('open_cfw_gx8002_kws_flash_load','.text',0x1023c,224)]
    strings=[]
    for label,row in zip(labels,attribution['diagnostics']):
        name='open_cfw_kws_flash_'+label;offset=row['runtime_address']-0x101f6a74
        strings.append('const char '+name+'[]='+json.dumps(row['text'])+';')
        entries.append((name,'.rodata',offset,len(row['text'].encode())+1))
    diagnostics=out/'diagnostics.c';diagnostics.write_text('/* SPDX-License-Identifier: MIT */\n'+'\n'.join(strings)+'\n')
    for path,name in ((source,'loader'),(diagnostics,'diagnostics')):
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(path),'-o',str(out/(name+'.o'))],check=True)
    script='SECTIONS {\n'+''.join(f'{section}.{name} {offset+0x101f6a74:#x} : {{ *({section}.{name}) }}\n' for name,section,offset,size in entries)+'}\n'+''.join(f'{name} = {address:#x};\n' for name,address in BINDINGS.items())
    (out/'loader.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'loader.ld'),str(out/'loader.o'),str(out/'diagnostics.o'),'-o',str(out/'loader.elf')],check=True)
    elf=Elf32((out/'loader.elf').read_bytes(),'loader.elf');allowed={s+'.'+n for n,s,o,z in entries};rows=[]
    if any(s['size'] and s['flags']&2 and s['name'] not in allowed for s in elf.sections):raise ValueError('Unaccounted sections')
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    for name,kind,offset,size in entries:
        section=next(s for s in elf.sections if s['name']==kind+'.'+name);payload=elf.contents(section)
        if kind=='.rodata' and payload!=stock[offset:offset+size]:raise ValueError('Diagnostic mismatch')
        rows.append({'symbol':name,'section_name':section['name'],'package_offset':offset,'compiled_bytes':len(payload),'stock_envelope_bytes':size,'compiled_sha256':sha(payload),'stock_sha256':sha(stock[offset:offset+size]),'fits':len(payload)<=size,'ownership_kind':'compiled_c' if kind=='.text' else 'generated_source_data'})
    (out/'loader.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'loader.elf')],text=True))
    return {'functions':rows,'bindings':BINDINGS,'attribution':attribution,'source_sha256':sha(source.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Linked candidate only. Candidate zeros previously uninitialized task fields before publication. Full helper behavior and model data remain unresolved.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-kws-flash-load-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print([(x['compiled_bytes'],x['stock_envelope_bytes']) for x in r['functions']])

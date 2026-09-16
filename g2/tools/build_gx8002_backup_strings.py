# SPDX-License-Identifier: MIT
"""Link reviewed source string leaves at the backup firmware ABI addresses."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

ROWS = [('strncmp', 'runtime_gx8002_strncmp.c', 'open_cfw_gx8002_strncmp', 0x10009998, 36),
        ('strlen', 'runtime_gx8002_stage2_libc.c', 'open_cfw_gx8002_stage2_strlen', 0x100099bc, 24)]

def build():
    out = ROOT/'build/gx8002-backup-strings'
    out.mkdir(parents=True, exist_ok=True)
    pre = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    inputs, scripts, sources = [], [], {}
    for name, filename, symbol, address, size in ROWS:
        source = ROOT/'components/shared/gx8002'/filename
        obj = out/(name+'.o')
        subprocess.run([pre+'gcc', '-Os', *FLAGS[1:], '-c', str(source), '-o', str(obj)], check=True)
        # Keep only the reviewed leaf; unrelated stage-2 functions are not linked.
        subprocess.run([pre+'objcopy', '--only-section=.text.'+symbol,
                        '--redefine-sym', symbol+'='+name, str(obj)], check=True)
        inputs.append(str(obj))
        scripts.append(f'.backup_{name} {address:#x} : {{ *(.text.{symbol}) }}')
        sources[filename] = sha(source.read_bytes())
    script = out/'strings.ld'
    script.write_text('SECTIONS {\n'+'\n'.join(scripts)+'\n}\n')
    path = out/'strings.elf'
    subprocess.run([pre+'ld', '-T', str(script), *inputs, '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), str(path))
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    allocated = [s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(allocated)==len(ROWS)
    results=[]
    for name, filename, symbol, address, size in ROWS:
        section=next(s for s in allocated if s['name']=='.backup_'+name)
        assert section['address']==address and section['size']<=size and not elf.relocations(section['index'])
        sym=next(s for s in elf.symbols() if s['name']==name)
        assert sym['value']==address and sym['section']==section['index']
        offset=address-0x10000000+0x38940
        results.append({'symbol':name,'address':address,'package_offset':offset,'compiled_bytes':section['size'],
                        'compiled_sha256':sha(elf.contents(section)), 'stock_envelope_bytes':size,
                        'stock_sha256':sha(stock[offset:offset+size])})
    (out/'strings.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'sources':sources,'functions':results,'source_admitted':False,'hardware_qualified':False,
            'limits':['Reviewed C leaves, not upstream libc attribution. See separate backup decoded verifiers; valid readable buffers, no timing or pointer-wrap qualification.']}
    (ROOT/'docs/research/gx8002-backup-strings-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(build(),indent=2))

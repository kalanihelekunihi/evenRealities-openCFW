# SPDX-License-Identifier: MIT
"""Compile all reconstructed IMCRA stages into one native-macOS development candidate."""
import json
import subprocess
import re
from analyze_gx8002_upstream_objects import ROOT, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    out = ROOT / 'build/gx8002-imcra-process'
    out.mkdir(exist_ok=True)
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_imcra_process.c'
    header = ROOT / 'build/gx8002-source-rfft-generated-reverse-cluster/fft_types.h'
    cluster = ROOT / 'build/gx8002-backup-startup-cluster/cluster.elf'
    if cluster.exists():
        elf = Elf32(cluster.read_bytes(), 'startup')
        symbols = {s['name']: s for s in elf.symbols()}
    else:
        # A failed relink may leave the authoritative disassembly but no ELF.
        # Recover only named symbol addresses to unblock regeneration; the next
        # successful startup link replaces this fallback evidence.
        text = (cluster.parent/'cluster.disassembly.txt').read_text()
        symbols = {name:{'value':int(addr,16),'section':1} for addr,name in
                   re.findall(r'^([0-9a-f]+) <([^>]+)>:',text,re.M)}
        symbols.update({
            'source_rfft_forward':{'value':0x20017020,'section':1},
            'source_rfft_inverse':{'value':0x2001700c,'section':1},
            'open_cfw_gx8002_backup_rfft':{'value':0x1000ef64,'section':1},
        })
    names = ['open_cfw_gx8002_memmove', 'open_cfw_gx8002_memset',
             'open_cfw_gx8002_imcra_peak_shift',
             'open_cfw_gx8002_imcra_sample_shift',
             'source_rfft_forward', 'source_rfft_inverse', 'open_cfw_gx8002_memcpy', 'open_cfw_gx8002_backup_rfft']
    bindings = {}
    for name in names:
        symbol = symbols[name]
        assert symbol['section'] not in (0, 0xfff1), name
        bindings[name] = symbol['value']
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    stages = ['process','prepare','power_spectrum','first_frame','prior_update',
              'smooth','minimum_mask','masked_smooth','probability','noise_update',
              'history_rotate','synthesize']
    sources = [ROOT / f'components/shared/gx8002/runtime_gx8002_imcra_{stage}.c' for stage in stages]
    objects = []
    for stage, component in zip(stages, sources):
        obj = out / f'{stage}.o'
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(header.parent),
                        '-c',str(component),'-o',str(obj)],check=True)
        objects.append(str(obj))
    script = 'SECTIONS { .prepare 0x10015d34 : { *(.text*) } }\n'
    script += ''.join(f'{name} = 0x{address:x};\n' for name, address in bindings.items())
    (out / 'prepare.ld').write_text(script)
    target = out / 'prepare.elf'
    subprocess.run([pre + 'ld', '-T', str(out / 'prepare.ld'),
                    *objects, '-o', str(target)], check=True)
    built = Elf32(target.read_bytes(), 'prepare')
    assert not any(s['name'] and s['section'] == 0 for s in built.symbols())
    assert not any(built.relocations(s['index']) for s in built.sections)
    sections = [s for s in built.sections if s['flags'] & 2 and s['size']]
    assert len(sections) == 1
    (out / 'prepare.disassembly.txt').write_text(subprocess.check_output(
        [pre + 'objdump', '-d', str(target)], text=True))
    report = {'source_sha256': sha(source.read_bytes()),
              'stage_sources': {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sources},
              'header_sha256': sha(header.read_bytes()),
              'startup_sha256': sha(cluster.read_bytes()) if cluster.exists() else None,
              'bytes': sections[0]['size'], 'helper_bindings': bindings,
              'source_admitted': False, 'startup_integrated': False,
              'limits': ['Composed processing candidate; whole-function equivalence not established.',
                         'Helpers resolved by address, not included in this standalone ELF.',
                         'Decoded equivalence and helper mutation verification pending.',
                         'No placement, complete firmware or hardware qualification.']}
    (ROOT / 'docs/research/gx8002-imcra-process.json').write_text(
        json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

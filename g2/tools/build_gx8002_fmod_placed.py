# SPDX-License-Identifier: MIT
"""Place complete source fmod; arithmetic target qualification remains separate."""
import json, subprocess
from build_gx8002_backup_cfft import ROOT, sha, Elf32
from build_gx8002_fmod_probe import build as probe


def build():
    evidence = probe()
    out = ROOT / 'build/gx8002-fmod-placed'
    out.mkdir(exist_ok=True)
    delta = 0x10003000 - 0x3b940
    ld = out / 'fmod.ld'
    ld.write_text(('__muldf3 = 0x%x; __divdf3 = 0x%x;\n'
                   'SECTIONS { .fmod 0x%x : { *(.text.__ieee754_fmod) } }\n'
                   'ASSERT(SIZEOF(.fmod)<=580,"fmod overflow")\n') %
                  (0x4a790 + delta, 0x4a990 + delta, 0x495e4 + delta))
    path = out / 'fmod.elf'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld', '-T', str(ld), str(ROOT/'build/gx8002-fmod-probe/signed-zero-compact.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'fmod')
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    allocated = [s for s in elf.sections if s['flags'] & 2 and s['size']]
    assert len(allocated) == 1
    sec = allocated[0]
    assert sec['name'] == '.fmod' and sec['size'] == 576 and sec['address'] == 0x495e4 + delta
    assert next(s['value'] for s in elf.symbols() if s['name'] == '__ieee754_fmod') == sec['address']
    (out/'fmod.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result = {'probe': evidence, 'elf_sha256': sha(path.read_bytes()),
              'sections': [{'name': '.fmod', 'package_offset': 0x495e4, 'bytes': sec['size'], 'sha256': sha(elf.contents(sec))}],
              'arithmetic_targets': {'__muldf3': 0x4a790, '__divdf3': 0x4a990},
              'source_admitted': False,
              'limits': ['Complete function fits original 580-byte region. Absolute arithmetic targets require authenticated source implementations at integration. Numerical, exceptional-value, ABI, reference and hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-fmod-placed.json').write_text(json.dumps(result, indent=2)+'\n')
    return result

if __name__ == '__main__':
    r = build()
    print(r['elf_sha256'], r['sections'])

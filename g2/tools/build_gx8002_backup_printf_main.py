# SPDX-License-Identifier: MIT
"""Place source main formatter with stock-supported features and explicit callees."""
import json
import subprocess
from analyze_gx8002_backup_printf_configuration import analyze, ROOT, Elf32, sha


def build():
    evidence = analyze()
    out = ROOT / 'build/gx8002-backup-printf'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    original = out / 'configuration-probes/0.o'
    assert sha(original.read_bytes()) == evidence['variants'][0]['object_sha256']
    obj = out / 'main.o'
    symbols = ('_vsnprintf', '_out_rev', '_ntoa_long', '_ntoa_long_long')
    subprocess.run([pre + 'objcopy', *['--globalize-symbol=' + s for s in symbols],
                    str(original), str(obj)], check=True)
    # All bytes come from compiled upstream sections. Data is relocated with
    # its owning formatter, without extracting the stock switch or pow10 table.
    script = '''SECTIONS {
.printf_null 0x10008a00 : { *(.text._out_null) }
.printf_main 0x10008e20 : {
 *(.text._vsnprintf) *(.rodata._vsnprintf*) *(.rodata.pow10*)
}
/DISCARD/ : { *(.text*) *(.rodata*) }
}
ASSERT(SIZEOF(.printf_null) <= 4, "null output overflow")
ASSERT(SIZEOF(.printf_main) <= 2820, "main formatter overflow")
'''
    offsets = {'_out_rev': 0x41344, '_ntoa_long': 0x415c8, '_ntoa_long_long': 0x41688,
               '__nedf2': 0x4aaa8, '__ltdf2': 0x4ab60, '__gtdf2': 0x4aae0,
               '__subdf3': 0x4a754, '__fixdfsi': 0x4ac38, '__floatsidf': 0x4abd0,
               '__muldf3': 0x4a790, '__fixunsdfsi': 0x49da4,
               '__floatunsidf': 0x4ad0c, '__ledf2': 0x4ab98}
    for name, offset in offsets.items():
        script += f'{name} = {offset - 0x38940 + 0x10000000:#x};\n'
    ld = out / 'main.ld'
    ld.write_text(script)
    path = out / 'main.elf'
    subprocess.run([pre + 'ld', '-T', str(ld), str(obj), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'main formatter')
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert next(s['value'] for s in elf.symbols() if s['name'] == '_vsnprintf') == 0x10008e20
    sections = [{'name': s['name'], 'address': s['address'], 'bytes': s['size'],
                 'sha256': sha(elf.contents(s))} for s in elf.sections if s['flags'] & 2 and s['size']]
    assert len(sections) == 2
    (out / 'main.disassembly.txt').write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    result = {'configuration': evidence, 'elf_sha256': sha(path.read_bytes()),
              'sections': sections, 'external_package_bindings': offsets, 'source_admitted': False,
              'limits': ['Main formatter and its switch/constants compiled from pinned SDK; fixed floating point and wide integer features retained. Exponential formats match stock fallback dispatch.',
                         'Helper entry bindings are external in this placement candidate. Main execution equivalence, source dependency composition and firmware qualification remain pending.']}
    (ROOT / 'docs/research/gx8002-backup-printf-main.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(build()['sections'])

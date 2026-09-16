# SPDX-License-Identifier: MIT
"""Reuse reconstructed SPL arithmetic at the BINH stage-one entries."""
import json
import subprocess
from verify_gx8002_uart_stage1_divmod import SOURCE, DIVMOD_FLAGS, battery_cases, execute, oracle
from build_gx8002_backup_cfft import ROOT, sha, Elf32, IMAGE, IMAGE_SHA
from verify_gx8002_memcpy_source import decode


def build():
    out = ROOT / 'build/gx8002-stage1-divmod'
    out.mkdir(exist_ok=True)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    obj = out / 'divmod.o'
    subprocess.run([pre+'gcc', *DIVMOD_FLAGS,
                    '-Dopen_cfw_gx8002_uart_stage1_udiv=open_cfw_gx8002_stage1_39774',
                    '-Dopen_cfw_gx8002_uart_stage1_umod=open_cfw_gx8002_stage1_397b8',
                    '-c', str(SOURCE), '-o', str(obj)], check=True)
    specs = [('.divide', 0x39774, 68, False), ('.remainder', 0x397b8, 60, True)]
    ld = out / 'divmod.ld'
    ld.write_text('SECTIONS {\n' + ''.join(
        f'{name} {off-0x38954+0x10000000:#x} : {{ *(.text.open_cfw_gx8002_stage1_{off:x}) }}\n'
        for name, off, _, _ in specs) +
        '/DISCARD/ : { *(.text.open_cfw_gx8002_uart_stage1_clear_bss) }\n}\n')
    path = out / 'divmod.elf'
    subprocess.run([pre+'ld', '-T', str(ld), str(obj), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), str(path))
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    wrapper = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    wrapped = Elf32(wrapper.read_bytes(), str(wrapper))
    assert wrapped.contents(next(s for s in wrapped.sections if s['name'] == '.data')) == stock
    dis = subprocess.check_output([pre+'objdump', '-d', str(path)], text=True)
    (out / 'divmod.disassembly.txt').write_text(dis)
    new = decode(dis)
    cases = 0
    sections = []
    for name, off, limit, is_mod in specs:
        section = next(s for s in elf.sections if s['name'] == name)
        assert section['size'] <= limit
        old = decode(subprocess.check_output([pre+'objdump', '-D',
            f'--start-address={off:#x}', f'--stop-address={off+limit:#x}', str(wrapper)], text=True))
        for num, den in battery_cases():
            expected = (oracle(num, den, is_mod), True, [])
            assert execute(old, off, num, den) == expected, (name, num, den, 'stock')
            assert execute(new, section['address'], num, den) == expected, (name, num, den, 'source')
            cases += 1
        sections.append({'name': name, 'address': section['address'], 'bytes': section['size']})
    report = {'source_sha256': sha(SOURCE.read_bytes()), 'elf_sha256': sha(path.read_bytes()),
              'target_cases': cases, 'sections': sections, 'source_admitted': False,
              'limits': ['Finite decoded-instruction battery with independent arithmetic oracle, including zero divisors.',
                         'Stage-one integration and hardware execution remain unqualified.']}
    (ROOT / 'docs/research/gx8002-stage1-divmod.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

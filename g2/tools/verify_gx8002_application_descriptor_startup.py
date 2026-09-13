# SPDX-License-Identifier: MIT
"""Qualify application descriptor placement through decoded loader and BSS clear."""
import json, re, subprocess
from build_gx8002_application_descriptor import build, ROOT, IMAGE, sha, Elf32
from analyze_gx8002_gsensor_state_references import mapped_offset, section_map, SDK_EVIDENCE
from verify_gx8002_uart_loader_setup import execute as loader
from compare_gx8002_clear_bss import execute as clear, START, END
from verify_gx8002_memcpy_source import decode


def verify():
    candidate = build()
    path = ROOT / 'build/gx8002-application-descriptor/descriptor.elf'
    elf = Elf32(path.read_bytes(), 'descriptor')
    base, offset, size = 0x20026d38, 0x18d4c, 36
    sections = sorted([s for s in elf.sections if s['flags'] & 2 and s['size']], key=lambda s: s['address'])
    data = b''.join(elf.contents(s) for s in sections)
    assert len(data) == size
    layout = section_map(); sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    for i in range(0, size, 4):
        assert mapped_offset(base + i, layout, sdk) == offset + i
    references = []; checked = 0
    registry = (ROOT / 'tools/build_gx8002_source_candidate.py').read_text()
    for kind, artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)", registry):
        if kind == 'application-descriptor': continue
        path = ROOT / 'build/gx8002-source-candidate' / kind / artifact
        owner = Elf32(path.read_bytes(), kind); checked += 1
        for section in owner.sections:
            if section['flags'] & 2 and section['size'] and section['address']:
                assert not (section['address'] < base + size and base < section['address'] + section['size']), (kind, section['name'])
        for symbol in owner.symbols():
            if symbol['name'] == 'open_cfw_gx8002_app_core_ops':
                assert symbol['value'] == base
                references.append({'kind': kind, 'elf_sha256': sha(path.read_bytes())})
    assert references
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock = IMAGE.read_bytes()
    path = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(path.read_bytes(), 'stock')
    assert elf.contents(next(s for s in elf.sections if s['name'] == '.data')) == stock
    code = decode(subprocess.check_output([pre, '-D', '--start-address=0x9fd0', '--stop-address=0xa04c', str(path)], text=True))
    path = ROOT / 'build/gx8002-clear-bss/clear.elf'
    elf = Elf32(path.read_bytes(), 'clear')
    row = json.loads((ROOT / 'docs/research/gx8002-clear-bss-verification.json').read_text())['functions'][0]
    section = next(s for s in elf.sections if s['name'] == row['section_name'])
    assert sha(elf.contents(section)) == row['compiled_sha256']
    writes = clear(decode(subprocess.check_output([pre, '-d', str(path)], text=True)), section['address'], 91)
    assert writes == [[a, 0] for a in range(START, END, 4)]
    patched = bytearray(stock); patched[offset:offset + size] = data
    cases = 0
    for mode in (0, 1, 0xffffffff, 0xaabbccdc):
        for seed in (0, 91, 0xffffffff):
            result, calls, memory = loader(code, bytes(patched), mode, seed)
            assert result == 0 and calls == [('read', 0x3000, 0x2000ffec, 4), ('read', 0xbe88, 0x10023400, 0x397c), ('entry', 0x10023500)]
            words = {base + i: memory[base - 0x10000000 + i] for i in range(0, size, 4)}
            assert b''.join(words[base + i].to_bytes(4, 'little') for i in range(0, size, 4)) == data
            for address, value in writes: words[address] = value
            assert all(words[base + i] == int.from_bytes(data[i:i + 4], 'little') for i in range(0, size, 4))
            assert words[base] == base + 4
            cases += 1
    return {'candidate': candidate, 'checked_artifacts': checked, 'references': references,
            'sdk_mapping_sha256': SDK_EVIDENCE, 'clear_elf_sha256': sha(path.read_bytes()),
            'startup_cases': cases, 'preserved_words': size // 4, 'clear_writes': len(writes),
            'source_admitted': False, 'hardware_qualified': False,
            'limits': ['Decoded primary loader with modeled flash reads loads compiled descriptor bytes through SDK-authenticated IRAM/DRAM alias. Decoded BSS clear preserves all nine initialized words.',
                       'Physical memory aliasing, typed callback definition reconciliation and composed application dispatch remain unqualified.']}


if __name__ == '__main__':
    result = verify(); assert json.loads(json.dumps(result)) == result
    (ROOT / 'docs/research/gx8002-application-descriptor-startup.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Application descriptor startup:', result['startup_cases'], 'cases;', result['preserved_words'], 'words preserved')

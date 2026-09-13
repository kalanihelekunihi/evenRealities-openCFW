# SPDX-License-Identifier: MIT
"""Compile semantic VAD sentinel and shared I2S pending defaults on macOS."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32


def build():
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_event_defaults.c'
    out = ROOT / 'build/gx8002-event-defaults'; out.mkdir(parents=True, exist_ok=True)
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([prefix + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding',
                    '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(out / 'defaults.o')], check=True)
    (out / 'defaults.ld').write_text('SECTIONS { .event_state 0x20026d30 : { *(.data.event_state) } }\n'
                                   'open_cfw_gx8002_i2s_pending = open_cfw_gx8002_event_state + 4;\n')
    path = out / 'defaults.elf'
    subprocess.run([prefix + 'ld', '-T', str(out / 'defaults.ld'), str(out / 'defaults.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'event defaults'); stock = IMAGE.read_bytes(); assert sha(stock) == IMAGE_SHA
    sections = [s for s in elf.sections if s['flags'] & 2 and s['size']]; assert len(sections) == 1
    section = sections[0]; body = elf.contents(section)
    assert section['address'] == 0x20026d30 and section['size'] == 8 and section['flags'] == 3
    assert body == stock[0x18d44:0x18d4c] and not elf.relocations(section['index'])
    symbol = next(s for s in elf.symbols() if s['name'] == 'open_cfw_gx8002_i2s_pending'); assert symbol['value'] == 0x20026d34
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert int.from_bytes(body[:4], 'little') not in range(8) and body[4] == 1 and body[5:] == bytes(3)
    return {'source_sha256': sha(source.read_bytes()), 'elf_sha256': sha(path.read_bytes()),
            'package_offset': 0x18d44, 'runtime_address': section['address'], 'bytes': 8,
            'compiled_sha256': sha(body), 'pending_alias': symbol['value'], 'source_admitted': False,
            'limits': ['Source-defined invalid prior VAD sentinel and initially pending byte compile exactly; three tail bytes are compiler-initialized struct padding.',
                       'Consumer execution, shared-field ownership and startup qualification remain pending. No opaque array or binary extraction used to define source.']}


if __name__ == '__main__':
    result = build()
    (ROOT / 'docs/research/gx8002-event-defaults-candidate.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Event defaults: 8 bytes exact, shared pending alias verified')

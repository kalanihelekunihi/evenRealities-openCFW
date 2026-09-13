# SPDX-License-Identifier: MIT
"""Compile upstream UART per-port header counters on macOS."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/common/uart_message_v2.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();upstream=authenticated_blob(sdk/rel,blob)
    assert b'static unsigned int s_recv_header_data_count[2] = {4, 4};' in upstream
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_header_defaults.c'
    out = ROOT / 'build/gx8002-uart-header-defaults'; out.mkdir(parents=True, exist_ok=True)
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([prefix + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding',
                    '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(out / 'defaults.o')], check=True)
    (out / 'defaults.ld').write_text('SECTIONS { .header_counts 0x20026c74 : { *(.data.header_counts) } }\n')
    path = out / 'defaults.elf'
    subprocess.run([prefix + 'ld', '-T', str(out / 'defaults.ld'), str(out / 'defaults.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'event defaults'); stock = IMAGE.read_bytes(); assert sha(stock) == IMAGE_SHA
    sections = [s for s in elf.sections if s['flags'] & 2 and s['size']]; assert len(sections) == 1
    section = sections[0]; body = elf.contents(section)
    assert section['address'] == 0x20026c74 and section['size'] == 8 and section['flags'] == 3
    assert body == stock[0x18c88:0x18c90] and not elf.relocations(section['index'])
    symbol = next(s for s in elf.symbols() if s['name'] == 's_recv_header_data_count'); assert symbol['value'] == 0x20026c74 and symbol['size']==8
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert all(int.from_bytes(body[i:i+4],'little')==4 for i in (0,4))
    return {'source_sha256': sha(source.read_bytes()), 'elf_sha256': sha(path.read_bytes()),
            'upstream':{'commit':SDK_COMMIT,'path':rel,'blob':blob,'sha256':sha(upstream)}, 'package_offset': 0x18c88, 'runtime_address': section['address'], 'bytes': 8,
            'compiled_sha256': sha(body), 'counter_address': symbol['value'], 'source_admitted': False,
            'limits': ['Named per-port parser counters match the pinned upstream initializer and original storage exactly.',
                       'Consumer execution, storage ownership and startup qualification remain pending. No opaque array or binary extraction used to define source.']}


if __name__ == '__main__':
    result = build()
    (ROOT / 'docs/research/gx8002-uart-header-defaults-candidate.json').write_text(json.dumps(result, indent=2) + '\n')
    print('UART header defaults: 8 bytes exact, upstream initializer authenticated')

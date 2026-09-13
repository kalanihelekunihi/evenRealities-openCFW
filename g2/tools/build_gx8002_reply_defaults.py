# SPDX-License-Identifier: MIT
"""Compile SDK reply packet defaults on macOS."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/common/uart_message_v2.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();upstream=authenticated_blob(sdk/rel,blob)
    assert b'#define MSG_SLAVE_MAGIC 0x58585542' in upstream
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_reply_defaults.c'
    out = ROOT / 'build/gx8002-reply-defaults'; out.mkdir(parents=True, exist_ok=True)
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([prefix + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding',
                    '-I'+str(sdk/'lvp/common'), '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(out / 'defaults.o')], check=True)
    (out / 'defaults.ld').write_text('SECTIONS { .reply_packet 0x20026d5c : { *(.data.reply_packet) } }\n')
    path = out / 'defaults.elf'
    subprocess.run([prefix + 'ld', '-T', str(out / 'defaults.ld'), str(out / 'defaults.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'event defaults'); stock = IMAGE.read_bytes(); assert sha(stock) == IMAGE_SHA
    sections = [s for s in elf.sections if s['flags'] & 2 and s['size']]; assert len(sections) == 1
    section = sections[0]; body = elf.contents(section)
    assert section['address'] == 0x20026d5c and section['size'] == 32 and section['flags'] == 3
    assert body == stock[0x18d70:0x18d90] and not elf.relocations(section['index'])
    symbol = next(s for s in elf.symbols() if s['name'] == 'open_cfw_gx8002_app_reply_state'); assert symbol['value'] == 0x20026d5c and symbol['size']==32
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert int.from_bytes(body[:4],'little')==0x58585542 and body[4:]==bytes(28)
    return {'source_sha256': sha(source.read_bytes()), 'elf_sha256': sha(path.read_bytes()),
            'upstream':{'commit':SDK_COMMIT,'path':rel,'blob':blob,'sha256':sha(upstream)}, 'package_offset': 0x18d70, 'runtime_address': section['address'], 'bytes': 32,
            'compiled_sha256': sha(body), 'counter_address': symbol['value'], 'source_admitted': False,
            'limits': ['SDK MSG_PACK field layout and named slave magic reproduce the initialized reply packet.',
                       'Existing helpers use a smaller local struct app_reply; reconcile their declarations and field meanings before source admission. Startup and consumers remain pending. No opaque array or binary extraction used to define source.']}


if __name__ == '__main__':
    result = build()
    (ROOT / 'docs/research/gx8002-reply-defaults-candidate.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Reply packet: 32 bytes exact using SDK MSG_PACK')

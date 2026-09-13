# SPDX-License-Identifier: MIT
"""Build an unadmitted typed application descriptor with authenticated targets."""
import json, subprocess
from analyze_gx8002_application_descriptor import analyze, ROOT, IMAGE, sha, Elf32


def build():
    evidence = analyze()
    out = ROOT / 'build/gx8002-application-descriptor'; out.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_application_descriptor.c'
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([prefix + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding',
                    '-Wall', '-Wextra', '-Werror', '-I' + str(ROOT / 'build/upstream-nationalchip-lvp-kws/lvp/app_core'),
                    '-c', str(source), '-o', str(out / 'descriptor.o')], check=True)
    names = {'AppInit': 'open_cfw_gx8002_sample_app_init',
             'AppEventResponse': 'open_cfw_gx8002_sample_event',
             'AppTaskLoop': 'open_cfw_gx8002_i2s_request_tick',
             'AppSuspend': 'open_cfw_gx8002_app_gpio_resume',
             'AppResume': 'open_cfw_gx8002_app_gpio_suspend',
             'app_name': 'open_cfw_gx8002_sample_app_labels'}
    script = out / 'descriptor.ld'
    script.write_text('SECTIONS { .app_core_ops 0x20026d38 : { *(.data.app_core_ops) }\n'
                      '.sample_application 0x20026d3c : { *(.data.sample_application) } }\n' +
                      ''.join(f'{symbol} = {evidence["descriptor_fields"][field]:#x};\n' for field, symbol in names.items()))
    path = out / 'descriptor.elf'
    subprocess.run([prefix + 'ld', '-T', str(script), str(out / 'descriptor.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'application descriptor'); stock = IMAGE.read_bytes(); rows = []
    assert len([s for s in elf.sections if s['flags'] & 2 and s['size']]) == 2
    for name, offset, size in (('app_core_ops', 0x18d4c, 4), ('sample_application', 0x18d50, 32)):
        section = next(s for s in elf.sections if s['name'] == '.' + name)
        body = elf.contents(section)
        assert section['flags'] == 3 and section['address'] == offset + 0x2000dfec
        assert len(body) == size and body == stock[offset:offset + size] and not elf.relocations(section['index'])
        rows.append({'section': section['name'], 'package_offset': offset, 'bytes': size, 'sha256': sha(body)})
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    return {'analysis': evidence, 'source_sha256': sha(source.read_bytes()), 'elf_sha256': sha(path.read_bytes()),
            'rows': rows, 'source_admitted': False, 'hardware_qualified': False,
            'limits': ['Typed descriptor compiles byte-exact on macOS. This object alone does not prove cross-translation-unit type compatibility.',
                       'SDK callback declaration reconciliation, startup mapping, dispatch composition and ownership admission remain pending.']}


if __name__ == '__main__':
    result = build()
    (ROOT / 'docs/research/gx8002-application-descriptor-candidate.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Typed application descriptor candidate: 36 bytes exact')

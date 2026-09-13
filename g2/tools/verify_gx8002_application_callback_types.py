# SPDX-License-Identifier: MIT
"""Verify SDK callback definitions together with their descriptor."""
import json, subprocess
from build_gx8002_application_descriptor import ROOT, sha, Elf32
from analyze_gx8002_application_descriptor import analyze
from verify_gx8002_analog_source import FLAGS


def verify():
    evidence = analyze()
    out = ROOT / 'build/gx8002-application-callback-types'; out.mkdir(parents=True, exist_ok=True)
    sources = ROOT / 'components/shared/gx8002'
    event = (sources / 'runtime_gx8002_sample_event.c').read_text()
    gpio = (sources / 'runtime_gx8002_app_gpio_power.c').read_text()
    (out / 'sample_event.c').write_text(event)
    (out / 'gpio_power.c').write_text(gpio)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    flags = ['-Os', *FLAGS[1:], '-I' + str(ROOT / 'build/upstream-nationalchip-lvp-kws/lvp/app_core')]
    # A single translation unit makes incompatible descriptor declarations a
    # compiler error instead of permitting unchecked declarations across files.
    descriptor = (sources / 'runtime_gx8002_application_descriptor.c').read_text()
    (out / 'type_contract.c').write_text(event + '\n' + gpio + '\n' + descriptor)
    subprocess.run([pre + 'gcc', *flags, '-fsyntax-only', str(out / 'type_contract.c')], check=True)
    rows = []
    for name, script, kind, artifact, report_name in (
            ('sample_event', 'gx8002-sample-event/candidate.ld', 'sample-event', 'candidate.elf', 'gx8002-sample-event-source-verification.json'),
            ('gpio_power', 'gx8002-app-gpio-power/offsets.ld', 'app-gpio-power', 'gpio-power.elf', 'gx8002-app-gpio-power-verification.json')):
        subprocess.run([pre + 'gcc', *flags, '-c', str(out / (name + '.c')), '-o', str(out / (name + '.o'))], check=True)
        linker = ROOT / 'build' / script
        subprocess.run([pre + 'ld', '-T', str(linker), str(out / (name + '.o')), '-o', str(out / (name + '.elf'))], check=True)
        changed = Elf32((out / (name + '.elf')).read_bytes(), name)
        report = json.loads((ROOT / 'docs/research' / report_name).read_text())
        sections = [s for s in changed.sections if s['flags'] & 2 and s['size']]
        checked = []
        for section in sections:
            body = changed.contents(section)
            matches = [r for r in report.get('functions', [report]) if r.get('compiled_sha256') == sha(body)]
            assert matches, (name, section['name'])
            assert any(any(o['package_offset'] + 0x101f6a74 == section['address'] for o in r.get('stock_occurrences', [])) for r in matches)
            checked.append({'section': section['name'], 'address': section['address'], 'bytes': len(body), 'sha256': sha(body)})
        assert not any(s['name'] and s['section'] == 0 for s in changed.symbols())
        rows.append({'name': name, 'staged_source_sha256': sha((out / (name + '.c')).read_bytes()), 'linker_sha256': sha(linker.read_bytes()), 'sections': checked})
    return {'sdk_headers': evidence['headers'], 'staged': rows, 'descriptor_contract_sha256': sha((out / 'type_contract.c').read_bytes()),
            'source_admitted': False, 'limits': ['Staged SDK APP_EVENT and void-pointer callbacks compile in the same translation unit as the typed descriptor under -Werror. All resulting allocated sections match reviewed original placement and hashes.',
                                               'Registered definitions are compiled together with descriptor declarations; linked allocated sections preserve reviewed bytes and addresses.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-application-callback-types.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Staged application SDK callback types passed')

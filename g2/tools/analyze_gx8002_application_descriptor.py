# SPDX-License-Identifier: MIT
"""Authenticate the remaining SDK-shaped application descriptor and source targets."""
import json, re, struct, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, SDK_COMMIT, sha, authenticated_blob
from build_transparent_image import Elf32


def analyze():
    stock = IMAGE.read_bytes(); assert sha(stock) == IMAGE_SHA
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    headers = {}
    for name in ('lvp/app_core/lvp_app.h', 'lvp/app_core/lvp_app_core.h'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + name], text=True).strip()
        headers[name] = {'blob': blob, 'sha256': sha(authenticated_blob(sdk / name, blob))}
    offset = 0x18d4c; address = offset + 0x2000dfec
    words = struct.unpack_from('<9I', stock, offset)
    assert words[0] == address + 4
    fields = ('app_name', 'AppInit', 'AppEventResponse', 'AppTaskLoop', 'AppSuspend', 'suspend_priv', 'AppResume', 'resume_priv')
    targets = dict(zip(fields, words[1:])); owners = {field: [] for field in fields}
    registry = (ROOT / 'tools/build_gx8002_source_candidate.py').read_text()
    for kind, artifact, report_name in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'(gx8002-[^']+\.json)'\)", registry):
        path = ROOT / 'build/gx8002-source-candidate' / kind / artifact
        elf = Elf32(path.read_bytes(), kind)
        report = json.loads((ROOT / 'docs/research' / report_name).read_text())
        for section in elf.sections:
            if not section['flags'] & 2 or section['type'] == 8: continue
            for field, target in targets.items():
                if not section['address'] <= target < section['address'] + section['size']: continue
                body = elf.contents(section)
                assert any(row.get('compiled_sha256') == sha(body) for row in report.get('functions', [report])), (kind, field)
                relative = target - section['address']
                item = {'kind': kind, 'section': section['name'], 'offset_in_section': relative, 'section_sha256': sha(body)}
                if field in ('app_name', 'suspend_priv', 'resume_priv'):
                    text = body[relative:].split(b'\0', 1)[0]
                    assert stock[target - 0x101f6a74:target - 0x101f6a74 + len(text) + 1] == text + b'\0'
                    item['text'] = text.decode('ascii')
                else:
                    symbols = [s['name'] for s in elf.symbols() if s['value'] == target and s['section'] == section['index']]
                    assert symbols; item['symbols'] = symbols
                owners[field].append(item)
    assert all(len(items) == 1 for items in owners.values()), owners
    return {'stock_sha256': IMAGE_SHA, 'sdk_commit': SDK_COMMIT, 'headers': headers,
            'package_offset': offset, 'bytes': 36, 'runtime_address': address,
            'app_core_ops_target': words[0], 'descriptor_fields': targets, 'owners': owners,
            'source_admitted': False,
            'limits': ['All eight descriptor fields resolve to reviewed source sections. Layout agrees with upstream LVP_APP; startup and typed compiled descriptor still pending.',
                       'Callback type compatibility is separately verified by compiling actual definitions with the descriptor in one translation unit. This address analysis alone does not prove C type compatibility.']}


if __name__ == '__main__':
    result = analyze()
    (ROOT / 'docs/research/gx8002-application-descriptor-analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Application descriptor: 36 bytes, eight source-owned fields')

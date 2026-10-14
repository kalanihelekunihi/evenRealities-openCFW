#!/usr/bin/env python3
"""Compare official Infineon widget typedef revisions on Cortex-M0+."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
GIT = ROOT / 'third-party/upstream/infineon-capsense'
COMMITS = {
    '4.0.0': '2dc8cc7ff14998a1b7bd4d412b5a11db35f0794d',
    '5.0.0': 'a4aa9306f7e4323994902f0baf5b1570ffbbfe59',
    '6.10.0': '247a9a0f79eb976f144f5fbeb29488c1c2606517',
    '11.0.0': '36580294e1587b2df8193f254f7e9b9b4aa6dd13',
}
NAMES = ['cy_stc_capsense_adaptive_filter_config_t',
         'cy_stc_capsense_ballistic_config_t',
         'cy_stc_capsense_advanced_touchpad_config_t',
         'cy_stc_capsense_widget_config_t']

def source(commit, file):
    return subprocess.check_output(['git', '-C', str(GIT), 'show', f'{commit}:{file}'], text=True)

def typedef(text, name):
    for match in re.finditer(r'typedef struct\s*\{.*?\}\s*(cy_\w+_t)\s*;', text, re.S):
        if match.group(1) == name:
            return match.group(0)
    raise ValueError(name)

def main():
    rows = []
    for version, commit in COMMITS.items():
        structure = source(commit, 'cy_capsense_structure.h')
        lib = source(commit, 'cy_capsense_lib.h')
        row = {'version': version, 'commit': commit,
               'structure_sha256': hashlib.sha256(structure.encode()).hexdigest(),
               'lib_sha256': hashlib.sha256(lib.encode()).hexdigest(), 'variants': []}
        try:
            texts = {name: typedef((lib if name in NAMES[:2] else structure), name)
                     for name in NAMES}
        except ValueError as exc:
            row['missing_typedef'] = str(exc)
            rows.append(row)
            continue
        pointer_names = set(re.findall(r'\bcy_stc_\w+_t\b', texts[NAMES[-1]])) - set(NAMES)
        prelude = ['typedef unsigned char uint8_t;', 'typedef unsigned short uint16_t;',
                   'typedef signed short int16_t;', 'typedef unsigned int uint32_t;']
        prelude += [f'typedef struct {name} {name};' for name in sorted(pointer_names)]
        for fifth in (0, 1):
            for lp in (0, 1):
                label = f'v{version.replace(".", "_")}_f{fifth}_lp{lp}'
                path = OUT / f'{label}.c'
                path.write_text('\n'.join(prelude +
                    [f'#define CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN {fifth}',
                     f'#define CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP {lp}'] +
                    [texts[name] for name in NAMES] +
                    ['unsigned char widget_size_probe[sizeof(cy_stc_capsense_widget_config_t)];', '']))
                obj = OUT / f'{label}.o'
                proc = subprocess.run(['clang', '-target', 'armv6m-none-eabi',
                        '-mcpu=cortex-m0plus', '-mthumb', '-std=c11', '-ffreestanding',
                        '-c', str(path), '-o', str(obj)], capture_output=True, text=True)
                variant = {'fifth_gen': fifth, 'fifth_gen_lp': lp,
                           'source': str(path.relative_to(ROOT)),
                           'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'compile_returncode': proc.returncode,
                           'compiler_stderr': proc.stderr[:1000]}
                if proc.returncode == 0:
                    nm = subprocess.check_output(['arm-none-eabi-nm', '-S', str(obj)], text=True)
                    match = re.search(r'\b([0-9a-fA-F]{8})\s+B\s+widget_size_probe\b', nm)
                    assert match, nm
                    variant['widget_bytes'] = int(match.group(1), 16)
                row['variants'].append(variant)
        rows.append(row)
    result = {'schema': 'opencfw-touch-widget-history-layout-v1',
              'observed_native_stride_bytes': 144, 'rows': rows,
              'limits': ['Revision and feature-macro layout probe only; not a generated product initializer.',
                         'A size match alone does not prove type identity or field values.']}
    (OUT / 'history-layout.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps([(r['version'], [(v.get('widget_bytes'), v['compile_returncode'])
                                 for v in r['variants']]) for r in rows]))

if __name__ == '__main__':
    main()

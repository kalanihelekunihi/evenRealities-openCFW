#!/usr/bin/env python3
"""Compile pinned CapSense v11 widget typedef under target feature choices."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
STRUCTURE = ROOT / 'g2/analysis/c-source-completion-20261011/touch/capsense-v11-reference/cy_capsense_structure.h'
LIB = OUT / 'cy_capsense_lib_v11.h'
NAMES = ['cy_stc_capsense_adaptive_filter_config_t',
         'cy_stc_capsense_ballistic_config_t',
         'cy_stc_capsense_advanced_touchpad_config_t',
         'cy_stc_capsense_widget_config_t']

def typedef(text, name):
    for match in re.finditer(r'typedef struct\s*\{.*?\}\s*(cy_\w+_t)\s*;', text, re.S):
        if match.group(1) == name:
            return match.group(0)
    raise ValueError(name)

def main():
    texts = {name: typedef((LIB if name in NAMES[:2] else STRUCTURE).read_text(), name)
             for name in NAMES}
    pointer_names = set(re.findall(r'\bcy_stc_\w+_t\b', texts[NAMES[-1]])) - set(NAMES)
    prelude = ['typedef unsigned char uint8_t;', 'typedef unsigned short uint16_t;',
               'typedef signed short int16_t;', 'typedef unsigned int uint32_t;']
    prelude += [f'typedef struct {name} {name};' for name in sorted(pointer_names)]
    rows = []
    for fifth in (0, 1):
        for lp in (0, 1):
            name = f'widget_f{fifth}_lp{lp}'
            source = OUT / f'{name}.c'
            source.write_text('\n'.join(prelude +
                [f'#define CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN {fifth}',
                 f'#define CY_CAPSENSE_PLATFORM_BLOCK_FIFTH_GEN_LP {lp}'] +
                [texts[item] for item in NAMES] +
                ['unsigned char widget_size_probe[sizeof(cy_stc_capsense_widget_config_t)];', '']))
            obj = OUT / f'{name}.o'
            cmd = ['clang', '-target', 'armv6m-none-eabi', '-mcpu=cortex-m0plus',
                   '-mthumb', '-std=c11', '-ffreestanding', '-c', str(source), '-o', str(obj)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            row = {'fifth_gen': fifth, 'fifth_gen_lp': lp,
                   'source': str(source.relative_to(ROOT)),
                   'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                   'compile_returncode': proc.returncode,
                   'compiler_stderr': proc.stderr[:1500]}
            if proc.returncode == 0:
                nm = subprocess.check_output(['arm-none-eabi-nm', '-S', str(obj)], text=True)
                match = re.search(r'\b([0-9a-fA-F]{8})\s+B\s+widget_size_probe\b', nm)
                assert match, nm
                row['widget_bytes'] = int(match.group(1), 16)
                row['object'] = str(obj.relative_to(ROOT))
                row['object_sha256'] = hashlib.sha256(obj.read_bytes()).hexdigest()
            rows.append(row)
    result = {'schema': 'opencfw-touch-widget-layout-probe-v1',
              'structure_header': str(STRUCTURE.relative_to(ROOT)),
              'structure_header_sha256': hashlib.sha256(STRUCTURE.read_bytes()).hexdigest(),
              'lib_header': str(LIB.relative_to(ROOT)),
              'lib_header_sha256': hashlib.sha256(LIB.read_bytes()).hexdigest(),
              'observed_native_record_stride': 144,
              'rows': rows,
              'limits': ['Only pinned typedef layout under four feature macro choices is tested.',
                         'No generated product initializer or final symbol extent is inferred.']}
    (OUT / 'layout-matrix.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps([(r['fifth_gen'], r['fifth_gen_lp'], r.get('widget_bytes'),
                       r['compile_returncode']) for r in rows]))

if __name__ == '__main__':
    main()

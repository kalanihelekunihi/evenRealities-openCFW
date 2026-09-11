# SPDX-License-Identifier: MIT
"""Isolated native macOS size probes; never export a firmware provider."""
import json
import subprocess
from pathlib import Path

from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS, sha

ROOT = Path(__file__).resolve().parents[1]


def probe():
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_dw_spi_setup.c'
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-spi-setup-size-probe'
    out.mkdir(parents=True, exist_ok=True)
    config = out / 'include'
    config.mkdir(exist_ok=True)
    (config / 'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    (config / 'string.h').write_text('#include <types.h>\nvoid *memset(void *, int, size_t);\n')
    prefix = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    variants = [None, '-Oz', '-O2', '-fno-shrink-wrap', '-fno-tree-reassoc',
                '-fno-tree-forwprop', '-fno-thread-jumps',
                '-fno-guess-branch-probability', '-fno-if-conversion',
                '-fno-tree-ter', '-fno-expensive-optimizations',
                '-fno-peephole2', '-fno-ipa-ra', '-fno-schedule-insns',
                '-fno-schedule-insns2', '-fno-tree-ccp', '-fno-tree-bit-ccp',
                '-fno-forward-propagate', '-fno-cse-follow-jumps',
                '-fno-tree-dominator-opts', '-fno-crossjumping']
    rows = []
    for index, extra in enumerate(variants):
        obj = out / ('option-%02d.o' % index)
        flags = ['-Os', *FLAGS[1:], '-fno-jump-tables']
        if extra:
            flags.append(extra)
        subprocess.run([prefix + 'gcc', *flags, '-I' + str(config),
                        '-isystem', str(sdk / 'include'),
                        '-isystem', str(sdk / 'include/utility'),
                        '-c', str(source), '-o', str(obj)], check=True)
        elf = Elf32(obj.read_bytes(), str(obj))
        section = next(s for s in elf.sections
                       if s['name'] == '.text.open_cfw_gx8002_dw_spi_setup')
        payload = elf.contents(section)
        rows.append({'extra_option': extra, 'text_bytes': len(payload),
                     'object_text_sha256': sha(payload)})
    report = {'source_sha256': sha(source.read_bytes()), 'variants': rows,
              'original_envelope_bytes': 116, 'source_admitted': False,
              'limits': ['Unlinked size measurements only. No semantic qualification or firmware output.']}
    (ROOT / 'docs/research/gx8002-dw-spi-setup-size-probe.json').write_text(
        json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    result = probe()
    print('Minimum SPI setup text size:', min(r['text_bytes'] for r in result['variants']))

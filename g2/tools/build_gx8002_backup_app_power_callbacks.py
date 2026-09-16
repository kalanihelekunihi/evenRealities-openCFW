# SPDX-License-Identifier: MIT
"""Compile authenticated SDK application suspend/resume callbacks on macOS."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from build_gx8002_backup_uart_registration import extract
from build_transparent_image import Elf32


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-backup-app-power-callbacks'
    out.mkdir(exist_ok=True)
    records = []
    texts = {}
    for rel in ('lvp/app_core/lvp_app_core.c', 'lvp/app_core/lvp_app.h', 'lvp/app_core/lvp_app_core.h'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + rel], text=True).strip()
        raw = authenticated_blob(sdk / rel, blob)
        records.append({'path': rel, 'blob': blob, 'sha256': sha(raw)})
        texts[rel] = raw.decode()
        if rel.endswith('.h'):
            (out / rel.split('/')[-1]).write_bytes(raw)
    original = texts['lvp/app_core/lvp_app_core.c']
    source = original[:original.index('#include')] + '\n#include <stddef.h>\n#include "lvp_app.h"\nextern LVP_APP *app_core_ops;\n'
    source += '_Static_assert(offsetof(LVP_APP,AppSuspend)==16,"suspend callback ABI");\n'
    source += '_Static_assert(offsetof(LVP_APP,suspend_priv)==20,"suspend context ABI");\n'
    source += '_Static_assert(offsetof(LVP_APP,AppResume)==24,"resume callback ABI");\n'
    source += '_Static_assert(offsetof(LVP_APP,resume_priv)==28,"resume context ABI");\n'
    for name in ('_LvpAppSuspend', '_LvpAppResume'):
        # Only storage linkage changes; the pinned function body stays unchanged.
        source += extract(original, 'static int ' + name + '(void *priv)').replace('static int ', 'int ', 1)
    (out / 'callbacks.c').write_text(source)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    command = [pre + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fno-shrink-wrap', '-I', str(out), '-c', str(out / 'callbacks.c'), '-o', str(out / 'callbacks.o')]
    subprocess.run(command, check=True)
    script = '''SECTIONS {
.app_suspend 0x1000bdb0 : { *(.text._LvpAppSuspend) }
.app_resume 0x1000bdcc : { *(.text._LvpAppResume) }
}
app_core_ops = 0x20016f74;
ASSERT(SIZEOF(.app_suspend) <= 28, "suspend overflow")
ASSERT(SIZEOF(.app_resume) <= 28, "resume overflow")
'''
    (out / 'callbacks.ld').write_text(script)
    path = out / 'callbacks.elf'
    subprocess.run([pre + 'ld', '-T', str(out / 'callbacks.ld'), str(out / 'callbacks.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'callbacks')
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows = []
    for name, offset in (('.app_suspend', 0x446f0), ('.app_resume', 0x4470c)):
        section = next(s for s in elf.sections if s['name'] == name)
        body = elf.contents(section)
        rows.append({'section': name, 'address': section['address'], 'bytes': len(body), 'stock_byte_exact': body == stock[offset:offset + len(body)]})
    (out / 'callbacks.disassembly.txt').write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    result = {'sdk_commit': SDK_COMMIT, 'upstream_files': records, 'command': command, 'derived_source_sha256': sha(source.encode()), 'elf_sha256': sha(path.read_bytes()), 'sections': rows, 'source_admitted': False, 'hardware_qualified': False, 'limits': ['Watchdog feature disabled, matching recovered suspend control flow.', 'Application operations pointer remains externally bound; callbacks are source candidates, not a complete firmware.']}
    (ROOT / 'docs/research/gx8002-backup-app-power-callbacks.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

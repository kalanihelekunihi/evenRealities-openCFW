# SPDX-License-Identifier: MIT
"""Compile authenticated SDK PMU initialization on macOS."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from build_gx8002_backup_uart_registration import extract
from build_transparent_image import Elf32


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-backup-pmu-initialize'
    out.mkdir(exist_ok=True)
    records = []
    texts = {}
    for rel in ('lvp/common/lvp_pmu.c', 'lvp/common/lvp_pmu.h', 'include/driver/gx_pmu_ctrl.h'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + rel], text=True).strip()
        raw = subprocess.check_output(['git', '-C', str(sdk), 'cat-file', 'blob', blob])
        if (sdk / rel).exists():
            assert authenticated_blob(sdk / rel, blob) == raw
        records.append({'path': rel, 'blob': blob, 'sha256': sha(raw)})
        texts[rel] = raw.decode()
        if rel.endswith('.h'):
            (out / rel.split('/')[-1]).write_bytes(raw)
    original = texts['lvp/common/lvp_pmu.c']
    source = original[:original.index('#include')] + '\n#include <stddef.h>\n#include "lvp_pmu.h"\n#include "gx_pmu_ctrl.h"\nextern void *memset(void *, int, unsigned int);\n'
    source += original[original.index('#define SUSPEND_INFO_NUM'):original.index('static LVP_STANDBY_HANDLE s_handle;')]
    source += 'extern LVP_STANDBY_HANDLE s_handle;\n_Static_assert(sizeof(LVP_STANDBY_HANDLE)==144,"PMU state ABI");\n_Static_assert(offsetof(LVP_STANDBY_HANDLE,s_suspend_info_buffer)==16,"suspend table ABI");\n_Static_assert(offsetof(LVP_STANDBY_HANDLE,s_resume_info_buffer)==80,"resume table ABI");\n'
    source += extract(original, 'int LvpPmuInit(void)')
    (out / 'common.h').write_text('#include <stdint.h>\n')
    (out / 'callbacks.c').write_text(source)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    command = [pre + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fdata-sections', '-fno-common', '-fno-shrink-wrap', '-I', str(out), '-c', str(out / 'callbacks.c'), '-o', str(out / 'callbacks.o')]
    subprocess.run(command, check=True)
    script = """SECTIONS {
.pmu_init 0x1000a744 : { *(.text.LvpPmuInit) }
}
s_handle = 0x2002cb88;
memset = 0x100113c4;
gx_pmu_get_wakeup_source = 0x10003fb8;
ASSERT(SIZEOF(.pmu_init) <= 64, "PMU initializer overflow")
"""
    (out / 'callbacks.ld').write_text(script)
    path = out / 'callbacks.elf'
    subprocess.run([pre + 'ld', '-T', str(out / 'callbacks.ld'), str(out / 'callbacks.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'callbacks')
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows = []
    for name, offset in (('.pmu_init', 0x43084),):
        section = next(s for s in elf.sections if s['name'] == name)
        body = elf.contents(section)
        rows.append({'section': name, 'address': section['address'], 'bytes': len(body), 'stock_byte_exact': body == stock[offset:offset + len(body)]})
    (out / 'callbacks.disassembly.txt').write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    result = {'sdk_commit': SDK_COMMIT, 'upstream_files': records, 'command': command, 'derived_source_sha256': sha(source.encode()), 'elf_sha256': sha(path.read_bytes()), 'sections': rows, 'source_admitted': False, 'hardware_qualified': False, 'limits': ['Pinned SDK initializer and state type isolated unchanged; common.h supplies standard integer types. PMU state, wakeup source and memset remain external dependencies; complete firmware qualification remains pending.']}
    (ROOT / 'docs/research/gx8002-backup-pmu-initialize.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

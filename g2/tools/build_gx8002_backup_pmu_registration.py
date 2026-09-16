# SPDX-License-Identifier: MIT
"""Compile authenticated SDK PMU registration on macOS."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from build_gx8002_backup_uart_registration import extract
from build_transparent_image import Elf32


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-backup-pmu-registration'
    out.mkdir(exist_ok=True)
    records = []
    texts = {}
    for rel in ('lvp/common/lvp_pmu.c', 'lvp/common/lvp_pmu.h'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + rel], text=True).strip()
        raw = subprocess.check_output(['git', '-C', str(sdk), 'cat-file', 'blob', blob])
        if (sdk / rel).exists():
            assert authenticated_blob(sdk / rel, blob) == raw
        records.append({'path': rel, 'blob': blob, 'sha256': sha(raw)})
        texts[rel] = raw.decode()
        if rel.endswith('.h'):
            (out / rel.split('/')[-1]).write_bytes(raw)
    original = texts['lvp/common/lvp_pmu.c']
    source = original[:original.index('#include')] + '\n#include <stddef.h>\n#include "lvp_pmu.h"\nextern void *memcpy(void *, const void *, unsigned int);\n'
    source += original[original.index('#define SUSPEND_INFO_NUM'):original.index('static LVP_STANDBY_HANDLE s_handle;')]
    source += 'LVP_STANDBY_HANDLE s_handle;\n_Static_assert(sizeof(LVP_STANDBY_HANDLE)==144,"PMU state ABI");\n_Static_assert(offsetof(LVP_STANDBY_HANDLE,s_suspend_info_buffer)==16,"suspend table ABI");\n_Static_assert(offsetof(LVP_STANDBY_HANDLE,s_resume_info_buffer)==80,"resume table ABI");\n'
    source += extract(original, 'int LvpSuspendInfoRegist(LVP_SUSPEND_INFO *suspend_info)')
    source += extract(original, 'int LvpResumeInfoRegist(LVP_RESUME_INFO *resume_info)')
    (out / 'callbacks.c').write_text(source)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    command = [pre + 'gcc', '-O2', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fdata-sections', '-fno-common', '-fno-shrink-wrap', '-I', str(out), '-c', str(out / 'callbacks.c'), '-o', str(out / 'callbacks.o')]
    subprocess.run(command, check=True)
    script = """SECTIONS {
.pmu_suspend_registration 0x1000a784 : { *(.text.LvpSuspendInfoRegist) }
.pmu_resume_registration 0x1000a7f0 : { *(.text.LvpResumeInfoRegist) }
.pmu_state 0x2002cb88 (NOLOAD) : { *(.bss.s_handle) }
}
ASSERT(SIZEOF(.pmu_state) == 144, "PMU state size")
memcpy = 0x10011344;
ASSERT(SIZEOF(.pmu_suspend_registration) <= 108, "suspend registration overflow")
ASSERT(SIZEOF(.pmu_resume_registration) <= 108, "resume registration overflow")
"""
    (out / 'callbacks.ld').write_text(script)
    path = out / 'callbacks.elf'
    subprocess.run([pre + 'ld', '-T', str(out / 'callbacks.ld'), str(out / 'callbacks.o'), '-o', str(path)], check=True)
    elf = Elf32(path.read_bytes(), 'callbacks')
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    state = next(s for s in elf.sections if s['name']=='.pmu_state')
    assert state['type']==8 and state['size']==144
    assert 0x20017090 <= state['address'] and state['address']+state['size'] <= 0x2002d79c
    rows = []
    for name, offset in (('.pmu_suspend_registration', 0x430c4), ('.pmu_resume_registration', 0x43130)):
        section = next(s for s in elf.sections if s['name'] == name)
        body = elf.contents(section)
        rows.append({'section': name, 'address': section['address'], 'bytes': len(body), 'stock_byte_exact': body == stock[offset:offset + len(body)]})
    (out / 'callbacks.disassembly.txt').write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    result = {'sdk_commit': SDK_COMMIT, 'upstream_files': records, 'command': command, 'derived_source_sha256': sha(source.encode()), 'elf_sha256': sha(path.read_bytes()), 'sections': rows, 'source_admitted': False, 'hardware_qualified': False, 'limits': ['Pinned SDK registration bodies and state type isolated unchanged. PMU state is allocated as source BSS within the reset clear range; memcpy remains an external dependency; complete firmware qualification remains pending.']}
    (ROOT / 'docs/research/gx8002-backup-pmu-registration.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

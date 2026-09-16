# SPDX-License-Identifier: MIT
"""Compile authenticated SDK application event initialization on macOS."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from build_gx8002_backup_uart_registration import extract
from build_transparent_image import Elf32


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-backup-app-event-initialize'
    out.mkdir(exist_ok=True)
    records = []
    texts = {}
    for rel in ('lvp/app_core/lvp_app_core.c', 'lvp/app_core/lvp_app.h', 'lvp/app_core/lvp_app_core.h', 'lvp/common/lvp_queue.h', 'lvp/common/lvp_pmu.h'):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + rel], text=True).strip()
        raw = subprocess.check_output(['git', '-C', str(sdk), 'cat-file', 'blob', blob])
        if (sdk / rel).exists():
            assert authenticated_blob(sdk / rel, blob) == raw
        records.append({'path': rel, 'blob': blob, 'sha256': sha(raw)})
        texts[rel] = raw.decode()
        if rel.endswith('.h'):
            (out / rel.split('/')[-1]).write_bytes(raw)
    original = texts['lvp/app_core/lvp_app_core.c']
    source = original[:original.index('#include')] + '\n#include <stddef.h>\n#include "lvp_app.h"\n#include "lvp_queue.h"\n#include "lvp_pmu.h"\nextern LVP_APP *app_core_ops;\nextern LVP_QUEUE s_app_misc_event_queue;\nextern unsigned char s_app_misc_event_queue_buffer[64];\nextern int _LvpAppSuspend(void *);\nextern int _LvpAppResume(void *);\n#define LVP_APP_MISC_QUEUE_LEN 8\n_Static_assert(sizeof(APP_EVENT)==8,"event ABI");\n_Static_assert(sizeof(LVP_SUSPEND_INFO)==8,"suspend ABI");\n_Static_assert(sizeof(LVP_RESUME_INFO)==8,"resume ABI");\n'
    source += 'static const char suspend_name[] __attribute__((section(".power_suspend_name"))) = "_LvpAppSuspend";\nstatic const char resume_name[] __attribute__((section(".power_resume_name"))) = "_LvpAppResume";\n'
    source += extract(original, 'int LvpInitializeAppEvent(void)').replace('"_LvpAppSuspend"', '(void *)suspend_name').replace('"_LvpAppResume"', '(void *)resume_name')
    (out / 'callbacks.c').write_text(source)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    command = [pre + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fno-shrink-wrap', '-I', str(out), '-c', str(out / 'callbacks.c'), '-o', str(out / 'callbacks.o')]
    subprocess.run(command, check=True)
    script = """SECTIONS {
.app_event_init 0x1000bdfc : { *(.text.LvpInitializeAppEvent) }
.app_suspend_name 0x10013ab4 : { *(.power_suspend_name) }
.app_resume_name 0x10013ac4 : { *(.power_resume_name) }
}
app_core_ops = 0x20016f74;
s_app_misc_event_queue = 0x2002d784;
s_app_misc_event_queue_buffer = 0x2002d31c;
LvpQueueInit = 0x10009fa8;
_LvpAppSuspend = 0x1000bdb0;
_LvpAppResume = 0x1000bdcc;
LvpSuspendInfoRegist = 0x1000a784;
LvpResumeInfoRegist = 0x1000a7f0;
ASSERT(SIZEOF(.app_event_init) <= 96, "event initializer overflow")
ASSERT(SIZEOF(.app_suspend_name) <= 16, "suspend name overflow")
ASSERT(SIZEOF(.app_resume_name) <= 16, "resume name overflow")
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
    for name, offset in (('.app_event_init', 0x4473c), ('.app_suspend_name', 0x4c3f4), ('.app_resume_name', 0x4c404)):
        section = next(s for s in elf.sections if s['name'] == name)
        body = elf.contents(section)
        rows.append({'section': name, 'address': section['address'], 'bytes': len(body), 'stock_byte_exact': body == stock[offset:offset + len(body)]})
    (out / 'callbacks.disassembly.txt').write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    result = {'sdk_commit': SDK_COMMIT, 'upstream_files': records, 'command': command, 'derived_source_sha256': sha(source.encode()), 'elf_sha256': sha(path.read_bytes()), 'sections': rows, 'source_admitted': False, 'hardware_qualified': False, 'limits': ['Optional sensor, recording and watchdog features disabled to match recovered control flow.', 'SDK initializer body retained except replacing two string literals with explicitly placed source-defined arrays.', 'Standalone queue, power callback, application operations pointer and PMU registration dependencies use recovered addresses; full firmware and hardware qualification remain pending.']}
    (ROOT / 'docs/research/gx8002-backup-app-event-initialize.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

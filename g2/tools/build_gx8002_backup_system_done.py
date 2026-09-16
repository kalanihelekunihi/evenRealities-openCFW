# SPDX-License-Identifier: MIT
"""Compile authenticated SDK system completion hook on macOS."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from build_gx8002_backup_uart_registration import extract
from build_transparent_image import Elf32


def build():
    sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
    out = ROOT / 'build/gx8002-backup-system-done'
    out.mkdir(exist_ok=True)
    records = []
    texts = {}
    for rel in ('lvp/common/lvp_system_init.c',):
        blob = subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', SDK_COMMIT + ':' + rel], text=True).strip()
        raw = subprocess.check_output(['git', '-C', str(sdk), 'cat-file', 'blob', blob])
        if (sdk / rel).exists():
            assert authenticated_blob(sdk / rel, blob) == raw
        records.append({'path': rel, 'blob': blob, 'sha256': sha(raw)})
        texts[rel] = raw.decode()
        if rel.endswith('.h'):
            (out / rel.split('/')[-1]).write_bytes(raw)
    original = texts['lvp/common/lvp_system_init.c']
    source = original[:original.index('#include')] + extract(original, 'void LvpSystemDone(void)')
    (out / 'callbacks.c').write_text(source)
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    command = [pre + 'gcc', '-Os', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fdata-sections', '-fno-common', '-fno-shrink-wrap', '-I', str(out), '-c', str(out / 'callbacks.c'), '-o', str(out / 'callbacks.o')]
    subprocess.run(command, check=True)
    script = """SECTIONS {
.system_done 0x1000aacc : { *(.text.LvpSystemDone) }
}
ASSERT(SIZEOF(.system_done) <= 4, "system completion hook overflow")
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
    for name, offset in (('.system_done', 0x4340c),):
        section = next(s for s in elf.sections if s['name'] == name)
        body = elf.contents(section)
        rows.append({'section': name, 'address': section['address'], 'bytes': len(body), 'stock_byte_exact': body == stock[offset:offset + len(body)]})
    (out / 'callbacks.disassembly.txt').write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
    assert all(row['stock_byte_exact'] for row in rows)
    result = {'sdk_commit': SDK_COMMIT, 'upstream_files': records, 'command': command, 'derived_source_sha256': sha(source.encode()), 'elf_sha256': sha(path.read_bytes()), 'sections': rows, 'source_admitted': False, 'hardware_qualified': False, 'limits': ['The upstream completion hook is empty, matching the stock return instruction exactly; this is not a placeholder for an unknown implementation. Full firmware remains incomplete.']}
    (ROOT / 'docs/research/gx8002-backup-system-done.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))

#!/usr/bin/env python3
"""Build source-owned BINH-B stage1 ELF/layout probe under pinned CK804EF GCC."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SRC = ROOT / 'g2/components/gx8002/image_b_stage1_candidate'
OUT = HERE / 'build'
TOOL = ROOT / 'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
STOCK = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage1.bin'
IMAGE = 'opencfw/iar-base:10.10.2-local'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def crc32_mpeg2(data):
    crc = 0xffffffff
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ (0x04c11db7 if crc & 0x80000000 else 0)) & 0xffffffff
    return crc

def run(cmd):
    return subprocess.check_output(cmd, text=True)

def target(*argv):
    return run(['docker','run','--rm','--network=none','--platform','linux/amd64',
                '--mount',f'type=bind,src={ROOT},dst=/repo',
                '--mount',f'type=bind,src={TOOL},dst=/tool,readonly','-w','/repo',IMAGE,*argv])

def main():
    OUT.mkdir(exist_ok=True)
    sources = sorted(SRC.glob('*.c'))
    before = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    lines = ['set -e', 'out=g2/analysis/c-source-completion-20261011/codec/image_b_stage1_candidate/build']
    common = '/tool/bin/csky-abiv2-elf-gcc -mcpu=ck804ef -mhard-float -Os -fno-builtin -fdata-sections -std=gnu11 -Wall -Wextra -Werror'
    for p in sources:
        rel = p.relative_to(ROOT)
        include = '-I third-party/upstream/nationalchip-lvp-kws/include'
        if p.stem == 'backup_stage1_clock_gate':
            include += ' -Wno-error=sign-compare -I g2/analysis/c-source-completion-20261011/codec/image_b_stage1_candidate/include -I third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include'
        lines.append(f'{common} {include} -c {rel} -o "$out/{p.stem}.o"')
    lines += ['/tool/bin/csky-abiv2-elf-ld -r "$out"/backup_stage1_*.o -o "$out/image_b_stage1_loader_candidate.o"',
              '/tool/bin/csky-abiv2-elf-ld -T g2/analysis/c-source-completion-20261011/codec/image_b_stage1_candidate/layout_probe.ld -Map "$out/layout_probe.map" -o "$out/layout_probe.elf" "$out"/backup_stage1_*.o',
              '/tool/bin/csky-abiv2-elf-objcopy -O binary "$out/layout_probe.elf" "$out/layout_probe.bin"']
    target('sh','-c','; '.join(lines))
    after = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    assert before == after, 'stage1 source changed during build'
    stock = STOCK.read_bytes()
    binary = (OUT/'layout_probe.bin').read_bytes()
    ranges = {'vectors':(0,0x100),'reset_prefix':(0x100,0x11a),
              'reset_tail':(0x122,0x132),'clock_param':(0x14c8,0x1668),
              'clock_sources':(0x1688,0x16d8),'clock_dto_div':(0x16d8,0x1720),
              'runtime_globals':(0x1720,0x1734)}
    checks = {name:binary[a:b] == stock[a+0x18:b+0x18] for name,(a,b) in ranges.items()}
    assert all(checks.values()), checks
    assert len(binary) == 0x1734 and len(binary) < 0x3000
    header = struct.pack('<4sIIIII', b'BINH', 0x55aa55aa, 0x203,
                         0x1408c, 0x3000, 0x20000000)
    assert header == stock[:24]
    package = bytearray(0x3000)
    package[:24] = header
    package[24:24+len(binary)] = binary
    crc = crc32_mpeg2(package[24:0x2ffc])
    struct.pack_into('<I', package, 0x2ffc, crc)
    assert crc32_mpeg2(stock[24:0x2ffc]) == int.from_bytes(stock[0x2ffc:0x3000], 'little')
    (OUT/'layout_probe_stage1_binh.bin').write_bytes(package)
    obj = OUT/'image_b_stage1_loader_candidate.o';elf=OUT/'layout_probe.elf'
    r={'result':'PASS_LAYOUT_PROBE','image':'BINH B stage1 separate CK804EF',
       'source_complete':False,'stock_sha256':sha(STOCK),
       'source_snapshot_coherent':True,
       'sources':[{'path':str(p.relative_to(ROOT)),'sha256':before[str(p.relative_to(ROOT))],
                   'object_sha256':sha(OUT/f'{p.stem}.o')} for p in sources],
       'relocatable_sha256':sha(obj),'elf_sha256':sha(elf),'binary_sha256':sha(OUT/'layout_probe.bin'),
       'entry':'0x10000100','linked_binary_bytes':len(binary),'stage1_extent':0x3000,
       'generated_stage1_binh_sha256':sha(OUT/'layout_probe_stage1_binh.bin'),
       'generated_stage1_crc32_mpeg2':hex(crc),
       'stock_equal_ranges':checks,'range_semantics':'Runtime load offsets, stock file offsets are +0x18',
       'interstage_reset_contract':'0x10003100',
       'limits':['Linker uses authenticated stage2 entry absolute symbol; stage2 executable linkage is separate.',
                 'Clock/MMIO and physical IRAM/DRAM alias behavior remain unqualified.',
                 'BINH header/footer/padding are derived by an experimental packer; no complete stage2 is appended.',
                 'Whole native body/effect equivalence and alternate transport paths remain open.']}
    (HERE/'layout-probe-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'elf_sha256':r['elf_sha256'],'units':len(sources),'binary_bytes':len(binary),'stock_ranges':checks},indent=2))

if __name__=='__main__':
    main()

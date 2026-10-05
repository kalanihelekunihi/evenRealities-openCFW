#!/usr/bin/env python3
"""Read-only authentication and disassembly for the Apollo scheduler resume seam."""
from __future__ import annotations
import hashlib, json, pathlib, struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

ROOT = pathlib.Path(__file__).resolve().parents[4]
OUT = pathlib.Path(__file__).resolve().parent
GH = ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29'
IMG = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = 0x438000
EXPECTED_IMAGE_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
TARGETS = {
    0x454d7c: (12, '3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2'),
    0x454dcc: (306, '548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09'),
    0x45504c: (338, '438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050'),
    0x455876: (38, 'a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598'),
    0x4420bc: (18, '2f99a4f1a4c654feb8c6d0b89bd975cf7c2acee3ad5b18ddf086097ed3f100da'),
    0x4420d0: (24, '5809638c22f928d2b32cd21cc9b92a292fad24cd8b8008de4ad92b9faeaba0d4'),
    0x4420e8: (44, 'bfd3ddb76c61ad634a3f58ed203260da3834895b646c9dffada546f9dc9d2a31'),
}

def sha(b): return hashlib.sha256(b).hexdigest()
raw = IMG.read_bytes()
assert sha(raw) == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
image = raw[32:]
assert sha(image) == EXPECTED_IMAGE_SHA and len(image) == 3523364
run = json.loads((GH/'RUN.json').read_text())
assert run['image_sha256'] == EXPECTED_IMAGE_SHA and int(run['base'], 16) == BASE
rows = [json.loads(x) for x in (GH/'functions-000.jsonl').read_text().splitlines() if x.strip()]
by_entry = {int(x['entry'],16):x for x in rows}
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail = True
out=[]; observed={}
for addr,(n,h) in TARGETS.items():
    row=by_entry[addr]
    assert row['body_bytes']==n and row['body_sha256']==h
    # All selected entries are represented by one contiguous census range.
    ranges=row['ranges']; assert len(ranges)==1
    lo,hi=(int(z,16) for z in ranges[0]); assert lo==addr and hi-lo+1==n
    off=addr-BASE; blob=image[off:off+n]
    assert len(blob)==n and sha(blob)==h
    observed[addr]={'bytes':n,'sha256':h,'body_end_exclusive':hex(addr+n),'callees':row.get('callees',[]),'callers':sorted(hex(c) for c,r in by_entry.items() if f'{addr:08x}' in r.get('callees',[]))}
    out.append(f'\n== 0x{addr:08x} bytes={n} sha256={h} ==')
    for ins in md.disasm(blob,addr): out.append(f'{ins.address:08x}: {ins.bytes.hex():<12} {ins.mnemonic:<8} {ins.op_str}')
# Resolve PC-relative literal loads relevant to the main routines; assert their contents.
# Thumb literal LDR encoding T1/T2 is decoded by Capstone; collect aligned PC + immediate targets and words.
def lit(addr, imm):
    return ((addr+4)&~3)+imm
expected_literals={
    (0x454d7c,0x6e8):(0x455468,0x20074a58),
    (0x454dd2,0x694):(0x455468,0x20074a58),
    (0x454dfa,0x3a4):(0x4551a0,0x20074a30),
    (0x454e54,0x354):(0x4551ac,0x20074a38),
    (0x454e64,0x348):(0x4551b0,0x2006a49c),
    (0x454e9c,0x304):(0x4551a4,0x20074a20),
    (0x454eaa,0xb68):(0x455a14,0x20074a44),
    (0x454eb0,0x8f4):(0x4557a8,0x20073d24),
    (0x454ec2,0xb54):(0x455a18,0x20074a40),
    (0x455050,0x414):(0x455468,0x20074a58),
    (0x45505c,0x40c):(0x45546c,0x20074a34),
    (0x45506a,0x404):(0x455470,0x20074a24),
    (0x455086,0x3ec):(0x455474,0x20074a28),
    (0x455090,0xa64):(0x455af8,0x20074a48),
    (0x45509e,0x684):(0x455724,0x20074a50),
    (0x455106,0xa4):(0x4551ac,0x20074a38),
    (0x455114,0x98):(0x4551b0,0x2006a49c),
    (0x45514c,0x54):(0x4551a4,0x20074a20),
    (0x45515a,0x314):(0x455470,0x20074a24),
    (0x45516e,0x34):(0x4551a4,0x20074a20),
    (0x455172,0x3c):(0x4551b0,0x2006a49c),
    (0x455182,0x890):(0x455a14,0x20074a44),
    (0x455190,0x884):(0x455a18,0x20074a40),
    (0x455876,0x7d8):(0x456050,0x20074a24),
    (0x455886,0x7d8):(0x456060,0x20074a50),
}
for (pc,imm),(target,value) in expected_literals.items():
    assert lit(pc,imm)==target
    assert struct.unpack_from('<I',image,target-BASE)[0]==value
# Verify the pinned source files against the upstream Git tree blob ids (sha1 git blob format).
def git_blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
source=ROOT/'g2/build/foundation/freertos-upstream/tasks.c'
source_bytes=source.read_bytes()
assert git_blob_sha(source_bytes)=='d97085d8736905c1eeb9d9e871c81e5970ee70ed'
assert sha(source_bytes)=='14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463'
# Key static caller census: direct reference lists, restricted to the known scheduler APIs.
callers={}
for target in (0x454d7c,0x454dcc): callers[hex(target)]=observed[target]['callers']
result={'image':{'path':str(IMG.relative_to(ROOT)),'ota_sha256':sha(raw),'image_sha256':sha(image),'base':hex(BASE),'bytes':len(image)},'ghidra_run':str((GH/'RUN.json').relative_to(ROOT)),'targets':{hex(k):v for k,v in observed.items()},'resolved_literals':[{ 'load_pc':hex(pc),'literal_address':hex(t),'value':hex(v)} for (pc,_),(t,v) in expected_literals.items()],'direct_callers':callers,'upstream_tasks_c':{'path':str(source.relative_to(ROOT)),'git_blob_sha1':git_blob_sha(source_bytes),'sha256':sha(source_bytes),'commit':'def7d2df2b0506d3d249334974f51e427c17a41c'},'verifier_sha256':sha(pathlib.Path(__file__).read_bytes()),'disassembly_file':'disassembly.txt'}
(OUT/'disassembly.txt').write_text('\n'.join(out)+'\n')
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'verified_targets':len(TARGETS),'resume_bytes':TARGETS[0x454dcc][0],'tick_helper_bytes':TARGETS[0x45504c][0],'direct_suspend_callers':len(callers[hex(0x454d7c)]),'direct_resume_callers':len(callers[hex(0x454dcc)]),'results':str(OUT/'results.json')},indent=2))

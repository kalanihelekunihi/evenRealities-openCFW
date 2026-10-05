#!/usr/bin/env python3
"""Re-authenticate bounded WSF/radio handoff evidence from the pinned image."""
from pathlib import Path
import hashlib, json, struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
ROOT = Path(__file__).resolve().parents[4]
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
CORPUS = ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29'
OUT = Path(__file__).resolve().parent
IMAGE_BASE = 0x438000
FILE_RUNTIME_BASE = 0x437fe0
TARGETS = {
  0x43c0e4: (8, 'd228ee6e554e7763e9cd764cd9f07d3074feac13e9fd05250611ffa1079041fc', 'FUN_0043c0e4'),
  0x52b8a4: (18, 'e0ff3f4fa338e939616823c70ae7fc13df075b7de32178db2810cf9eb39edb87', 'WsfCsEnter'),
  0x52b8b6: (18, '8685a9a54cba4040bb297f58f5bc9e0d5beed1f46a7159363edc8f80648e824c', 'WsfCsExit'),
  0x52b8d8: (70, 'a7a1285078ac515a4fea7ad18a50ab44ec84ba9f1c39e07df875dfa0f8681465', 'WsfSetOsSpecificEvent'),
  0x52b91e: (64, '62fda22da8f5aec6255e52e820a4570a593fa4637a710ce93ebfbdca428f7db8', 'WsfSetEvent'),
  0x52b95e: (30, 'feaf10178e32248aebd53109fd9c1a95e1d757484102fc7a775203160e257ff7', 'WsfTaskSetReady'),
  0x52b980: (30, '614f7f6c030d12ac7cb0ace224d26318a3089bc47a0d1fc24a17cf51cb7a396b', 'WsfOsSetNextHandler'),
  0x52b9b2: (30, 'f9c905e97f08e91afc84d8c6df9ed24e71e26accbea503f8f423f98e8e8ff6bb', 'WsfOsInit'),
  0x52b9d0: (232, '49ba08ce0c35eb58c098babd1ad0e4d68c303c67bf8e2543be552511732474d8', 'wsfOsDispatcher'),
  0x4b4a7c: (28, 'bf48e7e49fa879179ba8fba858ab918d2966384cae9b3cdf511f9189dd7a0cb1', 'HciDrvHandlerInit'),
  0x4b4a98: (26, '8aaad9561f503147d8dab516f5dcbed5b36fdef2ad0dc7965c8e1dc2a136ca28', 'HciDrvIntService'),
  0x4b7f64: (346, '74c187e6005693748a5b71bea5ec6f2e53a5e10d11a6eb01c3b880a8f384e5de', '_bleExactleStackInit'),
}
def sha(b): return hashlib.sha256(b).hexdigest()
raw = OTA.read_bytes()
assert sha(raw) == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
image = raw[32:]
assert len(image) == 3523364 and sha(image) == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
run = json.loads((CORPUS/'RUN.json').read_text())
assert run['image_sha256'] == sha(image) and run['base'] == '0x00438000'
rows = {}
for line in (CORPUS/'functions-000.jsonl').read_text().splitlines():
    r = json.loads(line)
    if r.get('entry') in {f'{a:08x}' for a in TARGETS}: rows[int(r['entry'],16)] = r
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN); md.detail = False
parts = []
results = {'ota_sha256':sha(raw),'image_sha256':sha(image),'image_size':len(image),'image_base':IMAGE_BASE,'file_runtime_base':FILE_RUNTIME_BASE,'authenticated_functions':[],'literals':{},'pass':True}
for addr,(n,want,name) in TARGETS.items():
    row=rows[addr]; assert row['body_bytes']==n and row['body_sha256']==want
    off=addr-IMAGE_BASE; body=image[off:off+n]
    assert len(body)==n and sha(body)==want,(name,sha(body),want)
    parts.append(f'## {name} @ 0x{addr:08x} ({n} bytes; sha256 {want})')
    parts.extend(f'0x{i.address:08x}: {i.bytes.hex():<8} {i.mnemonic:<8} {i.op_str}' for i in md.disasm(body,addr))
    results['authenticated_functions'].append({'address':f'0x{addr:08x}','name':name,'size':n,'sha256':want,'image_offset':off,'corpus_name':row['name'],'callees':row.get('callees',[])})
# The nominal 8-byte census function at 0x43c0e4 falls through into the memset-style shared tail.
fill_start=0x43c0e4; fill_size=0x66; fill_bytes=image[fill_start-IMAGE_BASE:fill_start-IMAGE_BASE+fill_size]
fill_sha=sha(fill_bytes); assert fill_sha=='34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a'
parts.append(f'## WsfOsInit clear path: fallthrough sequence @ 0x{fill_start:08x} ({fill_size} bytes; sha256 {fill_sha})')
parts.extend(f'0x{i.address:08x}: {i.bytes.hex():<8} {i.mnemonic:<9} {i.op_str}' for i in md.disasm(fill_bytes,fill_start))
results['wsf_state_clear_sequence']={'entry':'0x0043c0e4','size':fill_size,'sha256':fill_sha,'description':'8-byte Ghidra function entry falls through into aligned byte/halfword and word-fill body ending at 0x43c148; WsfOsInit calls it with state base, length 0x40, fill 0.'}
# literal words confirmed in the exact locked image, as referenced by PC-relative loads.
lits={0x52bab8:0x20075045,0x52babc:0x20074ef0,0x52bac0:0xe000ed04,0x52bac4:0x20073230,0x4b4da4:0x20074fcb,0x4b4d94:0x20074640}
for a,v in lits.items():
    got=struct.unpack_from('<I',image,a-IMAGE_BASE)[0]; assert got==v,(hex(a),hex(got),hex(v))
    results['literals'][f'0x{a:08x}']={'value':f'0x{got:08x}','image_offset':a-IMAGE_BASE}
# Capture relevant stack-init call sites and the registration store, tied to exact function body bytes.
stack=image[0x4b7f64-IMAGE_BASE:0x4b7f64-FILE_RUNTIME_BASE+346]
# Thumb BL instructions are 4 bytes; sites below are independently visible in decoded instruction stream.
calls=[]
for i in md.disasm(stack,0x4b7f64):
    if i.mnemonic=='bl' and i.op_str.strip()=='#0x52b980': calls.append(i.address)
assert calls == [0x4b7ff4,0x4b8002,0x4b803e,0x4b8058,0x4b8072,0x4b8096,0x4b80a4,0x4b80b2], [hex(x) for x in calls]
results['stack_init_registration_calls']=[f'0x{x:08x}' for x in calls]
results['radio_registration']='WsfOsInit clears the 0x40-byte state object via the 0x43c0e4 fallthrough fill path, so the next-handler counter at +0x3d is zero before registration. The eighth WsfOsSetNextHandler call returns 7; HciDrvHandlerInit stores that returned byte to 0x20074fcb.'
# Create each output once; later runs must reproduce it byte-for-byte.
for path,content in ((OUT/'results-corrected.json',json.dumps(results,indent=2)+'\n'),(OUT/'disassembly-corrected.txt','\n'.join(parts)+'\n')):
    if path.exists(): assert path.read_text()==content,f'{path} differs from verified output'
    else: path.write_text(content)
print('PASS',len(TARGETS),'function entries, 102-byte fill path, 6 literals, 8 registration calls; outputs match')

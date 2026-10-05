#!/usr/bin/env python3
"""Read-only hash, literal, vector, and caller checks for original Apollo tick code."""
from __future__ import annotations
import hashlib, json, pathlib, struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
ROOT=pathlib.Path(__file__).resolve().parents[4]
OUT=pathlib.Path(__file__).resolve().parent
IMG=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
GH=ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29'
BASE=0x438000

def sha(b): return hashlib.sha256(b).hexdigest()
def git_blob_sha(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
raw=IMG.read_bytes(); image=raw[32:]
assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert sha(image)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
assert len(image)==3523364
run=json.loads((GH/'RUN.json').read_text()); assert run['image_sha256']==sha(image) and int(run['base'],16)==BASE
rows=[json.loads(x) for x in (GH/'functions-000.jsonl').read_text().splitlines() if x.strip()]
by={int(x['entry'],16):x for x in rows}
expected={
 0x45504c:(338,'438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050'),
 0x442114:(32,'2999c107f0c2c7a14aa1dffb07531b0b9389af39295a4ae606201faf02675a6f'),
 0x4563b4:(114,'43a3151849cd96e46d45ad12bb338ea09f586e9fe734b01d485fb9b21c6775fa'),
 0x455876:(38,'a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598'),
}
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB); md.detail=True
funcs={}; dis=[]
for addr,(n,h) in expected.items():
 row=by[addr]; assert row['body_bytes']==n and row['body_sha256']==h
 assert len(row['ranges'])==1
 lo,hi=(int(a,16) for a in row['ranges'][0]); assert (lo,hi)==(addr,addr+n-1)
 code=image[addr-BASE:addr-BASE+n]; assert len(code)==n and sha(code)==h
 ins=list(md.disasm(code,addr))
 funcs[hex(addr)]={'bytes':n,'sha256':h,'end_exclusive':hex(addr+n),'callees':row.get('callees',[]),'callers':sorted(hex(c) for c,r in by.items() if f'{addr:08x}' in r.get('callees',[]))}
 dis.append(f'== {addr:#010x} bytes={n} sha256={h} ==')
 dis.extend(f'{i.address:08x}: {i.bytes.hex():<12} {i.mnemonic:<8} {i.op_str}' for i in ins)
# The SysTick exception vector (slot 15) is Thumb address 0x442114 | 1.
vector=struct.unpack_from('<I',image,15*4)[0]
assert vector==0x442115
# Authenticated PC-relative literal references within the tick helper.
literals={
 (0x455050,0x414):(0x455468,0x20074a58), # uxSchedulerSuspended
 (0x45505c,0x40c):(0x45546c,0x20074a34), # xTickCount
 (0x45506a,0x404):(0x455470,0x20074a24), # pxDelayedTaskList cell
 (0x455086,0x3ec):(0x455474,0x20074a28), # pxOverflowDelayedTaskList cell
 (0x455090,0xa64):(0x455af8,0x20074a48), # xNumOfOverflows
 (0x45509e,0x684):(0x455724,0x20074a50), # xNextTaskUnblockTime
 (0x455106,0xa4):(0x4551ac,0x20074a38),
 (0x455114,0x98):(0x4551b0,0x2006a49c),
 (0x45514c,0x54):(0x4551a4,0x20074a20),
 (0x45515a,0x314):(0x455470,0x20074a24),
 (0x45516e,0x34):(0x4551a4,0x20074a20),
 (0x455172,0x3c):(0x4551b0,0x2006a49c),
 (0x455182,0x890):(0x455a14,0x20074a44),
 (0x455190,0x884):(0x455a18,0x20074a40),
}
for (pc,imm),(target,value) in literals.items():
 assert ((pc+4)&~3)+imm==target
 assert struct.unpack_from('<I',image,target-BASE)[0]==value
# Verify the pinned FreeRTOS source identity.
tasks=ROOT/'g2/build/foundation/freertos-upstream/tasks.c'; tb=tasks.read_bytes()
assert git_blob_sha(tb)=='d97085d8736905c1eeb9d9e871c81e5970ee70ed'
assert sha(tb)=='14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463'
# Authenticate relevant evidence behind the earlier bounded one-due-task fixture.
prior=ROOT/'g2/build/pseudocode-first/20260930T190500Z/analysis'
p120=prior/'apollo-main-rtos-tick-original-due-task-fixture-12028/001'
p107=prior/'apollo-main-scheduler-tick-drain-map-10726/002'
assert json.loads((p120/'results.json').read_text())['cases']==168
receipt=json.loads((p107/'receipt.json').read_text()); assert receipt['accepted'] is False and receipt['status']=='partial'
prior_refs={
 'due_task_fixture':{'path':str(p120.relative_to(ROOT)),'cases':168,'replay_sha256':sha((p120/'replay.py').read_bytes()),'scope_sha256':sha((p120/'scope.md').read_bytes()),'receipt_sha256':sha((p120/'receipt.json').read_bytes())},
 'tick_drain_map':{'path':str(p107.relative_to(ROOT)),'accepted':False,'status':'partial','pseudocode_sha256':sha((p107/'pseudocode.md').read_bytes()),'replay_sha256':sha((p107/'replay.py').read_bytes()),'receipt_sha256':sha((p107/'receipt.json').read_bytes())},
}
# First level-1 vector only: retain the SysTick dispatch proof alongside bodies.
dis.append(f'\nVECTOR[15] @ 0x{BASE+60:08x}: {vector:08x} -> Thumb 0x{vector&~1:08x}')
result={'image':{'ota_path':str(IMG.relative_to(ROOT)),'ota_sha256':sha(raw),'image_sha256':sha(image),'base':hex(BASE),'bytes':len(image)},'ghidra_run':str((GH/'RUN.json').relative_to(ROOT)),'authenticated_functions':funcs,'systick_vector':{'slot':15,'address':hex(BASE+15*4),'raw_word':hex(vector),'thumb_target':hex(vector&~1)},'literal_references':[{'load_pc':hex(pc),'literal_address':hex(addr),'value':hex(val)} for (pc,_),(addr,val) in literals.items()],'upstream_tasks_c':{'path':str(tasks.relative_to(ROOT)),'commit':'def7d2df2b0506d3d249334974f51e427c17a41c','git_blob_sha1':git_blob_sha(tb),'sha256':sha(tb)},'prior_original_fixture_evidence':prior_refs,'verifier_sha256':sha(pathlib.Path(__file__).read_bytes()),'disassembly':'disassembly.txt'}
(OUT/'disassembly.txt').write_text('\n'.join(dis)+'\n')
(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'verified_functions':len(expected),'tick_body_bytes':expected[0x45504c][0],'systick_vector_target':hex(vector&~1),'prior_due_tick_fixture_cases':168,'result':str(OUT/'results.json')},indent=2))

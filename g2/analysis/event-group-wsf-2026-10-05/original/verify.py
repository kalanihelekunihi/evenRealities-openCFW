#!/usr/bin/env python3
"""Authenticate static Apollo EventGroup/timer-pend evidence and pinned source."""
from pathlib import Path
import hashlib, json, struct, re
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
if not __debug__:
    raise SystemExit('run with assertions enabled')
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
BASE=0x438000
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
GH=ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29'
UP=ROOT/'g2/build/foundation/freertos-upstream'
TARGETS={
 0x47ebd8:(32,'fe1edcf1a00dfbb69d8015b5958d6c24ffa6591e2fac90bb4e44ed8ebd33baf5','event-group create'),
 0x47ebf8:(280,'03d202c1154dc2084d02ce51526300623f3d75ffa263abf331276bfa950bbc79','event-group wait-bits'),
 0x47ed76:(168,'38b05fcf35bc59fd639e8a540e0e211d5d2a7026d1ad5fce97cd27f573084133','event-group set-bits'),
 0x47ee4a:(16,'449cf0bddf14c2b354d9a5d9a5610794c6087b1ef0ce99ab1c078e775877f996','event-group set-bits-from-ISR thunk'),
 0x47eb4a:(34,'0f7e8ec569481e5d0a1df6d44f8290da903768e0f31f129e19aa51429f203460','timer pend-function-from-ISR provider'),
 0x47ee30:(26,'8bad67993b977688e10e179b3fe078159b76bc981ab70983195e5704e18c7747','wait condition helper'),
 0x454d7c:(12,'3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2','scheduler suspend'),
 0x454dcc:(306,'548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09','scheduler resume'),
 0x45547c:(218,'aa14475cf28218296c4fd829c02080fc017a5fe137f476de47e747f1e920e33b','remove task from unordered event list'),
 0x4552ae:(100,'3a0c48a133434b13cf7f67eb907e45e8fddb79ce2fd1122948ac0a65dadeb83d','place task on unordered event list'),
 0x441952:(240,'09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08','queue-send-from-ISR boundary'),
 0x449590:(84,'6dfae64ebf472c51d4105d50434acfccd26b723a6d6da790eee981a529f4ed83','CMSIS osEventFlagsNew'),
 0x4495e4:(94,'11de6c596381befd11300bd6383f97b334847c3eafc74a7392bfe956629acce7','CMSIS osEventFlagsSet'),
 0x44969c:(128,'55efe563c27f16d40c0488e9a86351c934313b894a1428c89ddde96194ea8a08','CMSIS osEventFlagsWait'),
 0x52b8d8:(70,'a7a1285078ac515a4fea7ad18a50ab44ec84ba9f1c39e07df875dfa0f8681465','WsfSetOsSpecificEvent'),
 0x52b9b2:(30,'f9c905e97f08e91afc84d8c6df9ed24e71e26accbea503f8f423f98e8e8ff6bb','WsfOsInit'),
 0x52b9d0:(232,'49ba08ce0c35eb58c098babd1ad0e4d68c303c67bf8e2543be552511732474d8','wsfOsDispatcher'),
}
RAW_ONLY={0x47ee1e:(8,'','event-group-set callback thunk')}
def sha(b):return hashlib.sha256(b).hexdigest()
ota=OTA.read_bytes(); image=ota[32:]
assert sha(ota)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert sha(image)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701' and len(image)==3523364
run=json.loads((GH/'RUN.json').read_text()); assert run['base']=='0x00438000' and run['image_sha256']==sha(image)
rows=[json.loads(x) for x in (GH/'functions-000.jsonl').read_text().splitlines() if x.strip()]
by={int(r['entry'],16):r for r in rows}
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS); md.detail=True
functions={}; listing=[]; decoded_calls={}
for addr,(size,expected,name) in TARGETS.items():
    body=image[addr-BASE:addr-BASE+size]
    row=by[addr]
    assert len(body)==size and sha(body)==expected,(hex(addr),sha(body),expected)
    assert row['body_bytes']==size and row['body_sha256']==expected,(hex(addr),row)
    insns=[]; targets=[]
    listing.append(f'## {name} 0x{addr:08x} size={size} sha256={expected}')
    for i in md.disasm(body,addr):
        x={'pc':f'0x{i.address:08x}','bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str}
        if i.mnemonic in ('bl','blx'):
            op=i.op_str.split()[0].lstrip('#')
            try:
                target=int(op,0); targets.append({'pc':f'0x{i.address:08x}','target':f'0x{target:08x}'})
            except ValueError: pass
        insns.append(x); listing.append(f"0x{i.address:08x}: {i.bytes.hex():<8} {i.mnemonic:<10} {i.op_str}")
    assert sum(i.size for i in md.disasm(body,addr))==size
    functions[f'0x{addr:08x}']={'name':name,'size':size,'sha256':expected,'callees':row.get('callees',[]),'calls':targets,'instructions':insns}
    decoded_calls[addr]=targets
raw_funcs={}
for addr,(size,_,name) in RAW_ONLY.items():
    body=image[addr-BASE:addr-BASE+size]; raw_funcs[f'0x{addr:08x}']={'name':name,'size':size,'sha256':sha(body),'bytes':body.hex()}
    listing.append(f'## {name} 0x{addr:08x} size={size} sha256={sha(body)} (raw interval; no Ghidra function row)')
    for i in md.disasm(body,addr): listing.append(f'0x{i.address:08x}: {i.bytes.hex():<8} {i.mnemonic:<10} {i.op_str}')
# The callback's literal is a Thumb pointer to the preceding raw entry.
cb=image[0x47ee1e-BASE:0x47ee26-BASE]
assert cb.hex()=='80b5fff7a9ff01bd' and sha(cb)=='3497dc0fa15f3c8bf59fea82f558007401ba0b03fc81a0fb1c3087ce1a9b6a73'
assert cb.hex()=='80b5fff7a9ff01bd' and sha(cb)=='3497dc0fa15f3c8bf59fea82f558007401ba0b03fc81a0fb1c3087ce1a9b6a73'
def callees(addr): return [int(x['target'],16) for x in decoded_calls[addr]]
expected_calls={
 0x47eb4a:[0x441952],
 0x47ebf8:[0x5fa0a4,0x5fa0a4,0x5fa0a4,0x4558a4,0x5fa0a4,0x454d7c,0x47ee30,0x4552ae,0x454dcc,0x4420bc,0x455aca,0x4420d0,0x47ee30,0x4420e8],
 0x47ed76:[0x5fa0a4,0x5fa0a4,0x454d7c,0x45547c,0x454dcc],
 0x47ee4a:[0x47eb4a],
 0x449590:[0x44900e,0x47eb94,0x47ebd8],
 0x4495e4:[0x44900e,0x47ee4a,0x47ed64,0x47ed76],
 0x44969c:[0x44900e,0x47ebf8],
 0x52b8d8:[0x442228,0x47ee4a,0x47ed76,0x4420bc],
 0x52b9b2:[0x43c0e4,0x47ebd8],
 0x52b9d0:[0x52a574,0x52b8a4,0x52b8b6,0x4bf9b0,0x4bf9ec,0x52a542,0x52b8a4,0x52b8b6,0x52a574,0x52b99e,0x47ebf8],
}
for a,want in expected_calls.items():
    assert callees(a)==want,(hex(a),[hex(x) for x in callees(a)],[hex(x) for x in want])
def pc_literal(pc,imm): return ((pc+4)&~3)+imm
assert pc_literal(0x47ee52,8)==0x47ee5c and struct.unpack_from('<I',image,0x47ee5c-BASE)[0]==0x47ee1f
assert pc_literal(0x47eb60,8)==0x47eb6c and struct.unpack_from('<I',image,0x47eb6c-BASE)[0]==0x20074ab0
assert struct.unpack_from('<I',image,0x52babc-BASE)[0]==0x20074ef0
assert struct.unpack_from('<I',image,0x52bac4-BASE)[0]==0x20073230
wait_setup=image[0x52baa2-BASE:0x52bab6-BASE]
assert wait_setup.hex()=='5ff0ff3000900023012201210348006853f7a1f8'
direct={}
for target in (0x47ebd8,0x47ebf8,0x47ed76,0x47ee4a):
    direct[f'0x{target:08x}']=[{'entry':f'0x{r["entry"]}','name':r['name'],'sha256':r['body_sha256']} for r in rows if f'{target:08x}' in r.get('callees',[])]
tree=json.loads((UP/'tree.json').read_text()); commit=tree['sha']
def tree_row(name): return next(x for x in tree['tree'] if x['path']==name)
src_info={}
for name in ('event_groups.c','timers.c'):
    b=(UP/name).read_bytes(); row=tree_row(name); blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert blob==row['sha'],(name,blob,row['sha'])
    text=b.decode()
    assert 'FreeRTOS Kernel V10.5.1' in text and 'SPDX-License-Identifier: MIT' in text
    src_info[name]={'path':str((UP/name).relative_to(ROOT)),'size':len(b),'sha256':sha(b),'git_blob_sha1':blob,'pinned_blob_sha1':row['sha']}
event_src=(UP/'event_groups.c').read_text(); timer_src=(UP/'timers.c').read_text()
for marker in ('typedef struct EventGroupDef_t','eventCLEAR_EVENTS_ON_EXIT_BIT    0x01000000UL','eventUNBLOCKED_DUE_TO_BIT_SET    0x02000000UL','eventWAIT_FOR_ALL_BITS           0x04000000UL','eventEVENT_BITS_CONTROL_BYTES    0xff000000UL','EventBits_t xEventGroupWaitBits','EventBits_t xEventGroupSetBits','xEventGroupSetBitsFromISR','vEventGroupSetBitsCallback'):
    assert marker in event_src,marker
for marker in ('xTimerPendFunctionCallFromISR','xMessage.xMessageID = tmrCOMMAND_EXECUTE_CALLBACK_FROM_ISR','xQueueSendFromISR( xTimerQueue, &xMessage, pxHigherPriorityTaskWoken )','pxCallback->pxCallbackFunction( pxCallback->pvParameter1, pxCallback->ulParameter2 )'):
    assert marker in timer_src,marker
results={
 'verification':'PASS',
 'artifact':{'ota_sha256':sha(ota),'main_image_sha256':sha(image),'image_base':'0x00438000','image_size':len(image)},
 'functions':functions,'raw_intervals':raw_funcs,
 'literals':{'0x0047ee5c':'0x0047ee1f (Thumb callback 0x0047ee1e)','0x0047eb6c':'0x20074ab0 (timer queue handle global cell; code dereferences it)','0x0052babc':'0x20074ef0 (WSF EventGroupHandle_t cell)','0x0052bac4':'0x20073230 (WSF event-state base)','adjacent_word_0x0047eb70':'0x20074ab4'},
 'direct_callers':direct,
 'wsf_binding':{
  'creation':'WsfOsInit (0x0052b9b2) calls xEventGroupCreate-like body 0x0047ebd8 when *0x20074ef0 is zero, then stores the returned handle there.',
  'wake':'WsfSetOsSpecificEvent (0x0052b8d8) uses that handle and sets bits value 1 through 0x0047ed76 in task context or 0x0047ee4a in ISR context.',
  'wait':'wsfOsDispatcher (0x0052b9d0) waits on *0x20074ef0 with arguments (handle,1,clearOnExit=1,waitForAll=0,timeout=0xffffffff) through 0x0047ebf8.',
  'wait_argument_bytes':{'pc':'0x0052baa2','bytes':wait_setup.hex(),'register_stack_effect':'r0=-1 stored at [sp]; r3=0; r2=1; r1=1; r0 loaded from event-group handle cell *0x20074ef0; BL 0x0047ebf8.'},
  'cmsis':'osEventFlagsNew/Set/Wait (0x00449590/0x004495e4/0x0044969c) share the create/set/set-from-ISR/wait providers.'},
 'event_group_layout':{'handle_cell':'0x20074ef0','group_offset_0':'32-bit uxEventBits','group_offset_4':'List_t xTasksWaitingForBits (waiter list)','waiter_list_sentinel':'group + 0x0c (List_t offset +8; source List_t uses xListEnd)','list_head_pointer':'group + 0x10 (List_t offset +0xc)','creation_evidence':'allocator request 0x20 bytes; zero word at group+0; list initialization called with group+4; byte at group+0x1c cleared.'},
 'wait_control_flags_for_32bit_eventbits':{'clear_on_exit':'0x01000000 (upper control byte bit0)','unblocked_due_to_bit_set':'0x02000000 (upper control byte bit1)','wait_for_all':'0x04000000 (upper control byte bit2)','control_mask':'0xff000000','binary_evidence':'wait/set routines test and OR these exact masks; source selects these when configUSE_16_BIT_TICKS != 1.'},
 'set_waiter_semantics':'Task-context xEventGroupSetBits ORs user bits into group+0, walks every event waiter from list head to xListEnd, tests any/all based on 0x04000000, and calls vTaskRemoveFromUnorderedEventList (0x45547c) on each match with current bits OR 0x02000000. It accumulates requested bits from clear-on-exit waiters, clears their union after scanning all waiters, resumes the scheduler, and returns current bits. WaitBits (0x47ebf8) checks existing bits, returns immediately on a match, otherwise inserts the task event-list item into group+4 via 0x4552ae with wait mask/control bits and timeout; it suspends/resumes scheduling around shared-list operations. No direct task-notification API is called in these authenticated event-group bodies.',
 'isr_deferred_path':{
  'wrapper':'0x47ee4a receives (group,bits,higherPriorityTaskWoken), loads callback Thumb pointer 0x47ee1f (body 0x47ee1e), then calls 0x47eb4a.',
  'pend_provider':'0x47eb4a creates a 16-byte timer-command message on its stack: command word 0xfffffffe, callback pointer, group pointer, bits word. It calls queue boundary 0x441952 with xTimerQueue handle dereferenced through global cell 0x20074ab0, message pointer, original higher-priority-woken pointer, and r3=0.',
  'callback':'0x47ee1e calls task-context set-bits body 0x47ed76 with its two parameters.',
  'source_path':'Pinned timers.c xTimerPendFunctionCallFromISR fills a DaemonTaskMessage_t callback command and calls xQueueSendFromISR(xTimerQueue,...). Timer daemon command processing invokes callback fields for negative command IDs. The callback in pinned event_groups.c calls xEventGroupSetBits(group,bits).',
  'limit':'The queue-send boundary 0x441952 is authenticated here only as the immediate callee and argument path; deeper queue-full behavior, timer-queue creation state at the instant of an ISR, and daemon scheduling were not executed.'},
 'source':{'repository':'FreeRTOS/FreeRTOS-Kernel','commit':commit,'version':'FreeRTOS Kernel V10.5.1 (file headers)','license':'MIT (SPDX in file headers)','files':src_info,'byte_match_claim':False},
 'limits':['Static original-image decoding and pinned-source correspondence only; no firmware execution or scheduler/ISR simulation.','The local upstream subset contains event_groups.c and timers.c but not tasks.c, queue.c, or the exact FreeRTOSConfig.h; vTask* and queue provider contracts are bounded at authenticated binary call sites and pinned event/timer source.','Source correspondence is semantic and version-pinned, not compiler-byte identity.','The timer queue pointer cell is derived from the PC-relative literal at 0x47eb6c (value 0x20074ab0); adjacent word 0x47eb70 is recorded separately as 0x20074ab4, not treated as that LDR literal.']}
for path,content in ((OUT/'results-final.json',json.dumps(results,indent=2)+'\n'),(OUT/'disassembly-final.txt','\n'.join(listing)+'\n')):
    if path.exists(): assert path.read_text()==content,f'{path} differs; inspect before updating'
    else: path.write_text(content)
print('PASS',len(TARGETS),'authenticated function bodies, callback interval, pinned source files, and direct-call/literal assertions')

#!/usr/bin/env python3
"""Authenticate bounded xQueueGenericSendFromISR producer and pinned source evidence."""
from pathlib import Path
import hashlib, json, struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS

if not __debug__:
    raise SystemExit('assertions required')
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = 0x438000
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
GH = ROOT / 'g2/research/corpus/apollo-main/ghidra/open-2026-09-29'
UP = ROOT / 'g2/build/foundation/freertos-upstream'
TARGETS = {
 0x441952:(240,'09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08','xQueueGenericSendFromISR body'),
 0x441ed8:(134,'35c79bf50852c5f61d579981278509aa156ab8e18f57b4b6d6b7a88563682e36','copy-data-to-queue helper'),
 0x439be4:(104,'8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd','memory-copy helper'),
 0x455370:(246,'1a5d4850f0799e97548f23ee1617fc1de362f8d2a674301baa6facd579d13de4','task event-list removal / ready transition helper'),
 0x455876:(38,'a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598','task ready-list insertion helper'),
 0x454f10:(6,'43e18c3d205509129b075a8eb8c2c70afde30da1b933ac72d2963813aea8cfec','task-count read helper'),
 0x5fa0a4:(22,'f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323','interrupt mask helper'),
 0x5fa0ba:(14,'97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a','interrupt mask restore helper'),
 0x47eb4a:(34,'0f7e8ec569481e5d0a1df6d44f8290da903768e0f31f129e19aa51429f203460','event-group deferred timer-command producer'),
}
def sha(b): return hashlib.sha256(b).hexdigest()
ota=OTA.read_bytes(); image=ota[32:]
assert sha(ota)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert sha(image)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701' and len(image)==3523364
run=json.loads((GH/'RUN.json').read_text())
assert run['base']=='0x00438000' and run['image_sha256']==sha(image)
rows=[json.loads(s) for s in (GH/'functions-000.jsonl').read_text().splitlines() if s.strip()]
by={int(r['entry'],16):r for r in rows}
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS); md.detail=True
functions={}; listing=[]; calls={}
for addr,(size,want,name) in TARGETS.items():
    row=by[addr]
    span_end=int(row['body_end_inclusive'],16)+1
    body=image[addr-BASE:span_end-BASE]
    assert len(body)==span_end-addr and sha(body)==want,(hex(addr),sha(body))
    assert row['body_bytes']==size and row['body_sha256']==want
    insns=[]; targets=[]
    listing.append(f'## {name} @ 0x{addr:08x} ({size} Ghidra body bytes, {len(body)}-byte verified envelope, sha256 {want})')
    decoded=list(md.disasm(body,addr))
    assert sum(i.size for i in decoded)==len(body),(hex(addr),sum(i.size for i in decoded),len(body))
    for i in decoded:
        item={'pc':f'0x{i.address:08x}','bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str}
        if i.mnemonic in ('bl','blx'):
            try: targets.append({'pc':item['pc'],'target':f'0x{int(i.op_str.split()[0].lstrip("#"),0):08x}'})
            except ValueError: pass
        insns.append(item); listing.append(f'0x{i.address:08x}: {i.bytes.hex():<8} {i.mnemonic:<9} {i.op_str}')
    functions[f'0x{addr:08x}']={'name':name,'body_bytes':size,'span_bytes':len(body),'sha256':want,'ghidra_callees':row.get('callees',[]),'calls':targets,'instructions':insns}
    calls[addr]=[int(x['target'],16) for x in targets]
assert calls[0x441952]==[0x5fa0a4,0x5fa0a4,0x5fa0a4,0x5fa0a4,0x441ed8,0x455370,0x454f10,0x5fa0a4,0x5fa0ba]
assert calls[0x441ed8]==[0x45596e,0x439be4,0x439be4]
assert calls[0x455370]==[0x5fa0a4,0x455876]
assert calls[0x47eb4a]==[0x441952]
# Key Queue_t loads/stores and timer caller literal are present in the disassembly.
q=functions['0x00441952']['instructions']
assert any('0x40' in x['operands'] for x in q) and any('0x3c' in x['operands'] for x in q)
assert any('0x38' in x['operands'] for x in q) and any('0x45' in x['operands'] for x in q)
assert struct.unpack_from('<I',image,0x47eb6c-BASE)[0]==0x20074ab0
# Verify pinned tree identity for files used in semantic correspondence.
tree=json.loads((UP/'tree.json').read_text()); commit=tree['sha']
def tree_row(name): return next(x for x in tree['tree'] if x['path']==name)
sources={}
for name in ('queue.c','event_groups.c','timers.c'):
    b=(UP/name).read_bytes(); row=tree_row(name)
    blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert blob==row['sha'],(name,blob,row['sha'])
    text=b.decode()
    assert 'FreeRTOS Kernel V10.5.1' in text and 'SPDX-License-Identifier: MIT' in text
    sources[name]={'path':str((UP/name).relative_to(ROOT)),'size':len(b),'sha256':sha(b),'git_blob_sha1':blob,'pinned_blob_sha1':row['sha']}
qsrc=(UP/'queue.c').read_text()
for marker in ('typedef struct QueueDefinition','int8_t * pcHead','int8_t * pcWriteTo','List_t xTasksWaitingToSend','List_t xTasksWaitingToReceive','volatile UBaseType_t uxMessagesWaiting','UBaseType_t uxLength','UBaseType_t uxItemSize','volatile int8_t cTxLock','BaseType_t xQueueGenericSendFromISR','portSET_INTERRUPT_MASK_FROM_ISR()','prvCopyDataToQueue( pxQueue, pvItemToQueue, xCopyPosition )','xTaskRemoveFromEventList( &( pxQueue->xTasksWaitingToReceive ) )','portCLEAR_INTERRUPT_MASK_FROM_ISR( uxSavedInterruptStatus )','xReturn = pdPASS','xReturn = errQUEUE_FULL'):
    assert marker in qsrc,marker
# Keep exact source line anchors for reviewer navigation.
source_lines={}
for name in ('queue.c','event_groups.c','timers.c'):
    lines=(UP/name).read_text().splitlines()
    terms=('typedef struct QueueDefinition','BaseType_t xQueueGenericSendFromISR','static BaseType_t prvCopyDataToQueue','xTaskRemoveFromEventList( &( pxQueue->xTasksWaitingToReceive ) )','xTimerPendFunctionCallFromISR','xQueueSendFromISR( xTimerQueue')
    source_lines[name]=[{'line':n,'text':line.strip()} for n,line in enumerate(lines,1) if any(t in line for t in terms)]
result={
 'verification':'PASS',
 'artifact':{'ota_sha256':sha(ota),'image_sha256':sha(image),'image_base':'0x00438000','image_size':len(image)},
 'authenticated_functions':functions,
 'upstream':{'repository':'FreeRTOS/FreeRTOS-Kernel','commit':commit,'version':'V10.5.1','license':'MIT','files':sources,'source_line_anchors':source_lines,'byte_match_claim':False},
 'queue_layout_arm32':{
  'pcHead':{'offset':'0x00','source':'QueueDefinition first member; binary producer uses it as queue base pointer'},
  'pcWriteTo':{'offset':'0x04','source':'QueueDefinition second member; copy helper loads/stores through queue+4'},
  'union_queue_pcTail':{'offset':'0x08','source':'QueuePointers_t union member'},
  'union_queue_pcReadFrom':{'offset':'0x0c','source':'QueuePointers_t second member'},
  'xTasksWaitingToSend':{'offset':'0x10','size':'0x14 bytes','source':'20-byte ARM32 List_t from upstream type; queue body does not use this member on the send-from-ISR success path'},
  'xTasksWaitingToReceive':{'offset':'0x24','size':'0x14 bytes','source':'20-byte ARM32 List_t; send body passes queue+0x24 to event-list helpers'},
  'uxMessagesWaiting':{'offset':'0x38','source':'direct binary access and QueueDefinition'},
  'uxLength':{'offset':'0x3c','source':'direct binary access and QueueDefinition'},
  'uxItemSize':{'offset':'0x40','source':'direct binary access and QueueDefinition'},
  'cRxLock':{'offset':'0x44','source':'QueueDefinition; not used by this producer body'},
  'cTxLock':{'offset':'0x45','source':'signed-byte direct binary access and QueueDefinition'},
  'qualifier':'Offsets are the observed 32-bit target layout; optional trailing QueueDefinition members depend on build config and are not claimed here.'},
 'send_path':{
  'inputs':'ARM EABI xQueue, message pointer, higherPriorityTaskWoken pointer, copy position; caller 0x47eb4a passes copy position 0 (send-to-back).',
  'space_check':'With BASEPRI masking active, tests uxMessagesWaiting < uxLength; a full queue returns 0 (errQUEUE_FULL) without copying. This observed caller uses ordinary send-to-back, not overwrite.',
  'copy':'On available capacity calls 0x441ed8 once. For nonzero item size and copy-to-back, helper copies uxItemSize bytes from input into *pcWriteTo via 0x439be4 (memcpy behavior), advances pcWriteTo by item size, wraps at pcTail, increments uxMessagesWaiting.',
  'waiter_wake':'When cTxLock is -1 (unlocked), checks xTasksWaitingToReceive at queue+0x24; if nonempty calls 0x455370 (task event-list removal/ready transition). If helper reports a higher-priority task, writes pdTRUE to the optional caller flag. It does not yield directly.',
  'locked_case':'When cTxLock is not -1, does not edit receive waiters immediately; increments/saturates the queue TX-lock bookkeeping for a later queue-unlock path. Exact configured lock range is bounded by task count and signed byte representation in source.',
  'returns':'Returns pdPASS (1) after accepted copy; errQUEUE_FULL (0) when no space. Restores saved interrupt mask through 0x5fa0ba on these ordinary returns.',
  'invalid_argument_limit':'The binary has assert-failure tails that intentionally fault-loop; they are not tested or treated as normal success/error paths.'},
 'interrupt_mask_helpers':{
  'set':'0x5fa0a4 body executes MRS BASEPRI, sets BASEPRI threshold 0x30, writes it, DSB, ISB, returns prior value.',
  'restore':'0x5fa0ba restores passed saved BASEPRI value then DSB, ISB.',
  'limits':'The helper bodies are authenticated; global interrupt policy/config meaning beyond the instructions is not inferred.'},
 'producer_binding':{
  'timer_command':'0x47eb4a creates a 16-byte timer callback command and calls 0x441952; PC-relative literal at 0x47eb6c contains 0x20074ab0, the timer-queue handle cell used by the caller.',
  'message':'The producer builds command id 0xfffffffe, callback pointer 0x47ee1f, event-group pointer and bitmask (per preceding authenticated event-group packet).',
  'source':'Pinned timers.c xTimerPendFunctionCallFromISR constructs the daemon callback command and sends it to xTimerQueue with xQueueSendFromISR; pinned event_groups.c describes the callback binding.',
  'boundary':'The producer passes the original higher-priority-task-woken pointer and send-to-back position. This static packet does not establish that queue creation succeeded, that this queue is full/empty at runtime, or that the timer daemon later runs.'},
 'limits':['Static instruction/source evidence only: no execution, scheduler, ISR, or hardware test.','queue.c is byte-pinned upstream source, but the unavailable exact firmware compiler/config build means semantic correspondence is not a compiler-byte match.','Queue fields used by this function are authenticated; trailing optional queue fields and exact build-time configuration are outside scope.','The receiver waiter helper is decoded at its binary boundary; complete scheduler behavior is not reconstructed here.']}
# Write new files only; refuse overwrite to preserve any concurrent work.
for name,content in (('results.json',json.dumps(result,indent=2)+'\n'),('disassembly.txt','\n'.join(listing)+'\n')):
    path=OUT/name
    if path.exists():
        assert path.read_text()==content, f'{path} differs; inspect before updating'
    else:
        path.write_text(content)
print('PASS: authenticated',len(TARGETS),'bodies; pinned',len(sources),'source files')

#!/usr/bin/env python3
"""Authenticate FreeRTOS ready-transition helpers and bounded caller evidence."""
from pathlib import Path
import hashlib, json, struct
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
if not __debug__: raise SystemExit('assertions required')
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent; BASE=0x438000
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
GH=ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29'
UP=ROOT/'g2/build/foundation/freertos-upstream'
TARGETS={
 0x455370:(246,'1a5d4850f0799e97548f23ee1617fc1de362f8d2a674301baa6facd579d13de4','xTaskRemoveFromEventList candidate'),
 0x455876:(38,'a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598','prvResetNextTaskUnblockTime candidate'),
 0x441b0a:(314,'f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560','normal-context queue receive body/caller'),
 0x441c44:(354,'4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c','normal-context queue send body/caller'),
 0x441952:(240,'09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08','ISR queue send body/caller'),
 0x441da6:(192,'cd084580c8e0eededc50eef8fa544290e2c09df64d3ec1e1bf1bbe13bdeb25c4','ISR queue receive body/caller'),
}
def sha(b):return hashlib.sha256(b).hexdigest()
ota=OTA.read_bytes(); image=ota[32:]
assert sha(ota)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert sha(image)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701' and len(image)==3523364
run=json.loads((GH/'RUN.json').read_text());assert run['base']=='0x00438000' and run['image_sha256']==sha(image)
rows=[json.loads(s) for s in (GH/'functions-000.jsonl').read_text().splitlines() if s.strip()];by={int(r['entry'],16):r for r in rows}
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
functions={};listing=[]
for addr,(size,want,name) in TARGETS.items():
 row=by[addr]; end=int(row['body_end_inclusive'],16)+1; body=image[addr-BASE:end-BASE]
 assert row['body_bytes']==size and row['body_sha256']==want and sha(body)==want,(hex(addr),sha(body))
 listing.append(f'## {name} @ 0x{addr:08x} ({size} bytes, sha256 {want})')
 ins=list(md.disasm(body,addr)); assert sum(i.size for i in ins)==len(body)
 inst=[]; calls=[]
 for i in ins:
  x={'pc':f'0x{i.address:08x}','bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str};inst.append(x)
  listing.append(f"0x{i.address:08x}: {i.bytes.hex():<8} {i.mnemonic:<9} {i.op_str}")
  if i.mnemonic in ('bl','blx'):
   try:calls.append({'pc':x['pc'],'target':f'0x{int(i.op_str.split()[0].lstrip('#'),0):08x}'})
   except ValueError:pass
 functions[f'0x{addr:08x}']={'name':name,'size':size,'sha256':want,'ghidra_callees':row.get('callees',[]),'calls':calls,'instructions':inst}
# Must-have call sites: two ordinary task queue operations and both FromISR paths.
expected={0x441b0a:0x455370,0x441c44:0x455370,0x441952:0x455370,0x441da6:0x455370}
for caller,target in expected.items(): assert any(int(x['target'],16)==target for x in functions[f'0x{caller:08x}']['calls']),(hex(caller),hex(target))
# Call site PCs and resolved literal-address/value pairs are part of the evidence.
callpcs={a:[x['pc'] for x in functions[f'0x{a:08x}']['calls'] if int(x['target'],16)==0x455370] for a in expected}
assert callpcs=={0x441b0a:['0x00441c10'],0x441c44:['0x00441d56'],0x441952:['0x004419f4'],0x441da6:['0x00441e18']},callpcs
def has_call(caller,pc,target):
    return any(x['pc']==pc and int(x['target'],16)==target for x in functions[f'0x{caller:08x}']['calls'])
assert has_call(0x455370,'0x00455420',0x455876)
assert has_call(0x441b0a,'0x00441b7a',0x4420d0) and has_call(0x441b0a,'0x00441bc2',0x4420e8)
assert has_call(0x441c44,'0x00441ca6',0x4420d0) and has_call(0x441c44,'0x00441cee',0x4420e8)
assert has_call(0x441952,'0x004419ba',0x5fa0a4) and has_call(0x441952,'0x00441a38',0x5fa0ba)
assert has_call(0x441da6,'0x00441de6',0x5fa0a4) and has_call(0x441da6,'0x00441e5c',0x5fa0ba)
def pc_lit(pc,imm):return ((pc+4)&~3)+imm
literals={
 'scheduler_suspended':(0x4553ae,0xb8,0x20074a58),
 'top_ready_priority':(0x4553da,0x864,0x20074a38),
 'ready_list_array_base':(0x4553ea,0x9d0,0x2006a49c),
 'pending_ready_list':(0x455426,0x380,0x20073d24),
 'current_tcb_cell':(0x455448,0x7e8,0x20074a20),
 'yield_pending_cell':(0x45545a,0x7e8,0x20074a44),
 'current_delayed_list_pointer_cell':(0x455876,0x7d8,0x20074a24),
 'next_unblock_time_cell_empty_and_head':(0x455886,0x7d8,0x20074a50),
}
resolved={}
for name,(pc,imm,value) in literals.items():
 addr=pc_lit(pc,imm); word=struct.unpack_from('<I',image,addr-BASE)[0]
 assert word==value,(name,hex(addr),hex(word),hex(value));resolved[name]={'ldr_pc':f'0x{pc:08x}','literal_address':f'0x{addr:08x}','literal_value':f'0x{word:08x}'}
# Reset helper has a second PC-relative load resolving to same next-unblock cell literal.
addr=pc_lit(0x455894,0x7c8);word=struct.unpack_from('<I',image,addr-BASE)[0];assert word==0x20074a50
resolved['next_unblock_time_cell_nonempty']={'ldr_pc':'0x00455894','literal_address':f'0x{addr:08x}','literal_value':f'0x{word:08x}'}
# Explicit TCB-field use and scheduler-suspended split in the helper.
helper=functions['0x00455370']['instructions']
for pc,op in [('0x00455398','r2, r4, #0x18'),('0x004553c6','r2, r4, #4'),('0x004553e0','r2, [r4, #0x2c]'),('0x00455426','r1, [pc, #0x380]')]:
 assert any(x['pc']==pc and x['operands']==op for x in helper),(pc,op)
# Pin tasks.c/list.c sources to upstream tree and retain source line references.
tree=json.loads((UP/'tree.json').read_text());commit=tree['sha']
def treerow(name):return next(x for x in tree['tree'] if x['path']==name)
sources={};anchors={}
terms={
 'tasks.c':('xTaskRemoveFromEventList( const List_t','THIS FUNCTION MUST BE CALLED FROM A CRITICAL SECTION','if( uxSchedulerSuspended ==','listREMOVE_ITEM( &( pxUnblockedTCB->xEventListItem ) )','listREMOVE_ITEM( &( pxUnblockedTCB->xStateListItem ) )','listINSERT_END( &( xPendingReadyList )','xYieldPending = pdTRUE','static void prvResetNextTaskUnblockTime','xNextTaskUnblockTime = portMAX_DELAY','xNextTaskUnblockTime = listGET_ITEM_VALUE_OF_HEAD_ENTRY'),
 'list.c':('void vListInsertEnd','UBaseType_t uxListRemove','pxNewListItem->pxContainer = pxList')}
for name,needles in terms.items():
 b=(UP/name).read_bytes();r=treerow(name);blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 assert blob==r['sha'],(name,blob,r['sha'])
 txt=b.decode();assert 'FreeRTOS Kernel V10.5.1' in txt and 'SPDX-License-Identifier: MIT' in txt
 sources[name]={'path':str((UP/name).relative_to(ROOT)),'size':len(b),'sha256':sha(b),'git_blob_sha1':blob,'pinned_blob_sha1':r['sha']}
 lines=txt.splitlines();anchors[name]=[{'line':n,'text':line.strip()} for n,line in enumerate(lines,1) if any(q in line for q in needles)]
# Source-level semantic anchors.
tasks=(UP/'tasks.c').read_text();listc=(UP/'list.c').read_text()
for needle in ('BaseType_t xTaskRemoveFromEventList( const List_t * const pxEventList )','listREMOVE_ITEM( &( pxUnblockedTCB->xEventListItem ) )','listREMOVE_ITEM( &( pxUnblockedTCB->xStateListItem ) )','listINSERT_END( &( xPendingReadyList ), &( pxUnblockedTCB->xEventListItem ) )','xYieldPending = pdTRUE','static void prvResetNextTaskUnblockTime( void )'):
 assert needle in tasks,needle
for needle in ('void vListInsertEnd( List_t * const pxList','UBaseType_t uxListRemove( ListItem_t * const pxItemToRemove )'):
 assert needle in listc,needle
result={
 'verification':'PASS','artifact':{'ota_sha256':sha(ota),'image_sha256':sha(image),'base':'0x00438000','size':len(image)},
 'functions':functions,'resolved_literals':resolved,
 'caller_evidence':{
  'normal_task':'0x441b0a calls 0x455370 at 0x441c10 while receiving; 0x441c44 calls it at 0x441d56 while sending. Both are task-context queue bodies with critical-section calls; their hashes/call bytes are retained.',
  'isr':'0x441952 calls 0x455370 at 0x4419f4 in the queue send-from-ISR path; 0x441da6 calls it at 0x441e18 in the receive-from-ISR path. The callers’ higher-priority-task-woken pointer checks/stores are visible around those calls.',
  'call_census':'These caller rows and direct call sites are checked from the original image and Ghidra function table; public API naming follows the pinned queue source semantics.'},
 'ready_transition':{
  'event_owner':'The first event-list item owner is taken as TCB. Its event list item at TCB+0x18 (24) is removed first.',
  'not_suspended':'If scheduler-suspended word 0x20074a58 is zero, removes state-list item at TCB+0x04 and inserts that task into priority-indexed ready lists at base 0x2006a49c; priority is TCB+0x2c (44). Top-ready-priority cell is 0x20074a38. In this build the path also calls reset helper 0x455876.',
  'suspended':'If scheduler-suspended word is nonzero, branches at 0x4553b4 to the deferred path at 0x455426; inserts only the task event-list item (TCB+0x18) into pending-ready list 0x20073d24. It does not remove the task state item/add it to a ready list on this branch; later scheduler-resume processing owns that transition.',
  'yield':'Compares unblocked priority (TCB+0x2c) with current TCB priority loaded through cell 0x20074a20. If strictly higher, returns 1 and writes 1 to yield-pending cell 0x20074a44; otherwise returns 0. ISR callers then use their pxHigherPriorityTaskWoken output path; no context-switch execution is inferred.',
  'tcb_offsets':{'state_list_item':'0x04','event_list_item':'0x18','priority':'0x2c (44 decimal)'},
  'reset_next_unblock':{'helper':'0x455876; 38 bytes; source-corresponds to prvResetNextTaskUnblockTime','pxDelayedTaskList_pointer_cell':'0x20074a24','xNextTaskUnblockTime_cell':'0x20074a50','empty':'stores 0xffffffff (portMAX_DELAY)','nonempty':'reads first delayed-list item value and stores it to xNextTaskUnblockTime','literal_addresses':{'pxDelayedTaskList':'0x456050','next_unblock_empty':'0x456060','next_unblock_head':'0x456060'}}},
 'upstream':{'repository':'FreeRTOS/FreeRTOS-Kernel','commit':commit,'version':'V10.5.1','license':'MIT','files':sources,'source_anchors':anchors,'byte_match_claim':False},
 'limits':['Static original-byte decoding and pinned-source semantic comparison only; no scheduler/ISR runtime execution.','Exact firmware configuration headers are not in this source subset. Address-to-global names are bounded by original literal references and consistent source field use; no full private ABI reconstruction is asserted.','The pending-ready branch’s later drain is attributed to scheduler-resume ownership from pinned source, not simulated here.','No source compilation, firmware linking, queue injection, or task switch is claimed.']}
for f,c in [('results.json',json.dumps(result,indent=2)+'\n'),('disassembly.txt','\n'.join(listing)+'\n')]:
 p=OUT/f
 if p.exists():assert p.read_text()==c,f'{p} differs; inspect before updating'
 else:p.write_text(c)
print('PASS: authenticated',len(TARGETS),'function bodies; resolved',len(resolved),'global literals; pinned tasks/list sources')

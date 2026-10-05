#!/usr/bin/env python3
"""Authenticate bounded timer-daemon receive/callback path and kernel source."""
from pathlib import Path
import hashlib, json, struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
if not __debug__:
    raise SystemExit('assertions required')
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
BASE=0x438000
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
GH=ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29'
UP=ROOT/'g2/build/foundation/freertos-upstream'
TARGETS={
 0x441b0a:(314,'f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560','queue generic receive body'),
 0x4420d0:(24,'5809638c22f928d2b32cd21cc9b92a292fad24cd8b8008de4ad92b9faeaba0d4','critical-entry helper'),
 0x4420e8:(44,'bfd3ddb76c61ad634a3f58ed203260da3834895b646c9dffada546f9dc9d2a31','critical-exit helper'),
 0x5fa0a4:(22,'f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323','BASEPRI mask helper'),
 0x5fa0ba:(14,'97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a','BASEPRI restore helper'),
 0x454d7c:(12,'3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2','scheduler suspend helper'),
 0x454dcc:(306,'548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09','scheduler resume helper'),
}
RAW={
 'timer_task_loop_entry':(0x47e878,0x47e88b,'9a7fd60775e97786baeb1ea1871423c63c5d744b5b8e1ce0c8176e8bb80d377a'),
 'timer_task_block_helper':(0x47e88c,0x47e8f1,'','scheduler-wait wrapper interval; no Ghidra function row'),
 'daemon_receive_dispatch_prefix':(0x47e97a,0x47e9b7,'f6384185b419e8db5a51eaef08dce3ec905b81ab65079f0da6c924d66899e1cf'),
 'daemon_empty_queue_epilogue':(0x47ea8c,0x47ea8f,'54611bb01349f8870260222edbe76075952031373c167412f2cc2ef71f66b84a'),
}
def sha(b):return hashlib.sha256(b).hexdigest()
ota=OTA.read_bytes(); image=ota[32:]
assert sha(ota)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert sha(image)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701' and len(image)==3523364
run=json.loads((GH/'RUN.json').read_text());assert run['base']=='0x00438000' and run['image_sha256']==sha(image)
rows=[json.loads(s) for s in (GH/'functions-000.jsonl').read_text().splitlines() if s.strip()]
by={int(r['entry'],16):r for r in rows}
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
functions={}; listing=[]
def decode(addr,body):
    result=[]
    for i in md.disasm(body,addr):
        it={'pc':f'0x{i.address:08x}','bytes':i.bytes.hex(),'mnemonic':i.mnemonic,'operands':i.op_str}
        result.append(it)
        listing.append(f"0x{i.address:08x}: {i.bytes.hex():<8} {i.mnemonic:<9} {i.op_str}")
    assert sum(2 if len(bytes.fromhex(x['bytes']))==2 else 4 for x in result)==len(body)
    return result
for addr,(size,expected,name) in TARGETS.items():
    row=by[addr];span=int(row['body_end_inclusive'],16)+1
    body=image[addr-BASE:span-BASE]
    assert row['body_bytes']==size and len(body)>=size and row['body_sha256']==expected and sha(body)==expected,(hex(addr),sha(body))
    listing.append(f'## {name} @ 0x{addr:08x} body_bytes={size} span_bytes={len(body)} sha256={expected}')
    ins=decode(addr,body)
    calls=[]
    for i in ins:
        if i['mnemonic'] in ('bl','blx'):
            try:calls.append(int(i['operands'].split()[0].lstrip('#'),0))
            except ValueError:pass
    functions[f'0x{addr:08x}']={'name':name,'body_bytes':size,'span_bytes':len(body),'sha256':expected,'ghidra_callees':row.get('callees',[]),'direct_bl_targets':[f'0x{x:08x}' for x in calls],'instructions':ins}
raws={}
for name,(lo,hi,want,*note) in RAW.items():
    body=image[lo-BASE:hi+1-BASE]
    assert len(body)==hi-lo+1
    got=sha(body)
    if want:assert got==want,(name,got,want)
    listing.append(f"## raw {name} @ 0x{lo:08x}..0x{hi:08x} size={len(body)} sha256={got} {note[0] if note else ''}")
    ins=decode(lo,body)
    raws[name]={'start':f'0x{lo:08x}','end_inclusive':f'0x{hi:08x}','size':len(body),'sha256':got,'note':note[0] if note else '', 'instructions':ins}
# Direct call and literal evidence for receive/deferred callback loop.
entry_ins=raws['timer_task_loop_entry']['instructions']
assert [x['operands'] for x in entry_ins if x['mnemonic']=='bl']==['#0x47e8f2','#0x47e88c','#0x47e97a']
block_ins=raws['timer_task_block_helper']['instructions']
assert any(x['mnemonic']=='bl' and x['operands']=='#0x454d7c' for x in block_ins)
assert any(x['mnemonic']=='bl' and x['operands']=='#0x454dcc' for x in block_ins)
prefix=raws['daemon_receive_dispatch_prefix']['instructions']
assert [(x['pc'],x['operands']) for x in prefix if x['mnemonic']=='bl'][-1:]==[('0x0047e99a','#0x441b0a')]
assert any(x['pc']=='0x0047e992' and x['mnemonic']=='movs' and x['operands']=='r2, #0' for x in prefix)
assert any(x['pc']=='0x0047e994' and x['operands']=='r1, sp' for x in prefix)
assert any(x['pc']=='0x0047e9b0' and x['mnemonic']=='blx' and x['operands']=='r2' for x in prefix)
assert any(x['pc']=='0x0047e9b6' and x['operands']=='#0x47e992' for x in prefix)
assert struct.unpack_from('<I',image,0x47eb6c-BASE)[0]==0x20074ab0
def pc_lit(address,imm): return ((address+4)&~3)+imm
assert pc_lit(0x47e996,0x1d4)==0x47eb6c
assert struct.unpack_from('<I',image,0x442210-BASE)[0]==0x2000309c
# Both critical helpers resolve their PC-relative literal load to the same nesting cell.
assert pc_lit(0x4420d6,0x138)==0x442210 and pc_lit(0x4420ea,0x124)==0x442210
# Critical helper sequences and receive callsites.
enter=functions['0x004420d0'];leave=functions['0x004420e8'];receive=functions['0x00441b0a']
assert enter['direct_bl_targets']==['0x005fa0a4']
assert leave['direct_bl_targets']==['0x005fa0a4','0x005fa0ba']
rcalls=receive['direct_bl_targets']
assert rcalls.count('0x004420d0')>=2 and rcalls.count('0x004420e8')>=3
assert 0x454d7c in [int(x,16) for x in raws['timer_task_block_helper']['instructions'] if x['mnemonic']=='bl' for x in [x['operands'].split()[0].lstrip('#')]]
# Pinned source blob identity and semantic anchors.
tree=json.loads((UP/'tree.json').read_text());commit=tree['sha']
def tree_row(name):return next(x for x in tree['tree'] if x['path']==name)
sources={}; anchors={}
for name,terms in {
 'timers.c':('static portTASK_FUNCTION( prvTimerTask','prvProcessReceivedCommands();','static void prvProcessReceivedCommands','while( xQueueReceive( xTimerQueue, &xMessage, tmrNO_DELAY )','xMessage.xMessageID < ( BaseType_t ) 0','pxCallback->pxCallbackFunction( pxCallback->pvParameter1, pxCallback->ulParameter2 )','xQueueReceive( xTimerQueue, &xMessage, tmrNO_DELAY ) != pdFAIL'),
 'queue.c':('BaseType_t xQueueReceive( QueueHandle_t','taskENTER_CRITICAL();','taskEXIT_CRITICAL();','prvCopyDataFromQueue( pxQueue, pvBuffer )'),
}.items():
 b=(UP/name).read_bytes();row=tree_row(name);blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 assert blob==row['sha']
 text=b.decode();assert 'FreeRTOS Kernel V10.5.1' in text and 'SPDX-License-Identifier: MIT' in text
 sources[name]={'path':str((UP/name).relative_to(ROOT)),'size':len(b),'sha256':sha(b),'git_blob_sha1':blob,'pinned_blob_sha1':row['sha']}
 lines=text.splitlines();anchors[name]=[{'line':n,'text':line.strip()} for n,line in enumerate(lines,1) if any(t in line for t in terms)]
# Ensure exact source construct fragments rather than only line existence.
timers=(UP/'timers.c').read_text();queue=(UP/'queue.c').read_text()
for marker in ('xQueueReceive( xTimerQueue, &xMessage, tmrNO_DELAY )','if( xMessage.xMessageID < ( BaseType_t ) 0 )','pxCallback->pxCallbackFunction( pxCallback->pvParameter1, pxCallback->ulParameter2 )'):
 assert marker in timers,marker
for marker in ('BaseType_t xQueueReceive( QueueHandle_t','taskENTER_CRITICAL();','taskEXIT_CRITICAL();'):
 assert marker in queue,marker
result={
 'verification':'PASS',
 'artifact':{'ota_sha256':sha(ota),'image_sha256':sha(image),'base':'0x00438000','size':len(image)},
 'authenticated_functions':functions,
 'raw_intervals':raws,
 'timer_daemon_trace':{
  'in_census':False,
  'task_loop_entry':'0x0047e878',
  'task_loop_body':'0x0047e878..0x0047e88b; calls 0x0047e97a after 0x0047e88c block/wait helper returns; loops to 0x0047e87a.',
  'process_receive_prefix':'0x0047e97a..0x0047e9b7, with empty-queue epilogue 0x0047ea8c..0x0047ea8f. Positive timer-command handling starts at 0x0047e9b8 and is outside scope.',
  'receive_call':{'pc':'0x0047e99a','target':'0x00441b0a','args':'r0=*(*(uint32_t*)0x20074ab0), r1=SP (local DaemonTaskMessage_t), r2=0 (tmrNO_DELAY). PC-relative literal at 0x0047eb6c equals 0x20074ab0.'},
  'negative_callback':{'signed_test_pc':'0x0047e9a4','condition':'bpl skips callback; negative ID enters callback path','callback_pointer':'[SP+4]','parameter1':'[SP+8]','parameter2':'[SP+12]','indirect_call_pc':'0x0047e9b0 (BLX r2)','repeat':'reloads ID; BMI branches to receive loop 0x0047e992'},
  'missing_message':'BEQ from receive at 0x0047e9a0 branches to common epilogue 0x0047ea8c.',
  'positive_boundary':'BPL at 0x0047e9a6 targets 0x0047e9b2 then nonnegative falls through to 0x0047e9b8 timer-command handling. Not analyzed.'},
 'critical_section':{
  'entry_helper':'0x004420d0: calls 0x005fa0a4 (MRS BASEPRI; writes 0x30; DSB/ISB), increments nesting word at 0x2000309c via literal 0x00442210, DSB/ISB, returns.',
  'exit_helper':'0x004420e8: validates nonzero nesting, decrements 0x2000309c, and only at zero calls 0x005fa0ba with r0=0; that helper writes BASEPRI=0 then DSB/ISB.',
  'receive_call_sites':'Authenticated 0x00441b0a calls entry at 0x00441b7a and 0x00441b9e; it calls exit at 0x00441b96, 0x00441bc2, 0x00441c1c, and 0x00441c24 on visible paths.',
  'scheduler_distinction':'Surrounding timer-block helper 0x0047e88c calls scheduler suspend/resume helpers 0x00454d7c/0x00454dcc. These are separate from the BASEPRI/nesting critical-section helpers.'},
 'upstream':{'repository':'FreeRTOS/FreeRTOS-Kernel','commit':commit,'version':'V10.5.1','license':'MIT','files':sources,'source_anchors':anchors,'byte_match_claim':False},
 'limits':['The daemon and its caller are raw authenticated instruction intervals omitted as Ghidra function rows; no symbol/body census identity is asserted for them.','The negative-command branch and empty receive return are documented; positive timer command handling beginning at 0x0047e9b8 is intentionally out of scope.','Critical helper interpretation is instruction-backed; task.c/port configuration and dynamic nesting scenarios are not executed.','No scheduler execution, queue contents, callback execution, or hardware behavior is claimed. Source correspondence is semantic and commit-pinned, not source-to-firmware compiler-byte identity.']}
for filename,content in [('results.json',json.dumps(result,indent=2)+'\n'),('disassembly.txt','\n'.join(listing)+'\n')]:
 path=OUT/filename
 if path.exists(): assert path.read_text()==content,f'{path} differs; inspect before updating'
 else: path.write_text(content)
print('PASS: authenticated',len(TARGETS),'function bodies and',len(RAW),'raw code intervals; pinned source')

#!/usr/bin/env python3
"""Authenticated queued-write routines versus unchanged Nordic C; actual SVC sites."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'nrf_ble_qwr_init':0x783b6,'nrf_ble_qwr_conn_handle_assign':0x783a0,'nrf_ble_qwr_on_ble_evt':0x783da,'r1_sdk_qwr_user_mem_reply':0x95114}
CTX=0x20007e40;EVT=0x20003000;INIT=0x20003200;ERROR=0x100e001

def main():
    out=BASE/'sdk-qwr';receipt=out/'verification.json';receipt.unlink(missing_ok=True);rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'qwr.o';assert sha(obj)==report['selected_object_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    counts={n:0 for n in ENTRIES};svcs={};states={}
    with tempfile.TemporaryDirectory() as d:
        tmp=Path(d);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } '+''.join('.r1.qwr.'+letter+' '+hex(CTX+i*12)+' (NOLOAD) : { *(.r1.qwr.'+letter+') } ' for i,letter in enumerate('abc'))+' /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_ble_qwr_init',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        for name,address in report['context_addresses'].items():assert syms[name]==int(address,16)
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);svcs[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        assert bytes(stock.mem_read(CTX,36))==bytes(candidate.mem_read(CTX,36))==bytes(36)
        def code(uc,address,size,user):
            if address!=ERROR&~1:return
            f=states[id(uc)];f['trace'].append(('error',uc.reg_read(UC_ARM_REG_R0)))
            if f['mutation']:uc.mem_write(CTX+8,b'\0');uc.mem_write(CTX+2,b'\x34\x12')
            uc.reg_write(UC_ARM_REG_R0,0xcafebabe);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);op=bytes(uc.mem_read(pc-2,2));assert op[1]==0xdf and op[0] in (102,176),op
            f=states[id(uc)];index=f['index'];f['index']+=1;status=f['statuses'][index%len(f['statuses'])];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);svcs[id(uc)]+=1
            if op[0]==102:assert r1==0;f['trace'].append(('svc102',r0,r1,status))
            else:
                assert r1%4==0;raw=bytes(uc.mem_read(r1,16));assert raw[0]==2 and raw[1:4]==bytes(3) and raw[6:]==bytes(10);f['trace'].append(('svc176',r0,raw,status))
            uc.reg_write(UC_ARM_REG_R0,status)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,code);uc.hook_add(UC_HOOK_INTR,svc)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def run(uc,name,args,seed,event,statuses,mutation=False):
            uc.mem_write(CTX-4,b'LEFT');uc.mem_write(CTX,seed);uc.mem_write(CTX+36,b'RGHT');uc.mem_write(EVT,event);uc.mem_write(INIT,struct.pack('<I',ERROR));states[id(uc)]=dict(trace=[],statuses=statuses,index=0,mutation=mutation)
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000;assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            assert bytes(uc.mem_read(CTX-4,4))==b'LEFT' and bytes(uc.mem_read(CTX+36,4))==b'RGHT' and bytes(uc.mem_read(EVT,len(event)))==event
            return uc.reg_read(UC_ARM_REG_R0) if name in ('nrf_ble_qwr_init','nrf_ble_qwr_conn_handle_assign') else None,bytes(uc.mem_read(CTX,36)),list(states[id(uc)]['trace'])
        def compare(name,args,seed,event=bytes(64),statuses=(0,),mutation=False):
            a=run(stock,name,args,seed,event,statuses,mutation);b=run(candidate,name,args,seed,event,statuses,mutation);assert a==b,(name,args,seed,event,statuses,mutation,a,b);counts[name]+=1;return a
        def context(initialized=222,handle=1,pending=0):
            raw=bytearray((i*19+7)&255 for i in range(36));raw[0]=initialized;struct.pack_into('<H',raw,2,handle);struct.pack_into('<I',raw,4,ERROR);raw[8]=pending;return bytes(raw)
        def packet(event=0,handle=1,kind=1,auth=2,op=4):
            raw=bytearray((i*31+5)&255 for i in range(64));struct.pack_into('<HHH',raw,0,event,64,handle);raw[8]=kind
            if event==81:raw[6]=auth;raw[14]=op
            return bytes(raw)
        for initialized in range(256):
            for null_context,null_init in itertools.product((False,True),repeat=2):
                a=compare('nrf_ble_qwr_init',(0 if null_context else CTX,0 if null_init else INIT),context(initialized));assert a[0]==(14 if null_context or null_init else 8 if initialized==222 else 0)
            for handle in (0,1,19,20,0xffff,0x10000,0xffffffff):
                a=compare('nrf_ble_qwr_conn_handle_assign',(CTX,handle),context(initialized));assert a[0]==(0 if initialized==222 else 8)
        assert compare('nrf_ble_qwr_conn_handle_assign',(0,0),context())[0]==14
        # Deliberately invalid bool byte 2 exposes compiler-domain divergence.
        invalid_args=('r1_sdk_qwr_user_mem_reply',(CTX,),context(pending=2),bytes(64),(0,))
        invalid_stock=run(stock,*invalid_args);invalid_candidate=run(candidate,*invalid_args);assert invalid_stock!=invalid_candidate
        for handle,pending,statuses,mutation in itertools.product((0,1,19,0xffff),(0,1),((0,),(17,),(1,),(0xffffffff,),(17,0),(17,1)),(False,True)):
            compare('r1_sdk_qwr_user_mem_reply',(CTX,),context(handle=handle,pending=pending),statuses=statuses,mutation=mutation)
        for event,match,pending,statuses in itertools.product(range(128),(False,True),(0,1),((0,),(17,),(8,),(0xffffffff,),(17,0),(17,8))):
            compare('nrf_ble_qwr_on_ble_evt',(EVT,CTX),context(pending=pending),packet(event,1 if match else 2),statuses)
        for op,auth,match,pending,statuses,mutation in itertools.product(range(16),(0,1,2,255),(False,True),(0,1),((0,),(17,),(8,),(0xffffffff,),(17,0),(17,8)),(False,True)):
            a=compare('nrf_ble_qwr_on_ble_evt',(EVT,CTX),context(pending=pending),packet(81,1 if match else 2,auth=auth,op=op),statuses,mutation)
            for row in a[2]:
                if row[0]=='svc176':assert struct.unpack_from('<H',row[2],4)[0]==(0 if op==5 else 384)
        for kind,match,pending in itertools.product(range(256),(False,True),(0,1)):
            compare('nrf_ble_qwr_on_ble_evt',(EVT,CTX),context(pending=pending),packet(1,1 if match else 2,kind=kind),(17,0))
        for initialized in range(256):compare('nrf_ble_qwr_on_ble_evt',(EVT,CTX),context(initialized,pending=1),packet(1),(17,8))
        for args in ((0,CTX),(EVT,0),(0,0)):compare('nrf_ble_qwr_on_ble_evt',args,context())
        # Three native call-site iterations: execute the stock address arithmetic,
        # stop after initialization, preserve unrelated startup calls as outside scope.
        native_calls=[]
        def init_loop(uc,address,size,user):
            if address==0x783b6:native_calls.append((uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),4))));return
        hook=stock.hook_add(UC_HOOK_CODE,init_loop);stock.mem_write(CTX,bytes(36));stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x4df31,0x4df56,count=10000);stock.hook_del(hook)
        assert [r[0] for r in native_calls]==[CTX,CTX+12,CTX+24];callback_words=[struct.unpack('<I',r[1])[0] for r in native_calls];assert len(set(callback_words))==1
    assert svcs[id(stock)]==svcs[id(candidate)]+1
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),selected_object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,svc_calls=svcs[id(candidate)],invalid_bool_byte_2_diverges=True,invalid_bool_scope='Stock treats byte 2 as nonzero; Clang uses low bit. Only canonical bool 0/1 claimed.',context_initial_zero_bytes_compared=36,native_initialization_contexts=[hex(r[0]) for r in native_calls],native_initialization_error_callback=hex(callback_words[0]),scope='Unchanged SDK C: full init sentinels/nulls, handle assignment, pending retry and actual SVC102/176 paths, 128 event IDs, authorization operations/types, full guarded contexts, callbacks and saved registers/stack',limitations=['SVC results and returning error callbacks are controlled fixtures, not SoftDevice or hardware proof.','Handle assignment native span lacks a ledger row and is supplemental only.','Native initialization loop execution begins after earlier startup calls and ends before later services; this does not establish full startup.','Invalid bool byte 2 diverges between stock and Clang; only source-valid bool values 0/1 are claimed. This is an explicit byte-identity and corruption-domain gate.','Source compilation and bounded behavior do not establish instruction identity or full-image linking.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} queued-write comparisons passed; {svcs[id(candidate)]} SVC calls')
if __name__=='__main__':main()

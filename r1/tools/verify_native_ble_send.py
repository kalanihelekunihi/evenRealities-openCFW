#!/usr/bin/env python3
"""Stock serialized BLE sender plus semaphore selection/status/release contracts."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SLOTS=0x200064fc;SEM=0x2000c000;ALT=0x2000c100
ENTRIES={'r1_native_ble_message_send':0x3e7a8,'r1_ble_error_is_benign':0x3e884,'r1_ble_flush_one':0x3e8ae,'r1_ble_flush_bounded':0x3e8b4,'r1_ble_flush_drain':0x3e8dc,'r1_ble_link_semaphore':0x3e8fc,'r1_ble_semaphore_take':0x3e924}
PROVIDERS={'osSemaphoreAcquire':0x7d57c,'osSemaphoreRelease':0x7d698,'osSemaphoreGetCount':0x7d5e8,'r1_adc_error':0x4e5bc,'r1_native_bae8_send':0x526cc}
def main():
    receipt=BASE/'native-ble-send/verification.json';receipt.unlink(missing_ok=True);report_path=BASE/'native-ble-send/report.json';report=json.loads(report_path.read_text());obj=BASE/'native-ble-send/native_ble_send.o';assert sha(obj)==report['units'][0]['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    connection_report=BASE/'connection-handle/report.json';connection=BASE/'connection-handle/connection_handle.o';assert sha(connection)==json.loads(connection_report.read_text())['units'][0]['object_sha256']
    comparisons={name:0 for name in ENTRIES}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.ble.semaphores 0x200064fc (NOLOAD) : { *(.r1.ble.semaphores) } .r1.connection.field8 0x200064ba : { *(.r1.connection.field8) } .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(PROVIDERS)],'--defsym=r1_native_bae8_service=0x20006504',str(obj),str(connection),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3};assert syms['r1_ble_link_semaphores']==SLOTS
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(SLOTS,8))==bytes(candidate.mem_read(SLOTS,8))==bytes(8)
        states={};seams={a:n for n,a in PROVIDERS.items()};seams.update({0x100e000+i*16:n for i,n in enumerate(PROVIDERS)})
        def mutate(uc,f,name):
            if name==f['mutate_at'] and not f['mutated']:uc.mem_write(SLOTS,struct.pack('<2I',ALT,ALT+16));f['mutated']=True
        def hook(uc,address,size,user):
            f=states[id(uc)]
            for label,entry in (('glasses',0x4cb34),('phone',0x4cba4)):
                if address in (entry,syms['r1_'+label+'_connection_handle_get']):f['events'].append((label,));mutate(uc,f,label);return
            if address not in seams:return
            name=seams[address];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
            if name=='osSemaphoreAcquire':
                i=f['acquires'];f['acquires']+=1;value=f['acquire'][i] if i<len(f['acquire']) else 0xfffffffc;event=(name,r[0],r[1],value)
            elif name=='osSemaphoreRelease':event=(name,r[0]);value=0xfffffffc
            elif name=='osSemaphoreGetCount':
                i=f['count_reads'];f['count_reads']+=1;value=f['counts'][min(i,len(f['counts'])-1)];event=(name,r[0],value)
            elif name=='r1_adc_error':event=(name,r[0]);value=0x87654321
            else:
                assert r[0]==0x20006504;flag=struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0];length=struct.unpack('<I',bytes(uc.mem_read(r[2],4)))[0];i=f['sends'];f['sends']+=1;value=f['statuses'][min(i,len(f['statuses'])-1)];event=(name,r[0],r[1],length,r[3],flag,value)
                replacement=(length+0x10001)&0xffffffff
                if f['narrow_length']:uc.mem_write(r[2],struct.pack('<H',replacement&0xffff))
                else:uc.mem_write(r[2],struct.pack('<I',replacement))
            f['events'].append(event);mutate(uc,f,name);uc.reg_write(UC_ARM_REG_R0,value&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def setup(uc,glass=0,phone=1,slots=(SEM,ALT),acquire=(0,0),statuses=(0,0),counts=(0,),mutate_at=None,narrow_length=False):
            uc.mem_write(0x200064ba,struct.pack('<2H',phone,glass));uc.mem_write(SLOTS,struct.pack('<2I',*slots));states[id(uc)]=dict(events=[],acquires=0,count_reads=0,sends=0,acquire=acquire,statuses=statuses,counts=counts,mutate_at=mutate_at,mutated=False,narrow_length=narrow_length)
        def run(uc,name,args):
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(r,v)
            if len(args)>4:uc.mem_write(0x2003f000,struct.pack('<I',args[4]))
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=100000)
            assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
            assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            value=None if name.startswith('r1_ble_flush_') else uc.reg_read(UC_ARM_REG_R0)
            return value,list(states[id(uc)]['events']),bytes(uc.mem_read(SLOTS,8))
        def compare(name,args,**case):
            for uc in (stock,candidate):setup(uc,**case)
            a=run(stock,name,args);b=run(candidate,name,args);assert a==b,(name,args,case,a,b);comparisons[name]+=1;return a
        benign={0,1,5,8,19,0x3002,0x3401};rng=random.Random(0x3e7a8)
        for status in [*range(65536),0x7fffffff,0x80000000,0xffffffff,*[rng.getrandbits(32) for _ in range(4096)]]:
            assert compare('r1_ble_error_is_benign',(status,))[0]==int(status in benign)
        for connection_id,glass,phone,slots in itertools.product((0,1,2,0xffff,0x10000,0xffffffff),(0,1,0xffff),(0,1,0xffff),((SEM,ALT),(0,ALT),(SEM,0))):
            a=compare('r1_ble_link_semaphore',(connection_id,),glass=glass,phone=phone,slots=slots);assert a[0]==(slots[0] if connection_id==glass else slots[1] if connection_id==phone else 0)
        for semaphore,timeout,status in itertools.product((0,SEM,0xffffffff),(0,1,100,1000,0xffffffff),(0,1,0xfffffffc,0xffffffff)):
            assert compare('r1_ble_semaphore_take',(semaphore,timeout),acquire=(status,))[0]==int(bool(semaphore) and status==0)
        for semaphore,count,levels in itertools.product((0,SEM),(0,1,2,4,8,0xffffffff),((4,),(0,4),(0,1,2,3,4),(0xffffffff,))):
            compare('r1_ble_flush_bounded',(semaphore,count),counts=levels)
        for semaphore,count in itertools.product((0,SEM),range(7)):compare('r1_ble_flush_one',(semaphore,),counts=(count,))
        for semaphore,zeros,status,levels in itertools.product((0,SEM),range(9),(1,0xfffffffc,0xffffffff),((4,),(0,1,2,3,4))):compare('r1_ble_flush_drain',(semaphore,),acquire=tuple([0]*zeros+[status]),counts=levels)
        statuses=(0,1,4,5,8,19,0x3002,0x3401,0xffffffff,0x80000000)
        for flag,first,status,count,semaphore in itertools.product((0,1,2,0xffffffff),(0,1,0xfffffffc),statuses,(0,3,4,0xffffffff),(0,SEM)):
            retries=statuses if flag and first==0 and status==19 and semaphore else (0,)
            for retry in retries:
                for second in ((0,0xfffffffc) if len(retries)>1 else (0,)):
                    a=compare('r1_native_ble_message_send',(0,0x20002000,0x87654321,flag,200),slots=(semaphore,ALT),acquire=(first,second),statuses=(status,retry),counts=(count,));events=a[1]
                    sends=[e for e in events if e[0]=='r1_native_bae8_send'];expected_count=0 if flag and (not semaphore or first) else 1
                    if expected_count and flag and status==19 and second==0:expected_count+=1
                    assert len(sends)==expected_count
                    expected=19 if flag and (not semaphore or first) else 19 if flag and status==19 and second else retry if flag and status==19 else status
                    assert a[0]==expected
        for connection_id,length,flag,timeout,narrow in itertools.product((0,1,2,0xffff,0x10000,0xffffffff),(0,1,0xffff,0x10000,0xffffffff),(0,1,0xffffffff),(0,100,0xffffffff),(False,True)):
            compare('r1_native_ble_message_send',(connection_id,0,length,flag,timeout),statuses=(19,4),narrow_length=narrow)
        for where,flag,status in itertools.product(('glasses','phone',*PROVIDERS),(0,1),(0,4,19)):
            compare('r1_native_ble_message_send',(0,0x20002000,4,flag,100),statuses=(status,4),mutate_at=where)
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),object_sha256=sha(obj),connection_report_sha256=sha(connection_report),comparisons=sum(comparisons.values()),comparisons_by_entry=comparisons,initial_semaphore_zero_bytes_compared=8,unresolved_data_anchors={'r1_native_bae8_service':'0x20006504'},scope='Actual C connection getters; selector precedence, full-word identifiers, benign classifier, bounded releases/drain, semaphore try, zero-flag acquire bypass, status-19 sole retry/1000 timeout, mutable 16/32-bit length update, ignored release/error results and saved registers/stack',limitations=['CMSIS semaphore calls, returning error logger and BAE8 service-send provider are intercepted.','Service state at 0x20006504 is address-only; extent, initialization and callbacks remain unproven.','Drain loops use finite scripted acquire results; scheduler progress and physical transmission remain unproven.','Original instruction identity, full-image linking and hardware behavior remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(comparisons.values())} serialized BLE sender/helper comparisons passed')
if __name__=='__main__':main()

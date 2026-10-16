#!/usr/bin/env python3
"""Native cached-class primitives with real C memory and controlled port callbacks."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NODE=0x20001000;OUT=0x20002000;PORT_A=0x20000800;PORT_B=0x20000880;PORT_SLOT=0x20006974;HEALTH_SLOT=0x20007df4;SPAN=1056
ENTRIES={'r1_kv_class_read':0x73930,'r1_kv_class_write':0x73968,'r1_health_record_read':0x738f4,'r1_health_record_write':0x7390c}
def main():
    real_port='--real-port' in sys.argv;out=BASE/'native-kv-class';rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'native_kv_class.o';receipt=out/('port-integration-verification.json' if real_port else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==report['units'][0]['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';mr=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256'];counts={n:0 for n in ENTRIES};states={};callback_count={}
    port_path=BASE/'native-kv-port/report.json';port=BASE/'native-kv-port/native_kv_port.o'
    if real_port:assert sha(port)==json.loads(port_path.read_text())['units'][0]['object_sha256']
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';ld.write_text('SECTIONS { '+('.r1.kv.port_slot 0x20006974 (NOLOAD) : { *(.r1.kv.port_slot) } .r1.kv.mutex 0x20006978 (NOLOAD) : { *(.r1.kv.mutex) } .r1.kv.port_record 0x20006984 : { *(.r1.kv.port_record) } .r1.kv.block_cursor 0x20019e49 (NOLOAD) : { *(.r1.kv.block_cursor) } ' if real_port else '')+' .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_kv_class_read',*(['--defsym=r1_kv_storage_context=0x2000697c','--defsym=osMutexAcquire=0x100ea01','--defsym=osMutexRelease=0x100ea11','--defsym=r1_kv_port_initialize=0x100ed001','--defsym=r1_kv_store_get=0x100ed011','--defsym=r1_kv_store_put=0x100ed021'] if real_port else ['--defsym=r1_kv_port='+hex(PORT_SLOT)]),'--defsym=r1_health_record_kv_handle='+hex(HEALTH_SLOT),str(obj),str(memory),*([str(port)] if real_port else []),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);callback_count[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());callbacks={0x100e000:'enterA',0x100e010:'leaveA',0x100e020:'enterB',0x100e030:'leaveB'}
        port_bytes=b''
        if real_port:
            p=tmp/'port.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.kv.port_record='+str(p),str(elf)],check=True);port_bytes=p.read_bytes();assert len(port_bytes)==36
            callbacks.update({0x95138:'enterA',0x95150:'leaveA',syms['r1_kv_port_lock']:'enterA',syms['r1_kv_port_unlock']:'leaveA'})
        def hook(uc,address,size,user):
            if real_port and address in (0x7d488,0x7d536,0x100ea00,0x100ea10):
                f=states[id(uc)];name='acquire' if address in (0x7d488,0x100ea00) else 'release';f['os_trace'].append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if name=='acquire' else None));uc.reg_write(UC_ARM_REG_R0,f['callback_result']);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if address not in callbacks:return
            f=states[id(uc)];name=callbacks[address];flags,length=struct.unpack('<HH',bytes(uc.mem_read(NODE+18,4)));f['trace'].append((name,flags,length,bytes(uc.mem_read(NODE+24,16)),bytes(uc.mem_read(OUT,16))));callback_count[id(uc)]+=1
            if name.startswith('enter'):
                if f['mutation'] in (1,5):uc.mem_write(PORT_SLOT,struct.pack('<I',PORT_B))
                if f['mutation']==2:uc.mem_write((0x20006984 if real_port else PORT_A)+32,struct.pack('<I',0x100e031))
                if f['mutation'] in (3,5):uc.mem_write(NODE+18,struct.pack('<HH',0x8040,65535));uc.mem_write(NODE+24,b'\x39'*32);uc.mem_write(OUT,b'\x19'*32)
            elif f['mutation']==4:uc.mem_write(NODE+18,struct.pack('<H',flags|0x4000))
            if real_port and address in (0x95138,0x95150,syms['r1_kv_port_lock'],syms['r1_kv_port_unlock']):return
            uc.reg_write(UC_ARM_REG_R0,f['callback_result']);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        node_seed=bytes((i*37+11)&255 for i in range(SPAN));output_seed=bytes((i*53+7)&255 for i in range(SPAN))
        def run(uc,name,size,stored,flags,mutation,callback_result,data_pointer,port_null):
            node=bytearray(node_seed);struct.pack_into('<HH',node,18,flags,stored);uc.mem_write(NODE-4,b'LEFT');uc.mem_write(NODE,bytes(node));uc.mem_write(NODE+SPAN,b'RGHT');uc.mem_write(OUT-4,b'LEFT');uc.mem_write(OUT,output_seed);uc.mem_write(OUT+SPAN,b'RGHT');uc.mem_write(PORT_SLOT,struct.pack('<I',0 if port_null else PORT_A));uc.mem_write(HEALTH_SLOT,struct.pack('<I',NODE))
            for p,enter,leave in ((PORT_A,0x100e001,0x100e011),(PORT_B,0x100e021,0x100e031)):uc.mem_write(p,bytes(28)+struct.pack('<II',enter,leave))
            if real_port:
                native=(0x94e3d,0x94e2d,0x95165,0x94df1,0x95169,0x95305,0x94df5,0x95139,0x95151);uc.mem_write(0x20006984,struct.pack('<9I',*native) if uc is stock else port_bytes);uc.mem_write(PORT_SLOT,struct.pack('<I',0 if port_null else 0x20006984));uc.mem_write(0x20006978,struct.pack('<I',0x20000700))
            states[id(uc)]=dict(os_trace=[],trace=[],mutation=mutation,callback_result=callback_result);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            args=(data_pointer,) if name.startswith('r1_health') else (NODE,data_pointer,size)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            for p in (NODE,OUT):assert bytes(uc.mem_read(p-4,4))==b'LEFT' and bytes(uc.mem_read(p+SPAN,4))==b'RGHT'
            return uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(NODE,SPAN)),bytes(uc.mem_read(OUT,SPAN)),list(states[id(uc)]['trace']),bytes(uc.mem_read(PORT_SLOT,4)),bytes(uc.mem_read(PORT_A,36)),bytes(uc.mem_read(PORT_B,36)),list(states[id(uc)]['os_trace'])
        def compare(name,size=124,stored=124,flags=0,mutation=0,callback_result=0,data_pointer=OUT,port_null=False):
            a=run(stock,name,size,stored,flags,mutation,callback_result,data_pointer,port_null);b=run(candidate,name,size,stored,flags,mutation,callback_result,data_pointer,port_null);assert a==b,(name,size,stored,flags,mutation,callback_result,data_pointer,a,b);counts[name]+=1;return a
        for name in ('r1_kv_class_read','r1_kv_class_write'):
            for size in range(65536):
                a=compare(name,size=size);assert a[0]==(0 if size==124 else 5)
                if size!=124:assert a[1]==node_seed[:18]+struct.pack('<HH',0,124)+node_seed[22:] and a[2]==output_seed and not a[3]
            for size,flags in itertools.product(range(1025),(0,1,0x8040,0xffff)):
                a=compare(name,size=size,stored=size,flags=flags);assert a[0]==0 and [t[0] for t in a[3]]==['enterA','leaveA']
                if name.endswith('read'):assert a[2][:size]==node_seed[24:24+size]
                else:assert a[1][24:24+size]==output_seed[:size] and struct.unpack_from('<H',a[1],18)[0]==flags|1
            for size,mutation,callback_result in itertools.product((0,1,24,124,1024),range(6),(0,8,0xffffffff)):
                a=compare(name,size=size,stored=size,flags=0x4080,mutation=mutation,callback_result=callback_result);assert a[0]==0 and len(a[3])==2;assert a[3][1][0]==('leaveB' if mutation in (1,2,5) else 'leaveA')
            for size,stored,pointer in itertools.product((0x10000,0x1007c,0x8000007c,0xffffffff),(0,124,65535),(0,0xffffffff)):
                a=compare(name,size=size,stored=stored,data_pointer=pointer,port_null=True);assert a[0]==5 and not a[3]
            assert compare(name,size=0,stored=0,data_pointer=0)[0]==0
        for name in ('r1_health_record_read','r1_health_record_write'):
            for stored,flags,mutation,status in itertools.product((0,23,24,25,124,65535),(0,1,65535),range(6),(0,8,0xffffffff)):
                a=compare(name,stored=stored,flags=flags,mutation=mutation,callback_result=status);assert a[0]==(0 if stored==24 else 5)
            for stored in (0,24,65535):a=compare(name,stored=stored,data_pointer=0,port_null=True);assert a[0]==0 and not a[3]
    assert callback_count[id(stock)]==callback_count[id(candidate)]
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),memory_report_sha256=sha(mr),comparisons=sum(counts.values()),comparisons_by_entry=counts,actual_port_callbacks_executed=real_port,port_report_sha256=sha(port_path) if real_port else None,port_callback_calls=callback_count[id(candidate)],scope='Actual C cached-class copy and dirty-bit operations, all uint16 requested lengths against124, matched mapped sizes0..1024, full-word mismatches, no-copy errors, port/record mutation and pointer reload, ignored callback returns, health wrappers and guarded state/registers/stack',limitations=['Port tables, callbacks and class records are controlled fixtures; complete allocation, global port/handle initialization, actual locking, concurrency and flash persistence remain unresolved.','Only mapped nonoverlapping copy ranges and bounded zero-length null-pointer observations are covered; no portable invalid-pointer or overlapping-memcpy guarantee is claimed.','Original compiler/link identity, exact instructions, complete image linking and physical behavior remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} KV class comparisons passed; {callback_count[id(candidate)]} port callback calls')
if __name__=='__main__':main()

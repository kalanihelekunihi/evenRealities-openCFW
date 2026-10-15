#!/usr/bin/env python3
"""R1 GATT observer/helpers: actual typed C, memory/getter/strerror/init providers."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CTX=0x20007e1c;EVT=0x20003000;CALLBACK=0x100e801;MODE=0x200068ec
DESCRIPTORS={'mtu_request_ring':0x7832c,'mtu_request_sdk':0x7836c,'mtu_reply_ring':0x7ced8,'mtu_reply_sdk':0x7cf18,'length_ring':0xc1328,'length_sdk':0xc1378,'octets_ring':0xc1478,'octets_sdk':0x5a774,'time_ring':0xc13c4,'time_sdk':0xc1420}
ENTRIES={'nrf_ble_gatt_on_ble_evt':0x781b4,'r1_gatt_on_mtu_request':0x7ce34,'r1_gatt_data_length_update':0x5a65c}
PROVIDERS={'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8,'nrf_log_frontend_std_2':0x799d6}
def main():
    out=BASE/'native-gatt';rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'native_gatt_observer.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==report['units'][0]['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    providers={'sdk-gatt/report.json':BASE/'sdk-gatt/gatt-init.o','runtime/report.json':BASE/'runtime/memory-runtime.o','watchdog-logging/report.json':BASE/'watchdog-logging/mode-getter-only.o'}
    for p,o in providers.items():r=json.loads((BASE/p).read_text());assert sha(o)==r.get('selected_object_sha256',r.get('relocatable_sha256')) if p!='watchdog-logging/report.json' else sha(o)==r['selected_getter_sha256']
    strerror=BASE/'watchdog-logging/nrf_strerror.o';sr=json.loads((BASE/'watchdog-logging/report.json').read_text());assert sha(strerror)==next(r for r in sr['units'] if r['source'].endswith('/nrf_strerror.c'))['object_sha256']
    states={};svc_count={};counts=dict(length=0,events=0,mtu=0,flags=0,modes=0,mutations=0)
    with tempfile.TemporaryDirectory() as d:
        tmp=Path(d);ld=tmp/'layout.ld';elf=tmp/'test.elf';text=tmp/'text.bin';ld.write_text('SECTIONS { '+''.join('.r1.gatt.log.'+n+' '+hex(a)+' : { *(.r1.gatt.log.'+n+') } ' for n,a in DESCRIPTORS.items())+' .r1.log.mode 0x200068ec : { *(.r1.log.mode) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.gatt.context 0x20007e1c (NOLOAD) : { *(.r1.gatt.context) } /DISCARD/ : { *(.comment) *(.note*) } }')
        bindings={n:0x100e001+i*16 for i,n in enumerate(PROVIDERS)}
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),*[str(o) for o in providers.values()],str(strerror),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);svc_count[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,text.read_bytes());descriptor_bytes=0
        for n,a in DESCRIPTORS.items():
            path=tmp/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.gatt.log.'+n+'='+str(path),str(elf)],check=True);raw=path.read_bytes();assert raw==bytes(stock.mem_read(a,len(raw)));candidate.mem_write(a,raw);descriptor_bytes+=len(raw)
        addresses={v:k for k,v in PROVIDERS.items()};addresses.update({v&~1:k for k,v in bindings.items()})
        def cstr(uc,address):
            raw=bytearray()
            for i in range(512):
                v=uc.mem_read(address+i,1)[0]
                if not v:return raw.decode()
                raw.append(v)
            raise AssertionError('Unterminated string')
        def mutate(uc,f):
            if not f['mutation']:return
            # Observable providers/callbacks may update live link fields.
            offset=6+8*f['handle'];uc.mem_write(CTX+offset,struct.pack('<HHBBBB',119,31,1,0,87,29));f['mutated']=True
        def hook(uc,address,size,user):
            f=states[id(uc)]
            if address in (0x914ec,syms['r1_structured_log_mode_get']):
                mode=f['sequence'][min(f['reads'],len(f['sequence'])-1)];f['reads']+=1;uc.mem_write(MODE,bytes([mode]));f['trace'].append(('mode',mode));return
            if address==CALLBACK&~1:
                assert uc.reg_read(UC_ARM_REG_R0)==CTX;raw=bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8));f['trace'].append(('callback',raw));mutate(uc,f);uc.reg_write(UC_ARM_REG_R0,0xdeadbeef);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            name=addresses.get(address)
            if not name:return
            regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];fmt=cstr(uc,regs[1]);args=[]
            if name=='r1_structured_log_format':
                assert regs[1]==regs[2];argc=(regs[0]>>22)&3;args=([regs[3]]+list(struct.unpack('<2I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)))))[:argc]
            else:args=regs[2:3] if name.endswith('_1') else regs[2:4]
            if fmt.endswith('%s.'):args[-1]=cstr(uc,args[-1])
            f['trace'].append((name,regs[0],fmt,args));mutate(uc,f);uc.reg_write(UC_ARM_REG_R0,0x1234abcd);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);op=bytes(uc.mem_read(pc-2,2));assert op[1]==0xdf and op[0] in (144,165,181),op;f=states[id(uc)];index=f['svcs'];f['svcs']+=1;status=f['statuses'][min(index,len(f['statuses'])-1)];a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1);svc_count[id(uc)]+=1
            if op[0]==144:
                c=uc.reg_read(UC_ARM_REG_R2);raw=bytes(uc.mem_read(b,8));assert bytes(uc.mem_read(c,6))==bytes(6);uc.mem_write(c,struct.pack('<3H',*f['limits']));f['trace'].append(('svc144',a,raw,status,f['limits']))
            else:f['trace'].append(('svc'+str(op[0]),a,b,status))
            uc.reg_write(UC_ARM_REG_R0,status)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_INTR,svc)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def context(handle=1,desired=247,effective=23,pending=0,requested=0,callback=True,length=251,length_effective=27):
            raw=bytearray(36);struct.pack_into('<HHB',raw,0,desired,desired,length)
            for i in range(3):struct.pack_into('<HHBBBB',raw,6+i*8,desired,effective,pending,requested,length,length_effective)
            struct.pack_into('<I',raw,32,CALLBACK if callback else 0);return bytes(raw)
        def packet(event=0,handle=1,remote=247,role=1):
            raw=bytearray(64);struct.pack_into('<HHH',raw,0,event,64,handle);struct.pack_into('<H',raw,6,remote);struct.pack_into('<H',raw,8,remote);struct.pack_into('<H',raw,10,remote);raw[15]=role;return bytes(raw)
        def run(uc,name,seed,event,args,statuses,limits,sequence,mutation):
            uc.mem_write(CTX-4,b'LEFT');uc.mem_write(CTX,seed);uc.mem_write(CTX+36,b'RGHT');uc.mem_write(EVT,event);handle=struct.unpack_from('<H',event,4)[0];states[id(uc)]=dict(trace=[],svcs=0,reads=0,statuses=statuses,limits=limits,sequence=sequence,mutation=mutation,mutated=False,handle=handle if handle<3 else 0)
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            assert bytes(uc.mem_read(CTX-4,4))==b'LEFT' and bytes(uc.mem_read(CTX+36,4))==b'RGHT' and bytes(uc.mem_read(EVT,64))==event
            return uc.reg_read(UC_ARM_REG_R0) if name=='r1_gatt_data_length_update' else None,bytes(uc.mem_read(CTX,36)),list(states[id(uc)]['trace'])
        def compare(kind='events',name='nrf_ble_gatt_on_ble_evt',seed=None,event=None,args=None,statuses=(0,),limits=(0,0,0),sequence=(0,),mutation=False):
            seed=seed if seed is not None else context();event=event if event is not None else packet();args=args if args is not None else ((CTX,EVT) if name=='r1_gatt_on_mtu_request' else (EVT,CTX));a=run(stock,name,seed,event,args,statuses,limits,sequence,mutation);b=run(candidate,name,seed,event,args,statuses,limits,sequence,mutation);assert a==b,(kind,name,seed,event,args,statuses,limits,sequence,mutation,a,b);counts[kind]+=1;return a
        for connection,length,status,limits,mode in itertools.product((0,1,2,0xffff,0x10000,0xffffffff),(0,27,251,0xffff,0x10000,0xffffffff),(0,17,8,0xffffffff),((0,0,0),(1,0,0),(0,2,0),(1,2,3),(65535,65535,65535)),(0,1,2,4,7)):
            a=compare(kind='length',name='r1_gatt_data_length_update',args=(connection,length),statuses=(status,),limits=limits,sequence=(mode,));assert a[0]==status
        for event,handle,status,pending in itertools.product(range(128),(0,1,2,3,20,0xffff),(0,17,8),(0,1)):
            compare(event=packet(event,handle),seed=context(pending=pending),statuses=(status,))
        for name,handle,desired,remote,pending,requested,callback,status in itertools.product(('nrf_ble_gatt_on_ble_evt','r1_gatt_on_mtu_request'),(0,1,2),(0,22,23,24,247,0xffff),(0,22,23,24,247,0xffff),(0,1),(0,1),(False,True),(0,17,8)):
            compare(kind='mtu',name=name,seed=context(desired=desired,pending=pending,requested=requested,callback=callback),event=packet(85,handle,remote),statuses=(status,))
        for event in (0,58,85):
            for flag in range(256):compare(kind='flags',seed=context(pending=flag,requested=flag),event=packet(event),statuses=(17,))
        for event in (16,35,36):
            for desired,remote,effective,role in itertools.product((0,27,251),(0,27,251,65535),(0,27,251),(0,1,2,255)):
                compare(seed=context(length=desired,length_effective=effective),event=packet(event,remote=remote,role=role))
        stages=[dict(name='r1_gatt_data_length_update',args=(1,251),statuses=(8,),limits=(1,2,3)),dict(event=packet(85),statuses=(8,),seed=context()),dict(event=packet(0),statuses=(8,),seed=context(pending=1))]
        for stage in stages:
            for mode in range(256):compare(kind='modes',sequence=(mode,),**stage)
            for sequence in itertools.product(range(8),repeat=3):compare(kind='modes',sequence=sequence,**stage)
            for sequence in ((0,),(1,),(2,),(4,),(7,)):compare(kind='mutations',sequence=sequence,mutation=True,**stage)
        for event,pending,requested in itertools.product((36,58,85),(0,1),(0,1)):
            compare(kind='mutations',event=packet(event),seed=context(pending=pending,requested=requested),statuses=(8,),mutation=True,sequence=(7,))
    assert svc_count[id(stock)]==svc_count[id(candidate)]
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),provider_reports={p:sha(BASE/p) for p in providers},selected_getter_sha256=sha(providers['watchdog-logging/report.json']),strerror_object_sha256=sha(strerror),comparisons=sum(counts.values()),comparisons_by_kind=counts,svc_calls=svc_count[id(candidate)],descriptor_bytes_compared=descriptor_bytes,scope='Actual native GATT C and upstream init/memory/mode/strerror bodies, exact log strings, actual SVC144/165/181, callback payloads, all event IDs below128, handle bounds, MTU clamps, raw byte flags, R1 unconditional data requests, log modes/transitions and callback/log mutations',limitations=['SVC replies, limitation records, callbacks and final log backends are controlled boundaries; no live SoftDevice or hardware behavior is established.','Only mapped contexts/events and bounded mutations are covered; invalid pointer faults, asynchronous races and full startup are separate gates.','Original compiler/link identity, byte identity and whole-image linking remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} native GATT comparisons passed; {svc_count[id(candidate)]} actual SVC paths')
if __name__=='__main__':main()

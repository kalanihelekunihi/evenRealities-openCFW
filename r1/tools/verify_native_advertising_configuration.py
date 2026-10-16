#!/usr/bin/env python3
"""Native product initializer/config/read/callback C versus locked stock."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CTX=0x20007e64;PAYLOAD=0x20007e04;SLOT=0x20007dfc;OUTPUT=0x20002000;LENGTH=0x20002100;MODE=0x200068ec
ENTRIES={'r1_nordic_advertising_configuration':0x48a28,'r1_advertising_params_init':0x489e6,'r1_advertising_configuration_byte_get':0x7ba24,'r1_advertising_product_sn_read':0x7ba78,'r1_advertising_event_plan_build':0x7cbc8,'r1_advertising_status_publish':0x5e1cc}
DESCRIPTORS={'fast_ring':0x7cc5c,'fast_sdk':0x7cc74,'slow_ring':0x7cc88,'slow_sdk':0x7cca0}
PROVIDERS={'r1_kv_class_read':0x73930,'r1_adc_error':0x4e5bc,'r1_status_record_ring_publish':0x5e118,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0}
def main():
    real_port='--real-port' in sys.argv;real_kv='--real-kv' in sys.argv or real_port;out=BASE/'native-advertising-configuration';rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'native_advertising_configuration.o';receipt=out/('port-integration-verification.json' if real_port else 'kv-integration-verification.json' if real_kv else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==report['units'][0]['object_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    providers={'sdk-advertising-init/report.json':BASE/'sdk-advertising-init/advertising.o','runtime/report.json':BASE/'runtime/memory-runtime.o','watchdog-logging/report.json':BASE/'watchdog-logging/mode-getter-only.o'}
    if real_kv:providers['native-kv-class/report.json']=BASE/'native-kv-class/native_kv_class.o'
    if real_port:providers['native-kv-port/report.json']=BASE/'native-kv-port/native_kv_port.o'
    for name,o in providers.items():r=json.loads((BASE/name).read_text());assert sha(o)==(r['selected_getter_sha256'] if name.startswith('watchdog') else r.get('selected_object_sha256',r.get('relocatable_sha256',r['units'][0]['object_sha256'] if 'units' in r else None)))
    states={};svc_count={};os_mutex_calls={};counts={n:0 for n in ENTRIES}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';ld.write_text('SECTIONS { '+('.r1.kv.port_record 0x20006984 : { *(.r1.kv.port_record) } .r1.kv.port_slot 0x20006974 (NOLOAD) : { *(.r1.kv.port_slot) } .r1.kv.mutex 0x20006978 (NOLOAD) : { *(.r1.kv.mutex) } .r1.kv.block_cursor 0x20019e49 (NOLOAD) : { *(.r1.kv.block_cursor) } ' if real_port else '')+''.join('.r1.advertising.log.'+n+' '+hex(a)+' : { *(.r1.advertising.log.'+n+') } ' for n,a in DESCRIPTORS.items())+' .r1.advertising.intervals 0x99114 : { *(.r1.advertising.intervals) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } .r1.advertising.product_payload 0x20007e04 (NOLOAD) : { *(.r1.advertising.product_payload) } .r1.advertising.a 0x20007e64 (NOLOAD) : { *(.r1.advertising.a) } .r1.advertising.b 0x200082b0 (NOLOAD) : { *(.r1.advertising.b) } /DISCARD/ : { *(.comment) *(.note*) } }')
        bindings={n:0x100e001+i*16 for i,n in enumerate(PROVIDERS) if not (real_kv and n=='r1_kv_class_read')};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_nordic_advertising_configuration','--defsym=r1_device_info_kv_handle='+hex(SLOT),*(['--defsym=r1_kv_storage_context=0x2000697c','--defsym=osMutexAcquire=0x100ef01','--defsym=osMutexRelease=0x100ef11','--defsym=r1_kv_port_initialize=0x100ed001','--defsym=r1_kv_store_get=0x100ed011','--defsym=r1_kv_store_put=0x100ed021'] if real_port else []),*(['--defsym=r1_health_record_kv_handle=0x20007df4'] if real_kv else []),*(['--defsym=r1_kv_port=0x20006974'] if real_kv and not real_port else []),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),*[str(o) for o in providers.values()],'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);svc_count[id(uc)]=0;os_mutex_calls[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());descriptor_bytes=0
        for section,address in [('.r1.advertising.intervals',0x99114),*[( '.r1.advertising.log.'+n,a) for n,a in DESCRIPTORS.items()]]:
            p=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);raw=p.read_bytes();assert raw==bytes(stock.mem_read(address,len(raw)));candidate.mem_write(address,raw);descriptor_bytes+=len(raw)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(PAYLOAD,21))==bytes(candidate.mem_read(PAYLOAD,21))==bytes(21)
        port_bytes=b''
        if real_port:
            path=tmp/'port.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.kv.port_record='+str(path),str(elf)],check=True);port_bytes=path.read_bytes();assert len(port_bytes)==36
        addresses={v:k for k,v in PROVIDERS.items()};addresses.update({v&~1:k for k,v in bindings.items()})
        def cstr(uc,address):
            data=bytearray()
            for i in range(256):
                value=uc.mem_read(address+i,1)[0]
                if value==0:return data.decode()
                data.append(value)
            raise AssertionError('Unterminated log')
        if real_kv:addresses[syms['r1_kv_class_read']]='r1_kv_class_read'
        def hook(uc,address,size,user):
            f=states[id(uc)]
            if real_port and address in (0x7d488,0x7d536,0x100ef00,0x100ef10):
                kind='acquire' if address in (0x7d488,0x100ef00) else 'release';f['trace'].append(('kv_mutex',kind,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if kind=='acquire' else None,f['kv_status']));os_mutex_calls[id(uc)]+=1;uc.reg_write(UC_ARM_REG_R0,f['kv_status']);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if real_kv and address in (0x100ec00,0x100ec10):
                f['trace'].append(('kv_port','enter' if address==0x100ec00 else 'leave'));uc.reg_write(UC_ARM_REG_R0,f['kv_status']);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if address in (0x914ec,syms['r1_structured_log_mode_get']):
                mode=f['modes'][min(f['mode_reads'],len(f['modes'])-1)];f['mode_reads']+=1;uc.mem_write(MODE,bytes([mode]));f['trace'].append(('mode',mode));return
            if address in (0x51716,syms['ble_advertising_init']):
                p=uc.reg_read(UC_ARM_REG_R1);raw=bytearray(uc.mem_read(p,172));conn_ptr=struct.unpack_from('<I',raw,92)[0];manuf_ptr=struct.unpack_from('<I',raw,96)[0];assert struct.unpack_from('<I',raw,164)[0]==(0x7cbc9 if uc is stock else syms['r1_advertising_event_plan_build']|1)
                conn=bytes(uc.mem_read(conn_ptr,4));m=bytes(uc.mem_read(manuf_ptr,12));company=struct.unpack_from('<H',m)[0];length=struct.unpack_from('<H',m,4)[0];payload=struct.unpack_from('<I',m,8)[0];assert payload==PAYLOAD
                for at in (92,96,164):struct.pack_into('<I',raw,at,0)
                f['trace'].append(('initializer',bytes(raw),conn,company,length,bytes(uc.mem_read(payload,length))));f['init_entered']=True;return
            name=addresses.get(address)
            if not name:return
            regs=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
            if name=='r1_kv_class_read':
                expected=struct.unpack('<I',bytes(uc.mem_read(SLOT,4)))[0];assert regs[0]==expected and regs[2]==124;index=f['kv_reads'];f['kv_reads']+=1;record=bytearray((i*37+9)&255 for i in range(124));record[112]=f['config'][min(index,len(f['config'])-1)];record[61]=f['sentinel'];record[31:46]=f['serial'];assert len(record)==124
                if real_kv:uc.mem_write(expected+20,struct.pack('<H',124));uc.mem_write(expected+24,bytes(record))
                else:uc.mem_write(regs[1],bytes(record))
                f['trace'].append(('kv',expected,bytes(record),f['kv_status']))
                if f['mutate_handle']:uc.mem_write(SLOT,struct.pack('<I',(expected+4)&0xffffffff))
                if real_kv:return
                result=f['kv_status']
            elif name=='r1_adc_error':
                f['trace'].append(('error',regs[0]));result=0xfedcba98
                if f['mutate_error'] and not f['init_entered']:uc.mem_write(f['address_pointer'],b'\x02UVWXYZ')
            elif name=='r1_status_record_ring_publish':f['trace'].append(('publish',*regs));result=0x1234abcd
            elif name=='r1_structured_log_format':assert regs[1]==regs[2];f['trace'].append(('ring',regs[0],cstr(uc,regs[1])));result=0x1234abcd
            else:f['trace'].append(('sdk',regs[0],cstr(uc,regs[1])));result=0x1234abcd
            uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);op=bytes(uc.mem_read(pc-2,2));assert op[1]==0xdf and op[0] in (109,121,125,114,115),op;f=states[id(uc)];i=f['svc_calls'];f['svc_calls']+=1;svc_count[id(uc)]+=1;status=f['statuses'][min(i,len(f['statuses'])-1)];a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1)
            if op[0]==109:f['address_pointer']=a;uc.mem_write(a,f['address']);f['trace'].append(('address',f['address'],status))
            elif op[0]==121:uc.mem_write(a,b'\x34\x12');f['trace'].append(('appearance',status))
            elif op[0]==125:
                capacity=struct.unpack('<H',bytes(uc.mem_read(b,2)))[0];uc.mem_write(b,struct.pack('<H',len(f['name'])));uc.mem_write(a,f['name'][:capacity]);f['trace'].append(('name',capacity,len(f['name']),status))
            elif op[0]==114:
                c=uc.reg_read(UC_ARM_REG_R2);assert a==CTX+84;f['trace'].append(('configure',uc.mem_read(a,1)[0],bytes(uc.mem_read(b,16)) if b else None,bytes(uc.mem_read(c,24)),status))
                if status==0:uc.mem_write(a,b'\x41')
            else:f['trace'].append(('start',a,b,status))
            uc.reg_write(UC_ARM_REG_R0,status)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_INTR,svc)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def run(uc,name,args,config,sentinel,kv_status,modes,statuses,device_name,initialized,mutate_handle,mutate_error,fill,start_mode):
            if real_port:
                native=(0x94e3d,0x94e2d,0x95165,0x94df1,0x95169,0x95305,0x94df5,0x95139,0x95151);uc.mem_write(0x20006984,struct.pack('<9I',*native) if uc is stock else port_bytes);uc.mem_write(0x20006974,struct.pack('<I',0x20006984));uc.mem_write(0x20006978,struct.pack('<I',0x20000700))
            elif real_kv:uc.mem_write(0x20006974,struct.pack('<I',0x20000800));uc.mem_write(0x20000800,bytes(28)+struct.pack('<II',0x100ec01,0x100ec11))
            uc.mem_write(SLOT,struct.pack('<I',0x20001000));uc.mem_write(PAYLOAD-4,b'LEFT');uc.mem_write(PAYLOAD,bytes([fill])*21);uc.mem_write(PAYLOAD+21,b'RGHT');uc.mem_write(CTX-4,b'LEFT');seed=bytearray([fill])*1076;seed[0]=initialized;uc.mem_write(CTX,bytes(seed));uc.mem_write(CTX+1076,b'RGHT');uc.mem_write(OUTPUT-4,b'LEFT');uc.mem_write(OUTPUT,bytes([fill])*44);uc.mem_write(OUTPUT+44,b'RGHT');uc.mem_write(LENGTH,b'\x89');states[id(uc)]=dict(trace=[],kv_reads=0,config=config,sentinel=sentinel,serial=b'R1-SERIAL-12345',kv_status=kv_status,modes=modes,mode_reads=0,statuses=statuses,svc_calls=0,name=device_name,address=b'\x02ABCDEF',address_pointer=0,init_entered=False,mutate_handle=mutate_handle,mutate_error=mutate_error)
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            try:uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=100000)
            except UcError as error:raise AssertionError((name,'stock' if uc is stock else 'candidate',hex(uc.reg_read(UC_ARM_REG_PC)),states[id(uc)]['trace'][-4:])) from error
            assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            for address,size in ((PAYLOAD,21),(CTX,1076),(OUTPUT,44)):assert bytes(uc.mem_read(address-4,4))==b'LEFT' and bytes(uc.mem_read(address+size,4))==b'RGHT'
            start_result=None
            if start_mode is not None:
                assert name=='r1_nordic_advertising_configuration';uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,CTX);uc.reg_write(UC_ARM_REG_R1,start_mode)
                uc.emu_start((0x51870 if uc is stock else syms['ble_advertising_start'])|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)];start_result=uc.reg_read(UC_ARM_REG_R0);assert start_result==0
            context=bytearray(uc.mem_read(CTX,1076))
            if name=='r1_nordic_advertising_configuration':assert struct.unpack_from('<I',context,52)[0]==(0x7cbc9 if uc is stock else syms['r1_advertising_event_plan_build']|1);struct.pack_into('<I',context,52,0)
            return uc.reg_read(UC_ARM_REG_R0) if name=='r1_advertising_configuration_byte_get' else None,bytes(context),bytes(uc.mem_read(PAYLOAD,21)),bytes(uc.mem_read(OUTPUT,44)),bytes(uc.mem_read(LENGTH,1)),list(states[id(uc)]['trace']),bytes(uc.mem_read(SLOT,4)),start_result
        def compare(name,args=(),config=(0,),sentinel=0,kv_status=0,modes=(0,),statuses=(0,),device_name=b'OpenCFW-R1',initialized=0,mutate_handle=False,mutate_error=False,fill=0xa5,start_mode=None):
            a=run(stock,name,args,config,sentinel,kv_status,modes,statuses,device_name,initialized,mutate_handle,mutate_error,fill,start_mode);b=run(candidate,name,args,config,sentinel,kv_status,modes,statuses,device_name,initialized,mutate_handle,mutate_error,fill,start_mode);assert a==b,(name,args,config,sentinel,kv_status,modes,statuses,device_name,initialized,mutate_handle,mutate_error,a,b);counts[name]+=1;return a
        for first,second in itertools.product(range(256),repeat=2):
            a=compare('r1_advertising_params_init',(OUTPUT,),config=(first,second));assert a[3][4]==1 and a[3][5]==int(second!=85) and struct.unpack_from('<I',a[3],20)[0]==(0 if first==85 else 6000)
        for value,status in itertools.product(range(256),(0,8,0xffffffff)):assert compare('r1_advertising_configuration_byte_get',config=(value,),kv_status=status)[0]==value
        for sentinel,null_len,status in itertools.product(range(256),(False,True),(0,8)):
            a=compare('r1_advertising_product_sn_read',(OUTPUT,0 if null_len else LENGTH),sentinel=sentinel,kv_status=status);assert a[3][:15]==(b'\xff'*15 if sentinel==255 else b'R1-SERIAL-12345')
            if not null_len:assert a[4]==(b'\0' if sentinel==255 else b'\x0f')
        for event in range(256):compare('r1_advertising_event_plan_build',(event,),modes=(7,))
        for event,mode in itertools.product((0,3,4),range(256)):compare('r1_advertising_event_plan_build',(event,),modes=(mode,))
        for event,sequence in itertools.product((3,4),itertools.product(range(8),repeat=3)):compare('r1_advertising_event_plan_build',(event,),modes=sequence)
        for enabled,event in itertools.product((0,1,2,0xffffffff),(0,1,2,255,0xffffffff)):compare('r1_advertising_status_publish',(enabled,event))
        for sentinel,first,second,statuses,name_len,initialized in itertools.product((0,255),(0,85),(0,85),((0,),(8,0),(0,8),(0,0,8),(0,0,0,8),(0xffffffff,0)),(0,1,10,22,31,256),(0,1)):
            compare('r1_nordic_advertising_configuration',config=(0,first,second),sentinel=sentinel,statuses=statuses,device_name=b'X'*name_len,initialized=initialized)
        for sentinel,first,second,mode,log_mode in itertools.product((0,255),(0,85),(0,85),(0,3,4),(0,2,7)):
            compare('r1_nordic_advertising_configuration',config=(0,first,second),sentinel=sentinel,modes=(log_mode,),start_mode=mode)
        for name,args in (('r1_advertising_params_init',(OUTPUT,)),('r1_nordic_advertising_configuration',())):
            for status in (0,8,0xffffffff):compare(name,args,config=(85,0,85),kv_status=status,mutate_handle=True,mutate_error=True,statuses=(8,0))
    assert os_mutex_calls[id(stock)]==os_mutex_calls[id(candidate)]
    assert svc_count[id(stock)]==svc_count[id(candidate)]
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),provider_reports={p:sha(BASE/p) for p in providers},selected_getter_sha256=sha(providers['watchdog-logging/report.json']),comparisons=sum(counts.values()),comparisons_by_entry=counts,actual_port_mutex_adapters_executed=real_port,os_mutex_calls=os_mutex_calls[id(candidate)],actual_cached_kv_read_executed=real_kv,svc_calls=svc_count[id(candidate)],actual_product_config_start_callback_cases=72,descriptor_and_interval_bytes_compared=descriptor_bytes,product_payload_initial_zero_bytes_compared=21,scope='Actual product configuration plus pinned SDK init/encode/tag setter, source memory/getter, two independent configuration reads, bounded persistent SN extraction, exact typed initializer/manufacturer/interval records, native callback logging/status mapping and error continuation',limitations=['Persistent KV read fully fills124 fixture bytes on every call even on error; partial/unfilled reads and uninitialized failure bytes are outside this C contract.','Controller address fixture fully writes7 bytes even on errors; missing/partial controller writes and stale-stack behavior remain unresolved.','Persistent handles, KV contents, controller identity/name/appearance, final log/status publisher and error callbacks remain controlled boundaries.','Ephemeral input pointers and stored callback are normalized by typed content/function identity; original stack/padding/allocation identity, complete startup, exact bytes and physical behavior remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} product advertising comparisons passed; {svc_count[id(candidate)]} actual SVC paths')
if __name__=='__main__':main()

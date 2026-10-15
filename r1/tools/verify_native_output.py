#!/usr/bin/env python3
"""Stock differential for native queue-drain output and two send veneers."""
import hashlib,itertools,json,random,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_READ_UNMAPPED,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CTX=0x20002000;MSG=0x20003000;ALT=0x20004000
ENTRIES={'r1_native_output_worker':0x44f50,'r1_native_ble_send_phone':0x4e650,'r1_native_ble_send_glasses':0x4e65e}
PROVIDERS={'osMessageQueueGet':0x7d310,'vPortFree':0x95d48,'r1_native_ble_message_send':0x3e7a8,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0}
def main():
    real_events='--real-events' in sys.argv;events_provider='--events-provider' in sys.argv or real_events;real_index='--real-index' in sys.argv or events_provider;real_lookup='--real-lookup' in sys.argv or real_index;real_bae8='--real-bae8' in sys.argv or real_lookup;real_sender='--real-sender' in sys.argv or real_bae8
    receipt=BASE/('native-output/events-integration-verification.json' if real_events else 'native-output/events-provider-verification.json' if events_provider else 'native-output/index-integration-verification.json' if real_index else 'native-output/context-integration-verification.json' if real_lookup else 'native-output/bae8-integration-verification.json' if real_bae8 else 'native-output/sender-integration-verification.json' if real_sender else 'native-output/verification.json');receipt.unlink(missing_ok=True)
    report_path=BASE/'native-output/report.json';report=json.loads(report_path.read_text());obj=BASE/'native-output/native_output.o';assert sha(obj)==report['units'][0]['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    connection_report=BASE/'connection-handle/report.json';connection=BASE/'connection-handle/connection_handle.o';assert sha(connection)==json.loads(connection_report.read_text())['units'][0]['object_sha256']
    getter_report=BASE/'watchdog-logging/report.json';getter=BASE/'watchdog-logging/mode-getter-only.o';assert sha(getter)==json.loads(getter_report.read_text())['selected_getter_sha256']
    if real_sender:
        del PROVIDERS['r1_native_ble_message_send'];PROVIDERS.update({'osSemaphoreAcquire':0x7d57c,'osSemaphoreRelease':0x7d698,'osSemaphoreGetCount':0x7d5e8,'r1_adc_error':0x4e5bc,'r1_native_bae8_send':0x526cc})
        sender_report=BASE/'native-ble-send/report.json';sender=BASE/'native-ble-send/native_ble_send.o';assert sha(sender)==json.loads(sender_report.read_text())['units'][0]['object_sha256']
    if real_bae8:
        del PROVIDERS['r1_native_bae8_send'];PROVIDERS.update({'r1_native_bae8_context_get':0x514e0,'nrf_log_frontend_std_2':0x799d6,'nrf_log_frontend_std_3':0x799e6})
        from verify_native_bae8_send import DESCRIPTORS
        bae8_report=BASE/'native-bae8-send/report.json';bae8=BASE/'native-bae8-send/native_bae8_send.o';assert sha(bae8)==json.loads(bae8_report.read_text())['units'][0]['object_sha256']
        runtime_report=BASE/'runtime/report.json';runtime=BASE/'runtime/memory-runtime.o';assert sha(runtime)==json.loads(runtime_report.read_text())['relocatable_sha256']
    if real_lookup:
        del PROVIDERS['r1_native_bae8_context_get'];PROVIDERS['ble_conn_state_conn_idx']=0x51e04
        context_report=BASE/'sdk-link-context/report.json';context=BASE/'sdk-link-context/blcm_link_ctx_get.o';assert sha(context)==json.loads(context_report.read_text())['units'][0]['object_sha256']
    if real_index:
        del PROVIDERS['ble_conn_state_conn_idx'];index_report=BASE/('sdk-connection-events/report.json' if events_provider else 'sdk-connection-index/report.json');index_obj=BASE/('sdk-connection-events/connection-events.o' if events_provider else 'sdk-connection-index/connection-index-only.o');assert sha(index_obj)==json.loads(index_report.read_text())['selected_object_sha256']
    counts={'worker':0,'veneer':0,'mode_transitions':0,'multi_record':0,'mutations':0,'faults':0}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
        bae8_sections=''.join('.r1.bae8.log.'+name+' '+hex(address)+' : { *(.r1.bae8.log.'+name+') } ' for name,address in DESCRIPTORS.items()) if real_bae8 else ''
        ld.write_text('SECTIONS { '+bae8_sections+' .r1.output.ring 0x44fec : { *(.r1.output.ring) } .r1.output.sdk 0x4501c : { *(.r1.output.sdk) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.m_bcs 0x2002bdb0 (NOLOAD) : { *(.bss.m_bcs) } .r1.ble.semaphores 0x200064fc (NOLOAD) : { *(.r1.ble.semaphores) } .r1.connection.field6 0x200064b8 : { *(.r1.connection.field6) } .r1.connection.field8 0x200064ba : { *(.r1.connection.field8) } .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(PROVIDERS)],str(obj),str(connection),str(getter),*(['--defsym=r1_native_bae8_service=0x20006504',str(sender)] if real_sender else []),*([str(bae8),str(runtime)] if real_bae8 else []),*(['--defsym=r1_native_bae8_context_get=blcm_link_ctx_get',str(context)] if real_lookup else []),*([str(index_obj)] if real_index else []),*(['--undefined=r1_sdk_connection_event','--undefined=ble_conn_state_init'] if real_events else []),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        assert syms['r1_connection_field10']==0x200064bc and syms['r1_structured_log_mode']==0x200068ec
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());descriptor_bytes=0
        for section,address in (('.r1.output.ring',0x44fec),('.r1.output.sdk',0x4501c)):
            path=tmp/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(path),str(elf)],check=True);raw=path.read_bytes();assert raw==bytes(stock.mem_read(address,len(raw)));candidate.mem_write(address,raw);descriptor_bytes+=len(raw)
        registry_event_calls={id(uc):0 for uc in (stock,candidate)}
        execution_counts={id(uc):dict(sender_entries=0,bae8_calls=0) for uc in (stock,candidate)}
        if real_bae8:
            for name,address in DESCRIPTORS.items():
                path=tmp/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.bae8.log.'+name+'='+str(path),str(elf)],check=True);raw=path.read_bytes();assert raw==bytes(stock.mem_read(address,len(raw)));candidate.mem_write(address,raw)
        states={};faults={};seams={a:n for n,a in PROVIDERS.items()};seams.update({0x100e000+i*16:n for i,n in enumerate(PROVIDERS)})
        def string(uc,address):
            data=bytearray()
            while True:
                b=uc.mem_read(address+len(data),1)[0]
                if not b:return data.decode()
                data.append(b);assert len(data)<128
        def mutate(uc,f,where):
            if f['mutate_at']==where and not f['mutated']:
                f['mutated']=True
                if f['slot']:uc.mem_write(f['slot'],struct.pack('<I',f['replacement']))
                uc.mem_write(CTX+12,struct.pack('<I',0x22222222))
        def hook(uc,address,size,user):
            f=states[id(uc)]
            if real_lookup and address in (0x514e0,syms['blcm_link_ctx_get']):
                f['events'].append(('context_entry',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));return
            if real_bae8 and address in (0x526cc,syms['r1_native_bae8_send']):execution_counts[id(uc)]['bae8_calls']+=1
            if real_sender and address in (0x3e7a8,syms['r1_native_ble_message_send']):
                r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];timeout=struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0];f['events'].append(('r1_native_ble_message_send',*r,timeout));execution_counts[id(uc)]['sender_entries']+=1;mutate(uc,f,'send');return
            if address in (0x4cb34,syms['r1_glasses_connection_handle_get']):f['events'].append(('connection',struct.unpack('<H',bytes(uc.mem_read(0x200064bc,2)))[0]));mutate(uc,f,'connection');return
            if address in (0x914ec,syms['r1_structured_log_mode_get']):
                i=f['reads'];f['reads']+=1
                if f['sequence']:uc.mem_write(0x200068ec,bytes([f['sequence'][min(i,len(f['sequence'])-1)]]))
                f['events'].append(('mode',uc.mem_read(0x200068ec,1)[0]));mutate(uc,f,'mode');return
            if address not in seams:return
            name=seams[address];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
            if name=='osMessageQueueGet':
                assert r[2:]==[0,0];assert struct.unpack('<I',bytes(uc.mem_read(r[1],4)))[0]==0
                i=f['index'];f['index']+=1;f['slot']=r[1];item=f['queue'][i] if i<len(f['queue']) else (0xfffffffd,0,False)
                status,pointer,write=item
                if write:uc.mem_write(r[1],struct.pack('<I',pointer))
                f['events'].append((name,r[0],status,pointer,write));value=status
            elif name=='r1_native_ble_message_send':
                timeout=struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0];f['events'].append((name,*r,timeout));value=f['send_status'];mutate(uc,f,'send')
            elif name=='ble_conn_state_conn_idx':event=(name,r[0]);value=0
            elif name=='r1_native_bae8_context_get':
                assert bytes(uc.mem_read(r[2],4))==bytes(4);uc.mem_write(r[2],struct.pack('<I',0x2000d000));event=(name,r[0],r[1]);value=0
            elif name=='osSemaphoreAcquire':event=(name,r[0],r[1]);value=0
            elif name=='osSemaphoreRelease':event=(name,r[0]);value=0xfffffffc
            elif name=='osSemaphoreGetCount':event=(name,r[0]);value=0
            elif name=='r1_adc_error':event=(name,r[0]);value=0x76543210
            elif name=='r1_native_bae8_send':
                assert r[0]==0x20006504;flag=struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0];event=(name,r[0],r[1],struct.unpack('<I',bytes(uc.mem_read(r[2],4)))[0],r[3],flag);value=f['send_status'];execution_counts[id(uc)]['bae8_calls']+=1
            elif name=='vPortFree':f['events'].append((name,r[0]));mutate(uc,f,'free')
            elif name=='r1_structured_log_format':
                assert r[1]==r[2];argc=(r[0]>>22)&3;args=[r[3]] if argc else []
                for i in range(max(0,argc-1)):args.append(struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP)+i*4,4)))[0])
                f['events'].append((name,r[0],r[1],string(uc,r[1]),tuple(args)));mutate(uc,f,'ring')
            else:
                assert r[0]==0x1c0001;argc=int(name.rsplit('_',1)[1]);args=list(r[2:2+min(2,argc)])
                if argc==3:args.append(struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0])
                f['events'].append((name,r[0],r[1],string(uc,r[1]),tuple(args)));mutate(uc,f,'sdk')
            uc.reg_write(UC_ARM_REG_R0,value&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        svc_calls={id(uc):0 for uc in (stock,candidate)}
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);assert bytes(uc.mem_read(pc-2,2))==b'\xae\xdf';f=states[id(uc)];connection=uc.reg_read(UC_ARM_REG_R0);pointer=uc.reg_read(UC_ARM_REG_R1);data=bytearray(uc.mem_read(pointer,16));length_pointer=struct.unpack_from('<I',data,8)[0];length=bytes(uc.mem_read(length_pointer,4));data[8:12]=bytes(4);f['events'].append(('svc174',connection,bytes(data),length));svc_calls[id(uc)]+=1;uc.reg_write(UC_ARM_REG_R0,f['send_status'])
        def fault(uc,access,address,size,value,user):faults[id(uc)].append((access,address));return False
        for uc in (stock,candidate):
            if real_bae8:uc.hook_add(UC_HOOK_INTR,svc)
            uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def setup(uc,kind=0,identifier=0x12345678,length=0x89abcdef,handle=0,mode=0,alignment=0,queue=None,sequence=(),mutate_at=None,replacement=ALT,send_status=0):
            if real_sender:uc.mem_write(0x200064ba,struct.pack('<H',1));uc.mem_write(0x200064fc,struct.pack('<2I',0x2000c000,0x2000c100))
            if real_bae8:
                uc.mem_write(0x20006504,bytes(48));uc.mem_write(0x2000650a,struct.pack('<H',0x1111));uc.mem_write(0x2000651a,struct.pack('<H',0x2222));uc.mem_write(0x2000652c,struct.pack('<I',0x2000d100));uc.mem_write(0x2000d000,b'\x01\x01')
            if real_lookup:uc.mem_write(0x2000d100,struct.pack('<IBxH',0x2000d000,20,4))
            if real_index:uc.mem_write(0x2002bdb4,struct.pack('<I',0x000fffff));uc.mem_write(0x2000d000,b'\x01\x01\0\0'*20)
            uc.mem_write(CTX,struct.pack('<4I',0,0,0,0x11111111));uc.mem_write(MSG,bytes(512));uc.mem_write(MSG+alignment,struct.pack('<3I',identifier,kind,length)+b'payload\0');uc.mem_write(ALT,struct.pack('<3I',0x98765432,1,0x1234abcd)+b'alternative\0');uc.mem_write(0x200064bc,struct.pack('<H',handle));uc.mem_write(0x200068ec,bytes([mode]))
            states[id(uc)]={'queue':queue if queue is not None else [(0,MSG+alignment,True)],'index':0,'events':[],'reads':0,'slot':0,'sequence':sequence,'mutate_at':mutate_at,'replacement':replacement,'mutated':False,'send_status':send_status};faults[id(uc)]=[]
            if real_events:
                def invoke(entry,args):
                    uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                    for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(r,v)
                    uc.emu_start(entry|1,0x20000100,count=1000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                invoke(0x51e78 if uc is stock else syms['ble_conn_state_init'],())
                for handle in (0,1):
                    raw=bytearray(64);struct.pack_into('<HHH',raw,0,16,64,handle);raw[15]=2;uc.mem_write(0x20006000,bytes(raw));invoke(0x5380c if uc is stock else syms['r1_sdk_connection_event'],(0x20006000,0));registry_event_calls[id(uc)]+=1
        def run(uc,name,args):
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            try:uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=100000)
            except UcError:assert faults[id(uc)],hex(uc.reg_read(UC_ARM_REG_PC))
            else:
                assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
                assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            return (None if name=='r1_native_output_worker' or faults[id(uc)] else uc.reg_read(UC_ARM_REG_R0),list(states[id(uc)]['events']),list(faults[id(uc)]),bytes(uc.mem_read(CTX,16)),bytes(uc.mem_read(MSG,512)),bytes(uc.mem_read(ALT,64)),bytes(uc.mem_read(0x2002bdb0,124)) if real_events else None)
        def compare(name='r1_native_output_worker',args=(CTX,0,0),**case):
            for uc in (stock,candidate):setup(uc,**case)
            a=run(stock,name,args);b=run(candidate,name,args);assert a==b,(name,args,case,a,b);return a
        words=(0,1,0xffff,0x10000,0x80000000,0xffffffff)
        for kind,identifier,length,handle,alignment in itertools.product((0,1,2,3,0x80000000,0xffffffff),words,words,(0,1,0xfffe,0xffff),range(4)):
            result=compare(kind=kind,identifier=identifier,length=length,handle=handle,alignment=alignment);counts['worker']+=1
            sends=[e for e in result[1] if e[0]=='r1_native_ble_message_send'];assert len(sends)==int(kind==1 or kind in (0,2) and handle!=0xffff)
            if sends:assert sends[0][1:]==(identifier&0xffff,MSG+alignment+12,length&0xffff,1 if kind==1 else 0,200 if kind==1 else 100)
            assert ('vPortFree',MSG+alignment) in result[1]
        for mode,kind in itertools.product(range(256),(0,2)):
            compare(kind=kind,handle=0xffff,mode=mode);counts['worker']+=1
        for sequence in itertools.product(range(8),repeat=3):compare(handle=0xffff,sequence=sequence);counts['mode_transitions']+=1
        for status,pointer,write in itertools.product((0,1,0xfffffffd,0xffffffff),(0,MSG),(False,True)):
            compare(queue=[(status,pointer,write)]);counts['worker']+=1
        for where,replacement,handle,mode in itertools.product(('connection','send','mode','ring','sdk','free'),(ALT,0),(0,0xffff),(0,7)):
            result=compare(handle=handle,mode=mode,mutate_at=where,replacement=replacement,queue=[(0,MSG,True),(0,ALT,True),(0,0,True)]);counts['mutations']+=1
            if result[2]:counts['faults']+=1
        rng=random.Random(0x44f50)
        for _ in range(512):
            queue=[(0,MSG if rng.randrange(2) else ALT,True) for _ in range(rng.randrange(1,9))]+[(rng.choice((0,1,0xfffffffd)),0,True)]
            compare(kind=rng.randrange(5),identifier=rng.getrandbits(32),length=rng.getrandbits(32),handle=rng.choice((0,1,0xffff)),mode=rng.randrange(256),queue=queue,send_status=rng.getrandbits(32));counts['multi_record']+=1
        for name,identifier,length,status in itertools.product(('r1_native_ble_send_phone','r1_native_ble_send_glasses'),words,words,(0,1,0xffffffff,0x80000000)):
            result=compare(name,args=(identifier,MSG,length),send_status=status)
            if real_sender:
                expected=status if name.endswith('glasses') or identifier in (0,1) else 19
                if real_bae8 and (name.endswith('glasses') or identifier in (0,1)):
                    expected=5 if identifier==0xffff or real_index and identifier>=20 else 7 if length&0xffff>244 else status
                assert result[0]==expected,(name,identifier,length,status,result[0],expected)
            else:assert result[0]==status and result[1]==[('r1_native_ble_message_send',identifier,MSG,length,1 if name.endswith('phone') else 0,200 if name.endswith('phone') else 100)]
            counts['veneer']+=1
        for context in (0,0x2003fff8):assert compare(args=(context,0,0))[2];counts['faults']+=1
    total=sum(v for k,v in counts.items() if k!='faults')+2
    if real_events:assert registry_event_calls[id(stock)]==registry_event_calls[id(candidate)] and registry_event_calls[id(candidate)]>0
    if real_bae8:assert svc_calls[id(stock)]==svc_calls[id(candidate)] and svc_calls[id(candidate)]>0
    if real_sender:assert execution_counts[id(stock)]==execution_counts[id(candidate)] and all(execution_counts[id(candidate)].values()),execution_counts
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),object_sha256=sha(obj),provider_reports={'connection-handle/report.json':sha(connection_report),'watchdog-logging/report.json':sha(getter_report),**({'native-ble-send/report.json':sha(sender_report)} if real_sender else {}),**({'native-bae8-send/report.json':sha(bae8_report),'runtime/report.json':sha(runtime_report)} if real_bae8 else {}),**({'sdk-link-context/report.json':sha(context_report)} if real_lookup else {}),**({('sdk-connection-events/report.json' if events_provider else 'sdk-connection-index/report.json'):sha(index_report)} if real_index else {})},actual_sender_executed=real_sender,actual_bae8_executed=real_bae8,actual_link_context_executed=real_lookup,actual_connection_index_executed=real_index,events_provider=events_provider,actual_registry_events_executed=real_events,registry_event_calls=registry_event_calls[id(candidate)] if real_events else None,svc174_calls=svc_calls[id(candidate)] if real_bae8 else None,sender_execution_counts=execution_counts[id(candidate)] if real_sender else None,selected_getter_sha256=sha(getter),comparisons=total,comparisons_by_kind=counts,descriptor_bytes_compared=descriptor_bytes,scope='Stock worker and two veneers; actual C connection/mode getters, pointer queue drain/stop/null records, 16-bit consumed fields, unknown types, invalid handles, all mode bytes, mode transitions, reloaded pointers/queue after provider mutation, ownership/free order and full-word veneer returns',limitations=[('Actual registry init/connect writers and output/serialized/BAE8/lookup chain execute; client notification/storage pools, logger, semaphore, queue/free and SVC responses remain test boundaries; event delivery is direct, not a live BLE stack.' if real_events else 'Actual output/serialized/BAE8 send, SDK lookup/index/validity/flag-read and memory execute; registry bitmap/storage/pool are fixtures; logs, semaphore, queue/free and SVC174 responses remain intercepted.' if real_index else 'Actual output/serialized/BAE8 send, SDK link-context lookup and memory execute; connection index, logs, semaphore, queue/free and SVC174 responses remain intercepted; service/storage configuration is a fixture.' if real_lookup else 'Actual output/serialized/BAE8 send and memory execute; lookup, log, semaphore, queue/free boundaries and SVC174 responses are intercepted; service configuration is a fixture.' if real_bae8 else 'Actual serialized sender and helpers execute; queue/free, semaphore API, BAE8 send, returning error logger and both log backends are intercepted; the service data anchor is address-only.' if real_sender else 'Queue get/free, generic BLE sender and both log backends are intercepted; actual RTOS, allocator, BLE transport and logging-stack composition remain open.'),'Fault addresses are compared without access-width/granularity identity; source byte reads avoid alignment assumptions.','Original instructions, cycle timing, physical-device and whole-image behavior remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{total} output worker/veneer comparisons passed; {counts["faults"]} fault cases')
if __name__=='__main__':main()

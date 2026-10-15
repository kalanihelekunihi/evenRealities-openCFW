#!/usr/bin/env python3
"""Execute R1 BAE8 send against stock, intercepting only lookup/log/SVC boundaries."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_READ_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SERVICE=0x20006504;CLIENT=0x20004000;OTHER=CLIENT+16;LENGTH=0x20003000
DESCRIPTORS={'invalid_ring':0x528c0,'invalid_sdk':0x528f0,'lookup_ring':0xbe944,'lookup_sdk':0xbe9a8,'bc_ring':0xbe7ac,'bc_sdk':0xbe804,'eus_ring':0xbe858,'eus_sdk':0xbe8b0,'length_ring':0x52930,'length_sdk':0x52958,'hvx_ring':0xbe900,'hvx_sdk':0x52980}
PROVIDERS={'r1_native_bae8_context_get':0x514e0,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0,'nrf_log_frontend_std_2':0x799d6,'nrf_log_frontend_std_3':0x799e6}
def main():
    real_events='--real-events' in sys.argv;events_provider='--events-provider' in sys.argv or real_events;real_index='--real-index' in sys.argv or events_provider;real_lookup='--real-lookup' in sys.argv or real_index
    receipt=BASE/('native-bae8-send/events-integration-verification.json' if real_events else 'native-bae8-send/events-provider-verification.json' if events_provider else 'native-bae8-send/index-integration-verification.json' if real_index else 'native-bae8-send/context-integration-verification.json' if real_lookup else 'native-bae8-send/verification.json');receipt.unlink(missing_ok=True);report_path=BASE/'native-bae8-send/report.json';report=json.loads(report_path.read_text());obj=BASE/'native-bae8-send/native_bae8_send.o';assert sha(obj)==report['units'][0]['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    getter_report=BASE/'watchdog-logging/report.json';getter=BASE/'watchdog-logging/mode-getter-only.o';assert sha(getter)==json.loads(getter_report.read_text())['selected_getter_sha256']
    memory_report=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(memory_report.read_text())['relocatable_sha256']
    if real_lookup:
        del PROVIDERS['r1_native_bae8_context_get'];PROVIDERS['ble_conn_state_conn_idx']=0x51e04
        context_report=BASE/'sdk-link-context/report.json';context=BASE/'sdk-link-context/blcm_link_ctx_get.o';assert sha(context)==json.loads(context_report.read_text())['units'][0]['object_sha256']
    if real_index:
        del PROVIDERS['ble_conn_state_conn_idx'];index_report=BASE/('sdk-connection-events/report.json' if events_provider else 'sdk-connection-index/report.json');index_obj=BASE/('sdk-connection-events/connection-events.o' if events_provider else 'sdk-connection-index/connection-index-only.o');assert sha(index_obj)==json.loads(index_report.read_text())['selected_object_sha256']
    if real_events:PROVIDERS['r1_adc_error']=0x4e5bc
    counts=dict(core=0,modes=0,transitions=0,mutations=0,faults=0);svc_calls={}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';sections=''.join('.r1.bae8.log.'+name+' '+hex(address)+' : { *(.r1.bae8.log.'+name+') } ' for name,address in DESCRIPTORS.items())
        ld.write_text('SECTIONS { '+sections+' .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.m_bcs 0x2002bdb0 (NOLOAD) : { *(.bss.m_bcs) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry=r1_native_bae8_send',*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(PROVIDERS)],str(obj),str(getter),str(memory),*(['--defsym=r1_native_bae8_context_get=blcm_link_ctx_get',str(context)] if real_lookup else []),*([str(index_obj)] if real_index else []),*(['--undefined=r1_sdk_connection_event','--undefined=ble_conn_state_init'] if real_events else []),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        assert syms['r1_structured_log_mode']==0x200068ec
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);svc_calls[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());descriptor_bytes=0
        for name,address in DESCRIPTORS.items():
            path=tmp/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.bae8.log.'+name+'='+str(path),str(elf)],check=True);data=path.read_bytes();assert data==bytes(stock.mem_read(address,len(data))),name;candidate.mem_write(address,data);descriptor_bytes+=len(data)
        states={};faults={};seams={a:n for n,a in PROVIDERS.items()};seams.update({0x100e000+i*16:n for i,n in enumerate(PROVIDERS)})
        def mutate(uc,f,where):
            if f['mutate_at']==where and not f['mutated']:
                f['mutated']=True;uc.mem_write(f['slot'],struct.pack('<I',OTHER));uc.mem_write(SERVICE+6,struct.pack('<H',0x5678));uc.mem_write(SERVICE+22,struct.pack('<H',0x9876))
        def hook(uc,address,size,user):
            f=states[id(uc)]
            if real_lookup and address in (0x514e0,syms['blcm_link_ctx_get']):
                r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)];f['slot']=r[2];f['events'].append(('context_entry',r[0],r[1]));mutate(uc,f,'lookup');return
            if address in (0x914ec,syms['r1_structured_log_mode_get']):
                i=f['reads'];f['reads']+=1
                if f['sequence']:uc.mem_write(0x200068ec,bytes([f['sequence'][min(i,len(f['sequence'])-1)]]))
                f['events'].append(('mode',uc.mem_read(0x200068ec,1)[0]));mutate(uc,f,'mode');return
            if address not in seams:return
            name=seams[address];r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=0
            if name=='r1_adc_error':f['events'].append((name,r[0]));value=0x87654321
            elif name=='ble_conn_state_conn_idx':f['events'].append((name,r[0]));value=0
            elif name=='r1_native_bae8_context_get':
                assert bytes(uc.mem_read(r[2],4))==bytes(4);f['slot']=r[2];f['events'].append((name,r[0],r[1]));uc.mem_write(r[2],struct.pack('<I',f['client']));value=f['lookup'];mutate(uc,f,'lookup')
            else:
                if name=='r1_structured_log_format':
                    assert r[1]==r[2] and r[1] in DESCRIPTORS.values();argc=(r[0]>>22)&3;args=[r[3]] if argc else []
                    for i in range(max(0,argc-1)):args.append(struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP)+4*i,4)))[0])
                    f['events'].append((name,r[0],r[1],tuple(args)));mutate(uc,f,'ring')
                else:
                    assert r[0]==0x001c0001 and r[1] in DESCRIPTORS.values();argc=int(name.rsplit('_',1)[1]);args=list(r[2:2+min(2,argc)])
                    if argc==3:args.append(struct.unpack('<I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4)))[0])
                    f['events'].append((name,r[0],r[1],tuple(args)));mutate(uc,f,'sdk')
                value=0x87654321
            uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);assert bytes(uc.mem_read(pc-2,2))==b'\xae\xdf',(number,hex(pc));f=states[id(uc)];connection=uc.reg_read(UC_ARM_REG_R0);pointer=uc.reg_read(UC_ARM_REG_R1);data=bytes(uc.mem_read(pointer,16));p_len,p_data=struct.unpack_from('<II',data,8)
            expected=struct.pack('<HBxHxxII',0x9876 if f['mutated'] and f['flag'] else 0x5678 if f['mutated'] else 0x2222 if f['flag'] else 0x1111,1,0,f['length_pointer'],f['payload']);assert data==expected,(data,expected)
            f['events'].append(('svc174',connection,data,bytes(uc.mem_read(p_len,4))));svc_calls[id(uc)]+=1;uc.mem_write(p_len,struct.pack('<H',f['returned_length']));uc.reg_write(UC_ARM_REG_R0,f['svc_status']);mutate(uc,f,'svc')
        def fault(uc,access,address,size,value,user):faults[id(uc)].append((access,address));return False
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_INTR,svc);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def run(uc,service=SERVICE,connection=0,lookup=0,client=CLIENT,flags=(1,1),length=4,flag=0,mode=0,svc_status=0,sequence=(),mutate_at=None,length_pointer=LENGTH,payload=0x20002000,valid_flags=0x000fffff,event_phase=0):
            uc.mem_write(SERVICE,bytes(48));uc.mem_write(SERVICE+6,struct.pack('<H',0x1111));uc.mem_write(SERVICE+22,struct.pack('<H',0x2222));uc.mem_write(SERVICE+40,struct.pack('<I',0x12345678));uc.mem_write(CLIENT,bytes(flags));uc.mem_write(OTHER,bytes([2,3]));uc.mem_write(LENGTH,struct.pack('<I',length));uc.mem_write(0x200068ec,bytes([mode]));uc.mem_write(0x2003ee00,bytes([0xa5])*512)
            if real_lookup:uc.mem_write(SERVICE+40,struct.pack('<I',0x20005000));uc.mem_write(0x20005000,struct.pack('<IBxH',client,0 if lookup else 20,4))
            if real_index:uc.mem_write(0x2002bdb4,struct.pack('<I',valid_flags));uc.mem_write(CLIENT,(bytes(flags)+bytes(2))*20);uc.mem_write(OTHER,b'\x02\x03')
            states[id(uc)]=dict(events=[],reads=0,slot=0,client=client,lookup=lookup,flag=flag,svc_status=svc_status,returned_length=0x4321,sequence=sequence,mutate_at=mutate_at,mutated=False,length_pointer=length_pointer,payload=payload);faults[id(uc)]=[]
            if real_events:
                def invoke(entry,args):
                    uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                    for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(r,v)
                    uc.emu_start(entry|1,0x20000100,count=1000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                invoke(0x51e78 if uc is stock else syms['ble_conn_state_init'],())
                handle=connection&0xffff
                def emit(event,which):
                    raw=bytearray(64);struct.pack_into('<HHH',raw,0,event,64,which);raw[15]=2;uc.mem_write(0x20006000,bytes(raw));invoke(0x5380c if uc is stock else syms['r1_sdk_connection_event'],(0x20006000,0))
                emit(16,handle)
                if event_phase and connection<20:emit(17,handle)
                if event_phase==2 and connection<20:emit(16,(handle+1)%20)
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.mem_write(0x2003f000,struct.pack('<I',flag))
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(service,payload,length_pointer,connection)):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            try:uc.emu_start((0x526cc if uc is stock else syms['r1_native_bae8_send'])|1,0x20000100,count=100000)
            except UcError:assert faults[id(uc)],hex(uc.reg_read(UC_ARM_REG_PC))
            else:
                assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
                assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            return None if faults[id(uc)] else uc.reg_read(UC_ARM_REG_R0),list(states[id(uc)]['events']),bytes(uc.mem_read(LENGTH,4)),bytes(uc.mem_read(SERVICE,48)),list(faults[id(uc)]),bytes(uc.mem_read(0x2002bdb0,124)) if real_events else None
        def compare(**case):
            a=run(stock,**case);b=run(candidate,**case);assert a==b,(case,a,b);return a
        for connection,lookup,client,flags,length,flag,status in itertools.product((0,1,0xffff,0x10000,0xffffffff),(0,4),(0,CLIENT),((0,0),(1,0),(0,1),(1,1),(255,128)),(0,244,245,0xffff,0x12340001,0xffff00f4),(0,1,2,0xffffffff),(0,19,4,0xffffffff)):
            a=compare(connection=connection,lookup=lookup,client=client,flags=flags,length=length,flag=flag,svc_status=status);expected=5 if connection==0xffff or lookup or not client or real_index and connection>=20 else 8 if not flags[int(bool(flag))] else 7 if length&0xffff>244 else status;assert a[0]==expected;counts['core']+=1
        stages=[dict(connection=0xffff),dict(lookup=4),dict(flags=(0,1)),dict(flags=(1,0),flag=1),dict(length=245),dict(svc_status=4)]
        for stage in stages:
            for mode in range(256):compare(mode=mode,**stage);counts['modes']+=1
            for sequence in itertools.product(range(8),repeat=3):compare(sequence=sequence,**stage);counts['transitions']+=1
            for where,mode in itertools.product(('lookup','mode','ring','sdk','svc'),(0,1,2,4,7)):
                if stage.get('connection')==0xffff and where=='mode':continue
                # Invalid-connection logs have no lookup output pointer to mutate.
                if stage.get('connection')==0xffff:continue
                compare(mutate_at=where,mode=mode,**stage);counts['mutations']+=1
        for payload,length_pointer in itertools.product((0,0xffffffff,0x20002001),(0,LENGTH)):
            assert compare(service=0,payload=payload,length_pointer=length_pointer)[0]==14;counts['core']+=1
        for case in (dict(length_pointer=0),dict(client=0x20040000),dict(service=0x20040000)):
            assert compare(**case)[4];counts['faults']+=1
        if real_index and not real_events:
            for handle,bits,flag in itertools.product(range(20),(0,1,0x80000,0xfffff,0xffffffff),(0,1)):
                a=compare(connection=handle,valid_flags=bits,flag=flag);assert a[0]==(0 if bits&(1<<handle) else 5);counts['core']+=1
        if real_events:
            for handle,phase,flag in itertools.product(range(20),(0,1,2),(0,1)):
                a=compare(connection=handle,event_phase=phase,flag=flag);assert a[0]==(5 if phase==2 else 0);counts['core']+=1
    assert svc_calls[id(stock)]==svc_calls[id(candidate)] and svc_calls[id(candidate)]>0
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),object_sha256=sha(obj),provider_reports={'watchdog-logging/report.json':sha(getter_report),'runtime/report.json':sha(memory_report),**({'sdk-link-context/report.json':sha(context_report)} if real_lookup else {}),**({('sdk-connection-events/report.json' if events_provider else 'sdk-connection-index/report.json'):sha(index_report)} if real_index else {})},actual_link_context_executed=real_lookup,actual_connection_index_executed=real_index,events_provider=events_provider,actual_registry_events_executed=real_events,selected_getter_sha256=sha(getter),comparisons=sum(counts.values()),comparisons_by_kind=counts,descriptor_bytes_compared=descriptor_bytes,svc174_calls=svc_calls[id(candidate)],scope='Actual C mode getter/memory and SDK-typed 16-byte HVX parameters; all log modes and short-circuit transitions, dual enable flags/handle offsets, low-halfword 244-byte cap, full-word connection/flag registers, lookup result/null, client mutation, SVC return/length update and saved registers/stack',limitations=[('Actual registry init/CONNECTED/DISCONNECTED/reconnect events execute before BAE8/lookup; notification/storage pools remain fixtures, error/log and SVC174 responses remain intercepted; ' if real_events else 'Actual pinned lookup/index/validity/flag-read bodies execute; registry bitmap/storage/pool are fixtures, log backends and SVC174 responses remain intercepted; ' if real_index else 'Actual pinned link-context lookup executes; connection-index and log backends are intercepted; ' if real_lookup else 'Link-context lookup and log backends are intercepted; ')+ ' SVC174 is observed and answered by a deterministic hook, not a SoftDevice execution.','The service prefix is only a read view; complete object extent, initialization and callback configuration remain unproven.','Fault addresses are compared without access-width identity; physical BLE transmission, original instructions and whole-image linking remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} BAE8 comparisons passed; {svc_calls[id(candidate)]} actual SVC174 paths')
if __name__=='__main__':main()

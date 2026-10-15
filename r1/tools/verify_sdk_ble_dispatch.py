#!/usr/bin/env python3
"""Actual SDK BLE SVC poll, multi-range traversal and typed observer configuration."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    real_advertising_init='--real-advertising-init' in sys.argv;real_advertising='--real-advertising' in sys.argv or real_advertising_init;real_gatt='--real-gatt' in sys.argv or real_advertising;real_qwr='--real-qwr' in sys.argv or real_gatt;real_registry='--real-registry' in sys.argv or real_qwr;out=BASE/'sdk-ble-dispatch';receipt=out/('advertising-init-integration-verification.json' if real_advertising_init else 'advertising-integration-verification.json' if real_advertising else 'gatt-integration-verification.json' if real_gatt else 'qwr-integration-verification.json' if real_qwr else 'registry-integration-verification.json' if real_registry else 'verification.json');receipt.unlink(missing_ok=True);report_path=out/'report.json';report=json.loads(report_path.read_text());layout=report['layout'];obj=out/'ble-dispatch.o';assert sha(obj)==report['selected_object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==layout['application_sha256'];registry_report=BASE/'sdk-connection-events/report.json';registry=BASE/'sdk-connection-events/connection-events.o';assert sha(registry)==json.loads(registry_report.read_text())['selected_object_sha256'];memory_report=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(memory_report.read_text())['relocatable_sha256']
    handler_names=list(layout['handlers']);handler_addresses={name:int(address,16) for name,address in layout['handlers'].items()};contexts={name:int(address,16) for name,address in layout['contexts'].items()};boundaries={key+str(i):int(pair[j],16) for i,pair in enumerate(layout['ranges']) for j,key in enumerate(('__start_sdh_ble_observers','__stop_sdh_ble_observers'))}
    qwr_report=BASE/'sdk-qwr/report.json';qwr=BASE/'sdk-qwr/qwr.o'
    if real_qwr:assert sha(qwr)==json.loads(qwr_report.read_text())['selected_object_sha256']
    gatt_reports={};gatt_objects=[]
    if real_gatt:
        for name,path,key in (('native-gatt/report.json','native-gatt/native_gatt_observer.o',None),('sdk-gatt/report.json','sdk-gatt/gatt-init.o','selected_object_sha256'),('watchdog-logging/report.json','watchdog-logging/mode-getter-only.o','selected_getter_sha256')):
            r=json.loads((BASE/name).read_text());o=BASE/path;assert sha(o)==(r[key] if key else r['units'][0]['object_sha256']);gatt_reports[name]=sha(BASE/name);gatt_objects.append(str(o))
        sr=json.loads((BASE/'watchdog-logging/report.json').read_text());assert sha(BASE/'watchdog-logging/nrf_strerror.o')==next(r for r in sr['units'] if r['source'].endswith('/nrf_strerror.c'))['object_sha256']
        gatt_objects.append(str(BASE/'watchdog-logging/nrf_strerror.o'))
    if real_advertising:
        advertising_parent='sdk-advertising-init' if real_advertising_init else 'sdk-advertising';advertising_report=BASE/(advertising_parent+'/report.json');advertising=BASE/(advertising_parent+'/advertising.o');assert sha(advertising)==json.loads(advertising_report.read_text())['selected_object_sha256'];gatt_reports[advertising_parent+'/report.json']=sha(advertising_report);gatt_objects.append(str(advertising))
    comparisons=0;svc_total={};callback_total={};qwr_svc_total={};gatt_svc_total={};advertising_svc_total={}

    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';data_sections=[('.sdh_ble_observers'+str(i),int(pair[0],16)) for i,pair in enumerate(layout['ranges'])]+[('.rodata.sdh_ble_observers_array',0x9ca70),('.rodata.sdh_ble_observers',0x9ca94)]
        ld.write_text('SECTIONS { '+('.r1.advertising.a 0x20007e64 (NOLOAD) : { *(.r1.advertising.a) } .r1.advertising.b 0x200082b0 (NOLOAD) : { *(.r1.advertising.b) } ' if real_advertising else '')+('.r1.gatt.context 0x20007e1c (NOLOAD) : { *(.r1.gatt.context) } .r1.log.mode 0x200068ec : { *(.r1.log.mode) } ' if real_gatt else '')+(''.join('.r1.qwr.'+letter+' '+hex(0x20007e40+i*12)+' (NOLOAD) : { *(.r1.qwr.'+letter+') } ' for i,letter in enumerate('abc')) if real_qwr else '')+''.join(name+' '+hex(address)+' : { *('+name+') } ' for name,address in data_sections)+' .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.m_stack_is_enabled 0x20007a1b (NOLOAD) : { *(.bss.m_stack_is_enabled) } .bss.m_bcs 0x2002bdb0 (NOLOAD) : { *(.bss.m_bcs) } /DISCARD/ : { *(.comment) *(.note*) } }')
        roots=('r1_sdk_ble_events_poll','r1_sdk_connection_observer','r1_ble_observers_priority1','r1_ble_observers_priority2','r1_ble_observers_priority3')+(('nrf_ble_qwr_init','nrf_ble_qwr_conn_handle_assign') if real_qwr else ())+(('nrf_ble_gatt_init',) if real_gatt else ())+(('ble_advertising_init',) if real_advertising_init else ());handler_bindings={name:0x100e101+i*16 for i,name in enumerate(handler_names) if name!='r1_sdk_connection_event' and not (real_qwr and name=='nrf_ble_qwr_on_ble_evt') and not (real_gatt and name=='nrf_ble_gatt_on_ble_evt') and not (real_advertising and name=='ble_advertising_on_ble_evt')}
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+name for name in roots],*['--defsym='+name+'='+hex(value) for name,value in {**boundaries,**{n:a for n,a in contexts.items() if not (real_qwr and n.startswith('r1_ble_qwr_context_')) and not (real_gatt and n=='r1_ble_gatt_context') and not (real_advertising and n.startswith('r1_ble_advertising_context_'))},**handler_bindings,'r1_adc_error':0x100e001,**({'r1_structured_log_format':0x100ea01,'nrf_log_frontend_std_1':0x100ea11,'nrf_log_frontend_std_2':0x100ea21} if real_gatt else {})}.items()],str(obj),str(registry),str(memory),*([str(qwr)] if real_qwr else []),*gatt_objects,'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3};assert syms['r1_sdk_ble_stack_enabled']==0x20007a1b and syms['r1_sdk_ble_observer_sections']==0x9ca70 and syms['r1_sdk_ble_observer_set']==0x9ca94
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);svc_total[id(uc)]=0;callback_total[id(uc)]=0;qwr_svc_total[id(uc)]=0;gatt_svc_total[id(uc)]=0;advertising_svc_total[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());initial_sections={}
        for name,address in data_sections:
            path=tmp/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',name+'='+str(path),str(elf)],check=True);raw=path.read_bytes();initial_sections[name]=raw;candidate.mem_write(address,raw)
        assert initial_sections['.rodata.sdh_ble_observers_array']==bytes(stock.mem_read(0x9ca70,32)) and initial_sections['.rodata.sdh_ble_observers']==bytes(stock.mem_read(0x9ca94,12))
        for row in layout['records']:
            address=int(row['address'],16);old=struct.unpack('<2I',bytes(stock.mem_read(address,8)));new=struct.unpack('<2I',bytes(candidate.mem_read(address,8)));expected_context=contexts[row['context']] if row['context'] else 0
            assert old==(handler_addresses[row['handler']]|1,expected_context) and new==((syms[row['handler']]|1),expected_context)
        states={};callbacks={address:name for name,address in handler_addresses.items()};callbacks.update({syms[name]&~1:name for name in handler_names})
        def hook(uc,address,size,user):
            f=states[id(uc)]
            if address==0x100e900:f['trace'].append(('qwr_error',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if address in (0x4e5bc,0x100e000):f['trace'].append(('error',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0x87654321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if address not in callbacks:return
            name=callbacks[address];buffer=uc.reg_read(UC_ARM_REG_R0);context=uc.reg_read(UC_ARM_REG_R1);assert buffer==f['buffer'];f['trace'].append(('callback',name,context,bytes(uc.mem_read(buffer,f['length']))));callback_total[id(uc)]+=1
            if f['disable']:uc.mem_write(0x20007a1b,b'\0')
            if f['mutate'] and f['length'] and name!='r1_sdk_connection_event':
                at=buffer+f['length']-1;uc.mem_write(at,bytes([uc.mem_read(at,1)[0]^0x5a]))
            if real_registry and name=='r1_sdk_connection_event':return
            if real_qwr and name=='nrf_ble_qwr_on_ble_evt':return
            if real_gatt and name=='nrf_ble_gatt_on_ble_evt':return
            if real_advertising and name=='ble_advertising_on_ble_evt':return
            uc.reg_write(UC_ARM_REG_R0,0xdeadbeef);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);opcode=bytes(uc.mem_read(pc-2,2));f=states[id(uc)]
            if opcode in (b'\x72\xdf',b'\x73\xdf'):
                assert real_advertising;a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1)
                if opcode[0]==114:
                    c=uc.reg_read(UC_ARM_REG_R2);assert a in (0x20007e64+84,0x200082b0+84);f['trace'].append(('adv_configure',uc.mem_read(a,1)[0],bytes(uc.mem_read(b,16)) if b else None,bytes(uc.mem_read(c,24))))
                    if uc.mem_read(a,1)[0]==255:uc.mem_write(a,b'\x41')
                else:f['trace'].append(('adv_start',a,b))
                uc.reg_write(UC_ARM_REG_R0,0);advertising_svc_total[id(uc)]+=1;return
            if opcode in (b'\x90\xdf',b'\xa5\xdf',b'\xb5\xdf'):
                assert real_gatt;a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1);f['trace'].append(('gatt_svc',opcode[0],a,bytes(uc.mem_read(b,8)) if opcode[0]==144 else b));uc.reg_write(UC_ARM_REG_R0,0);gatt_svc_total[id(uc)]+=1;return
            if opcode in (b'\x66\xdf',b'\xb0\xdf'):
                assert real_qwr;ptr=uc.reg_read(UC_ARM_REG_R1);f['trace'].append(('qwr_svc',opcode[0],uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(ptr,16)) if opcode[0]==176 else ptr,f['qwr_status']));uc.reg_write(UC_ARM_REG_R0,f['qwr_status']);qwr_svc_total[id(uc)]+=1;return
            assert opcode==b'\x61\xdf';buffer=uc.reg_read(UC_ARM_REG_R0);length_pointer=uc.reg_read(UC_ARM_REG_R1);assert buffer%4==0 and struct.unpack('<H',bytes(uc.mem_read(length_pointer,2)))[0]==500
            index=f['gets'];f['gets']+=1;status,payload=f['items'][index] if index<len(f['items']) else (5,b'');f['trace'].append(('svc97',500,status,len(payload)));svc_total[id(uc)]+=1
            if status==0:uc.mem_write(buffer,payload);f['buffer']=buffer;f['length']=len(payload)
            uc.mem_write(length_pointer,struct.pack('<H',len(payload)));uc.reg_write(UC_ARM_REG_R0,status)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_INTR,svc)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        ranges=[tuple(map(lambda v:int(v,16),pair)) for pair in layout['ranges']]
        def run(uc,items,enabled=1,empty_mask=0,mutate=False,disable=False,qwr_status=0):
            for i,(first,last) in enumerate(ranges):uc.mem_write(0x9ca70+i*8,struct.pack('<2I',first,first if empty_mask&(1<<i) else last))
            uc.mem_write(0x20007a1b,bytes([enabled]));uc.mem_write(0x2002bdb0,bytes(124));states[id(uc)]=dict(qwr_status=qwr_status,items=items,trace=[],gets=0,buffer=0,length=0,mutate=mutate,disable=disable)
            if real_advertising_init:
                init=bytearray(172);init[3]=6;init[124]=1;init[125]=1;struct.pack_into('<6I',init,128,32,111,64,222,128,333);uc.mem_write(0x20003400,bytes(init))
                for base in (0x20007e64,0x200082b0):
                    uc.mem_write(base,bytes(1076));uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,base);uc.reg_write(UC_ARM_REG_R1,0x20003400)
                    uc.emu_start((0x51716 if uc is stock else syms['ble_advertising_init'])|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_R0)==0
                states[id(uc)]['init_trace']=list(states[id(uc)]['trace']);states[id(uc)]['trace']=[]
            elif real_advertising:
                for base in (0x20007e64,0x200082b0):
                    raw=bytearray(1076);raw[0]=1;raw[8]=1;raw[9]=1;struct.pack_into('<6I',raw,12,32,111,64,222,128,333);raw[44]=1;raw[48]=3;raw[84]=255;raw[85:94]=b'\x02\x01\x06\x05\x09TEST';struct.pack_into('<IH2xIH2xI',raw,1040,base+85,9,base+561,0,base+1040);struct.pack_into('<H',raw,1060,0xffff);uc.mem_write(base,bytes(raw))
            if real_gatt:
                uc.mem_write(0x20007e1c,bytes(36));uc.mem_write(0x200068ec,b'\0');uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,0x20007e1c);uc.reg_write(UC_ARM_REG_R1,0)
                uc.emu_start((0x78186 if uc is stock else syms['nrf_ble_gatt_init'])|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_R0)==0
            if real_qwr:
                uc.mem_write(0x20007e40,bytes(36));uc.mem_write(0x20003200,struct.pack('<I',0x100e901))
                for i in range(3):
                    uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,0x20007e40+i*12);uc.reg_write(UC_ARM_REG_R1,0x20003200)
                    uc.emu_start((0x783b6 if uc is stock else syms['nrf_ble_qwr_init'])|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_R0)==0
                    uc.reg_write(UC_ARM_REG_R0,0x20007e40+i*12);uc.reg_write(UC_ARM_REG_R1,i);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                    uc.emu_start((0x783a0 if uc is stock else syms['nrf_ble_qwr_conn_handle_assign'])|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_R0)==0
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,0xfedcba98)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((0x7a38c if uc is stock else syms['r1_sdk_ble_events_poll'])|1,0x20000100,count=5000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000;assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            return list(states[id(uc)]['trace']),bytes(uc.mem_read(0x2002bdb0,124)),uc.mem_read(0x20007a1b,1)[0],bytes(uc.mem_read(0x20007e40,36)) if real_qwr else None,bytes(uc.mem_read(0x20007e1c,36)) if real_gatt else None,tuple(bytes(uc.mem_read(a,1076)) for a in (0x20007e64,0x200082b0)) if real_advertising else None,states[id(uc)].get('init_trace',[]) if real_advertising_init else None
        def compare(items,**case):
            nonlocal comparisons
            a=run(stock,items,**case);b=run(candidate,items,**case);assert a==b,(items,case,a,b);comparisons+=1;return a
        def packet(event,handle=0,role=2):
            raw=bytearray(64);struct.pack_into('<HHH',raw,0,event,64,handle);raw[15]=role;return bytes(raw)
        expected_names=[row['handler'] for row in layout['records']]
        for enabled,error,empty,mutate,disable in itertools.product((0,1),(1,5,8,12,0xffffffff),range(16),(False,True),(False,True)):
            items=[(0,packet(16,1)),(0,packet(17,1)),(error,b'')];a=compare(items,enabled=enabled,empty_mask=empty,mutate=mutate,disable=disable)
            if not enabled:assert a[0]==[]
            else:
                active=[row['handler'] for row in layout['records'] if not empty&(1<<next(i for i,(first,last) in enumerate(ranges) if first<=int(row['address'],16)<last))];observed=[e[1] for e in a[0] if e[0]=='callback'];assert observed==active*2
                assert sum(e[0]=='svc97' for e in a[0])==3
                if error!=5:assert a[0][-1]==('error',error)
        for count in range(9):compare([(0,packet(16,i%20)) for i in range(count)])
        for error in (1,5,8,12,0x80000000,0xffffffff):compare([(error,b'')])
        if not real_registry:
            for size in (0,1,4,8,16,244,499,500):compare([(0,bytes((i*31+5)&255 for i in range(size)))])
        else:
            for handle in (*range(20),20,31,0xffff):
                a=compare([(0,packet(16,handle))]);words=struct.unpack('<31I',a[1]);assert words[1]==(1<<handle if handle<20 else 0) and words[2]==words[1]
            a=compare([(0,packet(16,0)),(0,packet(17,0)),(0,packet(16,1))]);words=struct.unpack('<31I',a[1]);assert words[1]==words[2]==2
        if real_qwr:
            for handle,status,op in itertools.product((0,1,2,3,0xffff),(0,17,8,0xffffffff),(4,5,6)):
                request=bytearray(packet(1,handle));request[8]=1;auth=bytearray(packet(81,handle));auth[6]=2;auth[14]=op
                compare([(0,bytes(request)),(0,bytes(auth)),(0,packet(17,handle)),(0,bytes(request))],qwr_status=status)
        if real_gatt:
            for handle,remote in itertools.product((0,1,2,3,20,0xffff),(0,23,247,0xffff)):
                packets=[]
                for event in (16,35,36,58,85,17):
                    raw=bytearray(packet(event,handle));struct.pack_into('<HHH',raw,6,remote,remote,remote);packets.append((0,bytes(raw)))
                compare(packets)
        if real_advertising:
            for handle,reason in itertools.product((0,1,2,0xffff),(0,1,2,3)):
                term=bytearray(packet(38,handle));term[8]=reason
                compare([(0,packet(16,handle,role=1)),(0,packet(17,handle)),(0,bytes(term)),(0,bytes(term)),(0,bytes(term))])
    assert advertising_svc_total[id(stock)]==advertising_svc_total[id(candidate)]
    assert gatt_svc_total[id(stock)]==gatt_svc_total[id(candidate)]
    assert qwr_svc_total[id(stock)]==qwr_svc_total[id(candidate)]
    assert svc_total[id(stock)]==svc_total[id(candidate)] and callback_total[id(stock)]==callback_total[id(candidate)]
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),selected_object_sha256=sha(obj),provider_reports={'sdk-connection-events/report.json':sha(registry_report),'runtime/report.json':sha(memory_report),**gatt_reports,**({'sdk-qwr/report.json':sha(qwr_report)} if real_qwr else {})},actual_advertising_init=real_advertising_init,advertising_init_calls=2*comparisons if real_advertising_init else 0,actual_advertising_handler=real_advertising,advertising_svc_calls=advertising_svc_total[id(candidate)],actual_gatt_handler=real_gatt,gatt_svc_calls=gatt_svc_total[id(candidate)],actual_qwr_handler=real_qwr,qwr_svc_calls=qwr_svc_total[id(candidate)],actual_registry_handler=real_registry,comparisons=comparisons,svc97_calls=svc_total[id(candidate)],observer_calls=callback_total[id(candidate)],observer_records_pointer_normalized=12,observer_record_bytes_pointer_normalized=96,section_ranges_bytes_compared=32,section_set_bytes_compared=12,scope='Actual SDK SVC97 poll and legacy iterator; exact four priority ranges and 12 typed records, 500-byte request reset, error/disabled/empty-range handling, callback ordering/context/byte visibility, ignored returns, enabled-state mutation and saved registers/stack',limitations=['SVC97 responses are deterministic hooks; this is not live SoftDevice event delivery.','Unknown observer bodies are intercepted; registry, QWR, GATT and advertising execute only in their named integration variants. QWR/GATT/advertising contexts are typed source records with product initialization gates; other contexts remain address anchors without full extent/initialization proof.','Empty ranges and callback mutations are controlled fixture changes; real concurrency, timing, observer lifetime, original instructions and full-image linking remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} BLE dispatcher comparisons passed; {callback_total[id(candidate)]} observer calls (actual registry: {real_registry})')
if __name__=='__main__':main()

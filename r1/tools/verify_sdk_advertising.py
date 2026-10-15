#!/usr/bin/env python3
"""Stock advertising state machine versus pinned unchanged Nordic C."""
import hashlib,itertools,json,random,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=0x20007e64;B=0x200082b0;SIZE=1076;EVT=0x20003000;INPUT=0x20004000;OFFSET=0x20004100;EVENT_CB=0x100e801;ERROR_CB=0x100e811
ENTRIES={'ble_advertising_on_ble_evt':0x51806,'ble_advertising_start':0x51870,'ble_advertising_conn_cfg_tag_set':0x51710,'ble_advertising_modes_config_set':0x517fe,'r1_sdk_adv_flags_set':0x64f1a,'r1_sdk_adv_phy_is_valid':0x7f0c8,'r1_sdk_adv_use_whitelist':0x94dd8,'ble_advdata_parse':0x516aa,'ble_advdata_search':0x516ca}
RETURNS=set(ENTRIES)-{'ble_advertising_on_ble_evt','ble_advertising_conn_cfg_tag_set','ble_advertising_modes_config_set'}
def main():
    init_provider='--init-provider' in sys.argv;out=BASE/('sdk-advertising-init' if init_provider else 'sdk-advertising');rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'advertising.o';receipt=out/('legacy-verification.json' if init_provider else 'verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==report['selected_object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';mr=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256']
    states={};svcs={};counts={n:0 for n in ENTRIES}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.advertising.a 0x20007e64 (NOLOAD) : { *(.r1.advertising.a) } .r1.advertising.b 0x200082b0 (NOLOAD) : { *(.r1.advertising.b) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=ble_advertising_start',str(obj),str(memory),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        for name,addr in report['context_addresses'].items():assert syms[name]==int(addr,16)
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);svcs[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        for address in (A,B):assert bytes(stock.mem_read(address,SIZE))==bytes(candidate.mem_read(address,SIZE))==bytes(SIZE)
        def code(uc,address,size,user):
            if address not in (EVENT_CB&~1,ERROR_CB&~1):return
            f=states[id(uc)];value=uc.reg_read(UC_ARM_REG_R0);kind='event' if address==EVENT_CB&~1 else 'error';f['trace'].append((kind,value));base=f['base']
            if kind=='event' and f['reply']:
                if value==8:uc.mem_write(base+1062,b'\x01\x11\x22\x33\x44\x55\x66')
                if value==7:uc.mem_write(base+1072,b'\x01')
            if f['mutation']:uc.mem_write(base+48,b'\x57');uc.mem_write(base+84,b'\x41');uc.mem_write(base+4,b'\x01')
            uc.reg_write(UC_ARM_REG_R0,0xabcdef01);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);op=bytes(uc.mem_read(pc-2,2));assert op[1]==0xdf and op[0] in (114,115),op;f=states[id(uc)];i=f['svcs'];f['svcs']+=1;status=f['statuses'][min(i,len(f['statuses'])-1)];svcs[id(uc)]+=1;a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1)
            if op[0]==114:
                c=uc.reg_read(UC_ARM_REG_R2);assert a==f['base']+84 and c==f['base']+60;raw=bytes(uc.mem_read(c,24));data=bytes(uc.mem_read(b,16)) if b else None;f['trace'].append(('configure',uc.mem_read(a,1)[0],data,raw,status))
                if status==0 and uc.mem_read(a,1)[0]==255:uc.mem_write(a,b'\x41')
            else:f['trace'].append(('start',a,b,status))
            uc.reg_write(UC_ARM_REG_R0,status)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,code);uc.hook_add(UC_HOOK_INTR,svc)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def context(base=A,initialized=1,flags=(0,0,0,0,1,1),mode=3,callbacks=True,whitelist=0,disabled=0,peer=False,extended=0,primary=1,secondary=1,fill=0):
            raw=bytearray([fill])*SIZE;raw[1]=0;raw[1062:1069]=bytes(7);raw[1069:1073]=bytes(4);raw[0]=initialized;raw[2]=mode;raw[4:10]=bytes(flags);struct.pack_into('<6I',raw,12,32,111,64,222,128,333);raw[36]=extended;struct.pack_into('<II',raw,40,secondary,primary);raw[48]=3;struct.pack_into('<II',raw,52,EVENT_CB if callbacks else 0,ERROR_CB if callbacks else 0);raw[84]=255;raw[85:94]=b'\x02\x01\x06\x05\x09TEST';struct.pack_into('<IH2xIH2xI',raw,1040,base+85,9,base+561,0,base+1040);struct.pack_into('<H',raw,1060,1);raw[1070]=disabled;raw[1072]=whitelist
            if peer:raw[1062:1069]=b'\x01\x11\x22\x33\x44\x55\x66'
            return bytes(raw)
        def packet(event=0,handle=1,role=1,reason=1):
            raw=bytearray(64);struct.pack_into('<HHH',raw,0,event,64,handle);raw[8]=reason;raw[15]=role;return bytes(raw)
        def run(uc,name,args,seed,event,data,offset,statuses,reply,mutation,base):
            for address in (A,B):uc.mem_write(address-4,b'LEFT');uc.mem_write(address,seed if address==base else bytes(SIZE));uc.mem_write(address+SIZE,b'RGHT')
            uc.mem_write(EVT,event);uc.mem_write(INPUT,data+bytes(512-len(data)));uc.mem_write(OFFSET,struct.pack('<H',offset));states[id(uc)]=dict(trace=[],svcs=0,statuses=statuses,reply=reply,mutation=mutation,base=base);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            for address in (A,B):assert bytes(uc.mem_read(address-4,4))==b'LEFT' and bytes(uc.mem_read(address+SIZE,4))==b'RGHT'
            assert bytes(uc.mem_read(EVT,64))==event
            return uc.reg_read(UC_ARM_REG_R0) if name in RETURNS else None,bytes(uc.mem_read(A,SIZE)),bytes(uc.mem_read(B,SIZE)),bytes(uc.mem_read(OFFSET,2)),list(states[id(uc)]['trace']),bytes(uc.mem_read(INPUT,512))
        def compare(name='ble_advertising_start',args=None,seed=None,event=None,data=bytes(44),offset=0,statuses=(0,),reply=True,mutation=False,base=A):
            seed=seed if seed is not None else context(base);event=event if event is not None else packet();args=args if args is not None else (base,3);a=run(stock,name,args,seed,event,data,offset,statuses,reply,mutation,base);b=run(candidate,name,args,seed,event,data,offset,statuses,reply,mutation,base);assert a==b,(name,args,seed[:60],event,statuses,reply,mutation,a,b);counts[name]+=1;return a
        for base,flags,mode,extended,reply,callbacks in itertools.product((A,B),itertools.product((0,1),repeat=6),range(5),(0,1),(False,True),(False,True)):
            compare(seed=context(base,flags=flags,extended=extended,callbacks=callbacks),args=(base,mode),reply=reply,base=base)
        for mode,whitelist,disabled,primary,secondary,statuses in itertools.product(range(5),(0,1),(0,1),(0,1,2,4,255),(0,1,2,4,255),((0,),(8,),(0,8),(8,0),(0,0,8))):
            compare(seed=context(flags=(0,1,1,1,1,1),whitelist=whitelist,disabled=disabled,extended=1,primary=primary,secondary=secondary),args=(A,mode),statuses=statuses)
        for event,handle,role,reason,mode in itertools.product((0,16,17,38,0xffff),(0,1,0xffff),(0,1,2,255),(0,1,2,3),range(5)):
            compare(name='ble_advertising_on_ble_evt',args=(EVT,A),seed=context(mode=mode),event=packet(event,handle,role,reason))
        for mode in range(256):
            for reason,status in itertools.product((1,2),(0,8)):
                compare(name='ble_advertising_on_ble_evt',args=(EVT,A),seed=context(mode=mode),event=packet(38,reason=reason),statuses=(status,))
        for event in (16,17,38):
            for callbacks,reply,mutation,status in itertools.product((False,True),(False,True),(False,True),(0,8)):
                compare(name='ble_advertising_on_ble_evt',args=(EVT,A),seed=context(flags=(0,1,1,1,1,1),callbacks=callbacks),event=packet(event),statuses=(status,),reply=reply,mutation=mutation)
        for base,mode in itertools.product((A,B),range(5)):
            a=compare(seed=context(base,initialized=0),args=(base,mode),base=base);assert a[0]==8 and not a[4]
        for disabled,callbacks,status in itertools.product((0,1),(False,True),(0,8)):
            a=compare(name='ble_advertising_on_ble_evt',args=(EVT,A),seed=context(flags=(disabled,0,0,0,1,1),callbacks=callbacks),event=packet(17),statuses=(status,))
            if disabled:assert not a[4]
        for fill in range(256):
            for mode in range(5):compare(seed=context(fill=fill),args=(A,mode))
            for event in (16,17,38):compare(name='ble_advertising_on_ble_evt',args=(EVT,A),seed=context(fill=fill),event=packet(event))
        for tag in range(256):compare(name='ble_advertising_conn_cfg_tag_set',args=(A,tag))
        rng=random.Random(0x51806)
        for _ in range(256):compare(name='ble_advertising_modes_config_set',args=(A,INPUT),data=rng.randbytes(44))
        for phy in (*range(256),0xffff,0x10000,0xffffffff):compare(name='r1_sdk_adv_phy_is_valid',args=(INPUT,),data=struct.pack('<I',phy))
        for flags in itertools.product((0,1),repeat=3):
            a=compare(name='r1_sdk_adv_use_whitelist',args=(A,),seed=context(flags=(0,flags[0],0,0,1,1),whitelist=flags[1],disabled=flags[2]));assert a[0]==int(flags[0] and flags[1] and not flags[2])
        for flag,status in itertools.product(range(256),(0,8)):compare(name='r1_sdk_adv_flags_set',args=(A,flag),statuses=(status,))
        records=[b'',b'\0',b'\x02\x01\x06',b'\x02\x01\x06\x05\x09TEST',bytes(range(64)),*[rng.randbytes(rng.randrange(1,65)) for _ in range(64)]]
        for raw,ad_type in itertools.product(records,range(256)):
            for name in ('ble_advdata_parse','ble_advdata_search'):
                args=(INPUT,len(raw),ad_type) if name.endswith('parse') else (INPUT,len(raw),OFFSET,ad_type)
                compare(name=name,args=args,data=raw,offset=0)
        for name in ('ble_advdata_parse','ble_advdata_search'):
            args=(0,64,1) if name.endswith('parse') else (0,64,OFFSET,1);assert compare(name=name,args=args)[0]==0
        for offset in (1,2,3,8,64,65535):compare(name='ble_advdata_search',args=(INPUT,9,OFFSET,9),data=b'\x02\x01\x06\x05\x09TEST',offset=offset)
    assert svcs[id(stock)]==svcs[id(candidate)]
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),selected_object_sha256=sha(obj),memory_report_sha256=sha(mr),comparisons=sum(counts.values()),comparisons_by_entry=counts,svc_calls=svcs[id(candidate)],compatible_context_initial_zero_bytes_compared=SIZE*2,scope='Unchanged SDK advertising observer/start/config/flags/PHY/whitelist and parsing; actual C memory, real SVC114/115 sites, mode selection, callbacks, all canonical bool configs, both contexts and guarded state',limitations=['SVC responses and event/error callbacks are deterministic fixtures; callback-owned peer/whitelist changes are controlled. No live SoftDevice/radio proof.','Boolean configuration values 0/1 and mode arguments0..4 are claimed; noncanonical bool bytes and wide invalid enum arguments remain separate compiler-domain gates.','Typed 1076-byte compatible storage and initial zeros do not establish complete product callback/mode initialization, original allocation identity or all writers.','This legacy oracle does not execute advertising initialization or encoding; their separate receipt is required. Full startup/linking, exact bytes and physical behavior remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} advertising/provider comparisons passed; {svcs[id(candidate)]} actual SVC paths')
if __name__=='__main__':main()

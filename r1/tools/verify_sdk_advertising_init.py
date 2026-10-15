#!/usr/bin/env python3
"""Advertising init/encoding and helper contracts against the authenticated image."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=0x20007e64;B=0x200082b0;SIZE=1076;INPUT=0x20003000;AUX=0x20004000;OUTPUT=0x20005000;LENGTH=0x20005500
ENTRIES={'ble_advertising_init':0x51716,'ble_advdata_encode':0x51528,'r1_sdk_adv_device_addr_encode':0x51fb8,'r1_sdk_adv_conn_int_encode':0x59bde,'r1_sdk_adv_manuf_encode':0x76088,'r1_sdk_adv_service_encode':0x8aba0,'r1_sdk_adv_name_encode':0x770bc,'r1_sdk_adv_uuid_list_sized_encode':0x95570,'r1_sdk_adv_data_size_max_get':0x489d6}
def main():
    out=BASE/'sdk-advertising-init';rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'advertising.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==report['selected_object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';mr=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(mr.read_text())['relocatable_sha256'];counts={n:0 for n in ENTRIES};states={};svcs={};capacity_overrun_cases=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.advertising.a 0x20007e64 (NOLOAD) : { *(.r1.advertising.a) } .r1.advertising.b 0x200082b0 (NOLOAD) : { *(.r1.advertising.b) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=ble_advertising_init',str(obj),str(memory),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);svcs[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);op=bytes(uc.mem_read(pc-2,2));assert op[1]==0xdf and op[0] in (100,109,114,115,121,125),op;f=states[id(uc)];index=f['calls'];f['calls']+=1;status=f['statuses'][min(index,len(f['statuses'])-1)];svcs[id(uc)]+=1;a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1);c=uc.reg_read(UC_ARM_REG_R2)
            if op[0]==109:
                f['trace'].append(('address',f['addr_type'],status))
                if status==0:uc.mem_write(a,bytes([f['addr_type']<<1])+b'ABCDEF')
            elif op[0]==121:
                f['trace'].append(('appearance',0x1234,status))
                if status==0:uc.mem_write(a,b'\x34\x12')
            elif op[0]==125:
                capacity=struct.unpack('<H',bytes(uc.mem_read(b,2)))[0];name=f['name'];f['trace'].append(('name',capacity,len(name),status))
                uc.mem_write(b,struct.pack('<H',len(name)))
                if status==0 and capacity:uc.mem_write(a,name[:capacity])
            elif op[0]==100:
                uuid=struct.unpack('<H',bytes(uc.mem_read(a,2)))[0];kind=uc.mem_read(a+2,1)[0];size={1:2,2:16,3:4}.get(kind,0);status=status or (7 if not size else 0);f['trace'].append(('uuid',uuid,kind,bool(c),size,status))
                if status==0:
                    uc.mem_write(b,bytes([size]))
                    if c:uc.mem_write(c,(struct.pack('<H',uuid)+bytes([kind])*14)[:size])
            elif op[0]==114:
                assert a in (A+84,B+84);f['trace'].append(('configure',uc.mem_read(a,1)[0],bytes(uc.mem_read(b,16)) if b else None,bytes(uc.mem_read(c,24)),status))
                if status==0:uc.mem_write(a,b'\x41')
            else:f['trace'].append(('start',a,b,status))
            uc.reg_write(UC_ARM_REG_R0,status)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_INTR,svc)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def fixture(kind='empty',size=3,name_type=2,short=4,uuid_types=(1,2),conn=(6,3200),null_data=False):
            adv=bytearray(60);aux=bytearray(2048)
            if kind in ('all','address'):adv[45]=1
            if kind in ('all','appearance'):adv[2]=1
            if kind in ('all','flags'):adv[3]=6
            if kind in ('all','power'):struct.pack_into('<I',adv,4,AUX);aux[0]=0x80
            if kind in ('all','uuids'):
                for at in (8,16,24):struct.pack_into('<H2xI',adv,at,len(uuid_types),AUX+16)
                for i,t in enumerate(uuid_types):struct.pack_into('<HBB',aux,16+i*4,0x1800+i,t,0)
            struct.pack_into('<HH',aux,64,*conn)
            if kind in ('all','interval'):struct.pack_into('<I',adv,32,AUX+64)
            struct.pack_into('<H2xH2xI',aux,80,0x1234,size,0 if null_data else AUX+512)
            if kind in ('all','manufacturer'):struct.pack_into('<I',adv,36,AUX+80)
            for i in range(3):struct.pack_into('<H2xH2xI',aux,96+i*12,0x180d+i,size,0 if null_data else AUX+512)
            if kind in ('all','service'):struct.pack_into('<I',adv,40,AUX+96);adv[44]=3
            if kind in ('all','name'):adv[0]=name_type;adv[1]=short
            aux[512:1024]=bytes((i*17+7)&255 for i in range(512));return bytes(adv),bytes(aux)
        def run(uc,name,args,adv,aux,capacity,offset,seed,statuses,device_name,addr_type,start_after):
            for base in (A,B):uc.mem_write(base-4,b'LEFT');uc.mem_write(base,seed);uc.mem_write(base+SIZE,b'RGHT')
            uc.mem_write(INPUT,adv);uc.mem_write(AUX,aux);uc.mem_write(OUTPUT-16,b'G'*16);uc.mem_write(OUTPUT,b'\xa5'*1024);uc.mem_write(OUTPUT+1024,b'H'*16);uc.mem_write(LENGTH,struct.pack('<H',capacity if name=='ble_advdata_encode' else offset));states[id(uc)]=dict(trace=[],calls=0,statuses=statuses,name=device_name,addr_type=addr_type)
            def invoke(address,parameters):
                uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.mem_write(0x2003f000,bytes(16))
                for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),parameters):uc.reg_write(r,v)
                for i,v in enumerate(parameters[4:]):uc.mem_write(0x2003f000+i*4,struct.pack('<I',v))
                for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
                uc.emu_start(address|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)];return uc.reg_read(UC_ARM_REG_R0)
            result=invoke(ENTRIES[name] if uc is stock else syms[name],args)
            if start_after and result==0:result=invoke(0x51870 if uc is stock else syms['ble_advertising_start'],(args[0],3))
            for base in (A,B):assert bytes(uc.mem_read(base-4,4))==b'LEFT' and bytes(uc.mem_read(base+SIZE,4))==b'RGHT'
            assert bytes(uc.mem_read(OUTPUT-16,16))==b'G'*16 and bytes(uc.mem_read(OUTPUT+1024,16))==b'H'*16
            assert bytes(uc.mem_read(INPUT,len(adv)))==adv and bytes(uc.mem_read(AUX,len(aux)))==aux
            return result,bytes(uc.mem_read(OUTPUT,1024)),bytes(uc.mem_read(LENGTH,2)),bytes(uc.mem_read(A,SIZE)),bytes(uc.mem_read(B,SIZE)),list(states[id(uc)]['trace'])
        def compare(name='ble_advdata_encode',args=None,kind='empty',capacity=31,offset=0,size=3,statuses=(0,),device_name=b'OpenCFW',addr_type=0,seed=None,adv=None,aux=None,start_after=False,**fixture_args):
            nonlocal capacity_overrun_cases
            a,b=fixture(kind,size=size,**fixture_args);adv=adv if adv is not None else a;aux=aux if aux is not None else b;seed=seed if seed is not None else bytes(SIZE);args=args if args is not None else (INPUT,OUTPUT,LENGTH);x=run(stock,name,args,adv,aux,capacity,offset,seed,statuses,device_name,addr_type,start_after);y=run(candidate,name,args,adv,aux,capacity,offset,seed,statuses,device_name,addr_type,start_after);assert x==y,(name,args,kind,capacity,offset,size,statuses,fixture_args,seed[0],adv[152] if len(adv)>152 else None,x[0],y[0],[(i,next((j for j,(a,b) in enumerate(zip(u,v)) if a!=b),None)) for i,(u,v) in enumerate(zip(x[1:5],y[1:5]),1) if u!=v],x[-1],y[-1]);counts[name]+=1
            if name=='ble_advdata_encode' and struct.unpack('<H',x[2])[0]>capacity:capacity_overrun_cases+=1
            return x
        kinds=('empty','address','appearance','flags','power','uuids','interval','manufacturer','service','name','all')
        for kind,capacity,status in itertools.product(kinds,range(65),(0,8,12,0xffffffff)):
            compare(kind=kind,capacity=capacity,statuses=(status,))
        for name_type,short,name_len,capacity in itertools.product((0,1,2,255),(0,1,4,31),(0,1,4,31,238,254,255,260),(0,2,3,8,31,238,255,512)):
            compare(kind='name',name_type=name_type,short=short,capacity=capacity,device_name=bytes((i%26)+65 for i in range(name_len)))
        for size,null_data,capacity in itertools.product((0,1,3,31,250,251,252,253,254,255,256,260),(False,True),(0,3,4,31,238,512)):
            for kind in ('manufacturer','service'):compare(kind=kind,size=size,null_data=null_data,capacity=capacity)
        for conn in itertools.product((0,5,6,7,3200,3201,65535),repeat=2):compare(kind='interval',conn=conn)
        for uuid_types,capacity,statuses in itertools.product(((1,),(2,),(3,),(0,),(1,2,3),(1,1,1,1)),(0,3,4,18,31,64),((0,),(8,),(0,8),(0,0,8))):compare(kind='uuids',uuid_types=uuid_types,capacity=capacity,statuses=statuses)
        for kind,helper,pointer in (('address','r1_sdk_adv_device_addr_encode',None),('interval','r1_sdk_adv_conn_int_encode',AUX+64),('manufacturer','r1_sdk_adv_manuf_encode',AUX+80),('service','r1_sdk_adv_service_encode',INPUT),('name','r1_sdk_adv_name_encode',INPUT)):
            for capacity,offset,status in itertools.product((0,3,4,31,238,512),(0,1,7,31,238),(0,8)):
                args=(OUTPUT,LENGTH,capacity) if pointer is None else (pointer,OUTPUT,LENGTH,capacity);compare(name=helper,args=args,kind=kind,capacity=capacity,offset=offset,statuses=(status,))
        for uuid_size,ad_type,capacity,offset in itertools.product((2,4,16),(2,3,6,7,20,21),(0,3,18,64),(0,3,31)):
            compare(name='r1_sdk_adv_uuid_list_sized_encode',args=(INPUT+8,ad_type,uuid_size,OUTPUT,LENGTH,capacity),kind='uuids',capacity=capacity,offset=offset)
        for base,initialized,extended,directed,status,kind in itertools.product((A,B),(0,1),(0,1),(0,1),(0,8),('empty','all','flags')):
            adv,aux=fixture(kind);init=bytearray(172);init[:60]=adv;init[60:120]=adv;init[120+2]=directed;init[120+4]=1;init[120+5]=1;init[120+32]=extended;struct.pack_into('<6I',init,128,32,111,64,222,128,333);seed=bytearray([0xa5])*SIZE;seed[0]=initialized
            compare(name='ble_advertising_init',args=(base,INPUT),adv=bytes(init),aux=aux,seed=bytes(seed),statuses=(status,))
        for kind in kinds:
            adv,aux=fixture(kind);init=bytearray(172);init[:60]=adv;init[60:120]=adv;init[124]=1;init[125]=1;struct.pack_into('<6I',init,128,32,111,64,222,128,333)
            compare(name='ble_advertising_init',args=(A,INPUT),adv=bytes(init),aux=aux,start_after=True)
        for args in ((0,INPUT),(A,0),(0,0)):assert compare(name='ble_advertising_init',args=args,adv=bytes(172))[0]==14
        for extended in (0,1):
            seed=bytearray(SIZE);seed[36]=extended;a=compare(name='r1_sdk_adv_data_size_max_get',args=(A,),seed=bytes(seed));assert a[0]==(238 if extended else 31)
    assert svcs[id(stock)]==svcs[id(candidate)]
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),selected_object_sha256=sha(obj),memory_report_sha256=sha(mr),comparisons=sum(counts.values()),comparisons_by_entry=counts,svc_calls=svcs[id(candidate)],native_capacity_overrun_cases=capacity_overrun_cases,scope='Unchanged SDK advertising init and every encode family, actual source memory, guarded outputs/contexts, short/full names, UUID-size queries/writes, manufacturer/service/connection records, size/error propagation and init-to-start sequences',limitations=['Controller/identity/appearance/name/UUID replies are deterministic SVC fixtures, not actual SoftDevice execution.','Only mapped valid pointers and bounded output spans are covered. Any source-observed writes beyond a supplied capacity are preserved, not a safety or protocol-conformance claim.','Canonical bool values are used. Product-owned initializer values/callbacks, all application writers, original allocation identity, byte identity, full-image linking and hardware remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} advertising init/encode comparisons passed; {svcs[id(candidate)]} actual SVC paths')
if __name__=='__main__':main()

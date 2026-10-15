#!/usr/bin/env python3
"""GATT initialization proof plus an explicit upstream connected-path counterexample."""
import hashlib,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CTX=0x20007e1c;EVT=0x20003000

def main():
    out=BASE/'sdk-gatt';rp=out/'report.json';report=json.loads(rp.read_text());obj=out/'gatt-init.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==report['selected_object_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    counts={'nrf_ble_gatt_init':0,'r1_sdk_gatt_link_init':0};states={};counterexamples=[]
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.gatt.context 0x20007e1c (NOLOAD) : { *(.r1.gatt.context) } /DISCARD/ : { *(.comment) *(.note*) } }')
        # Full SDK object is included only to measure its observer mismatch.
        sdk_obj=out/'nrf_ble_gatt.o';context_obj=out/'native_gatt_context.o'
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_ble_gatt_init','--defsym=__start_log_const_data=0x100d000','--defsym=nrf_log_frontend_std_1=0x100e001','--defsym=nrf_log_frontend_std_2=0x100e011','--defsym=nrf_strerror_get=0x100e021',str(sdk_obj),str(context_obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3};assert syms['r1_ble_gatt_context']==CTX
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(CTX,36))==bytes(candidate.mem_read(CTX,36))==bytes(36)
        def hook(uc,address,size,user):assert address not in (0x100e000,0x100e010,0x100e020),'Unclaimed SDK logging path executed'
        def svc(uc,number,user):
            pc=uc.reg_read(UC_ARM_REG_PC);assert bytes(uc.mem_read(pc-2,2))==b'\x90\xdf';r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);params=bytes(uc.mem_read(r1,8));assert bytes(uc.mem_read(r2,6))==bytes(6);states[id(uc)].append((144,r0,list(struct.unpack('<4H',params))));uc.reg_write(UC_ARM_REG_R0,0)
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_INTR,svc)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        entries={'nrf_ble_gatt_init':0x78186,'r1_sdk_gatt_link_init':0x74f20,'nrf_ble_gatt_on_ble_evt':0x781b4}
        def run(uc,name,args,seed,event=bytes(64)):
            uc.mem_write(CTX-4,b'LEFT');uc.mem_write(CTX,seed);uc.mem_write(CTX+36,b'RGHT');uc.mem_write(EVT,event);states[id(uc)]=[];uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((entries[name] if uc is stock else syms[name])|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            assert bytes(uc.mem_read(CTX-4,4))==b'LEFT' and bytes(uc.mem_read(CTX+36,4))==b'RGHT' and bytes(uc.mem_read(EVT,64))==event
            return uc.reg_read(UC_ARM_REG_R0) if name=='nrf_ble_gatt_init' else None,bytes(uc.mem_read(CTX,36)),list(states[id(uc)])
        def compare(name,args,seed):
            a=run(stock,name,args,seed);b=run(candidate,name,args,seed);assert a==b,(name,args,seed,a,b);assert not a[2];counts[name]+=1;return a
        rng=random.Random(0x78186);seeds=[bytes([i])*36 for i in range(256)]+[rng.randbytes(36) for _ in range(128)]
        for seed in seeds:
            for callback in (0,1,0x100e101,0x20000101,0x79dc9,0xffffffff):
                a=compare('nrf_ble_gatt_init',(CTX,callback),seed);expected=bytearray(seed);struct.pack_into('<HHB',expected,0,247,247,251);struct.pack_into('<I',expected,32,callback)
                for i in range(3):struct.pack_into('<HHBBBB',expected,6+i*8,247,23,0,0,251,27)
                assert a[0]==0 and a[1]==bytes(expected)
            assert compare('nrf_ble_gatt_init',(0,0xffffffff),seed)[0]==14
            for offset in (0,2,6,8,14,22,28):
                a=compare('r1_sdk_gatt_link_init',(CTX+offset,),seed);expected=bytearray(seed);struct.pack_into('<HHBBBB',expected,offset,247,23,0,0,251,27);assert a[1]==bytes(expected)
        # Native startup call site supplies GATT context and null event callback.
        native_init=[]
        def callsite(uc,address,size,user):
            if address==0x78186:native_init.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
        hook_handle=stock.hook_add(UC_HOOK_CODE,callsite);stock.reg_write(UC_ARM_REG_R1,0xffffffff);stock.emu_start(0x4df1f,0x4df26,count=10000);stock.hook_del(hook_handle);assert native_init==[(CTX,0)]
        event=bytearray(64);struct.pack_into('<HHH',event,0,16,64,1);event[15]=1
        for desired,effective in ((0,27),(27,27),(27,251),(251,251),(251,27)):
            seed=bytearray(36);struct.pack_into('<HHB',seed,0,247,247,desired)
            for i in range(3):struct.pack_into('<HHBBBB',seed,6+i*8,247,23,0,0,desired,effective)
            a=run(stock,'nrf_ble_gatt_on_ble_evt',(EVT,CTX),bytes(seed),bytes(event));b=run(candidate,'nrf_ble_gatt_on_ble_evt',(EVT,CTX),bytes(seed),bytes(event));assert a[1]==b[1];assert a[2]==[(144,1,[desired,desired,0,0])];assert b[2]==(a[2] if desired>effective else [])
            counterexamples.append(dict(desired=desired,effective=effective,stock_svc_calls=a[2],upstream_svc_calls=b[2],equivalent=a==b))
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),selected_object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,context_initial_zero_bytes_compared=36,native_startup_init_args=[hex(v) for v in native_init[0]],observer_counterexamples=counterexamples,observer_contract_proven=False,scope='Unchanged pinned SDK init/link-init: all fill bytes and random padded contexts, arbitrary callback bits, nulls, mapped aligned link offsets, exact writes/guards and preserved registers/stack',limitations=['Three-link aggregate is proven; inherited peripheral/central split is not established by this contract.','Full SDK observer is used only as an unselected diagnostic candidate: product connected path unconditionally sends SVC144 while SDK is conditional.','Observer counterexamples use successful controlled SVC replies and do not validate logging, all event branches, live SoftDevice or hardware behavior.','No original compiler identity, instruction identity, complete startup or whole-image linking is claimed.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} GATT init/link comparisons passed; {sum(not c["equivalent"] for c in counterexamples)} observer counterexamples retained')
if __name__=='__main__':main()

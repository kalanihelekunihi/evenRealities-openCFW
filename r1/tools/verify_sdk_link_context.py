#!/usr/bin/env python3
"""Stock-versus-unmodified SDK link-context lookup with scripted connection index."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ_UNMAPPED,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
STORAGE=0x20001000;OUT=0x20001100;POOL=0x20002000
def main():
    real_index='--real-index' in sys.argv
    receipt=BASE/('sdk-link-context/index-integration-verification.json' if real_index else 'sdk-link-context/verification.json');receipt.unlink(missing_ok=True);report_path=BASE/'sdk-link-context/report.json';report=json.loads(report_path.read_text());obj=BASE/'sdk-link-context/blcm_link_ctx_get.o';assert sha(obj)==report['units'][0]['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    if real_index:
        index_report=BASE/'sdk-connection-index/report.json';index_obj=BASE/'sdk-connection-index/connection-index-only.o';assert sha(index_obj)==json.loads(index_report.read_text())['selected_object_sha256']
    counts=dict(core=0,nulls=0,aliases=0,mutations=0,faults=0)
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.m_bcs 0x2002bdb0 (NOLOAD) : { *(.bss.m_bcs) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=blcm_link_ctx_get','--gc-sections',*([str(index_obj)] if real_index else ['--defsym=ble_conn_state_conn_idx=0x100e001']),str(obj),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());states={};faults={}
        def hook(uc,address,size,user):
            if address not in (0x51e04,syms['ble_conn_state_conn_idx'] if real_index else 0x100e000):return
            f=states[id(uc)];f['events'].append(('index',uc.reg_read(UC_ARM_REG_R0)))
            if f['mutation']:
                pool,maximum,stride=f['mutation'];uc.mem_write(STORAGE,struct.pack('<IBxH',pool,maximum,stride))
            if real_index:return
            uc.reg_write(UC_ARM_REG_R0,f['index']);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def fault(uc,access,address,size,value,user):faults[id(uc)].append((access,address,size));return False
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def run(uc,pool=POOL,maximum=20,stride=4,index=0,connection=0,storage=STORAGE,output=OUT,mutation=None,valid_flags=0x000fffff):
            uc.mem_write(STORAGE,struct.pack('<IBBH',pool,maximum,0xa5,stride)+bytes([0x5a])*8);uc.mem_write(OUT,struct.pack('<I',0xdeadbeef));states[id(uc)]=dict(events=[],index=index,mutation=mutation);faults[id(uc)]=[]
            if real_index:uc.mem_write(0x2002bdb4,struct.pack('<I',valid_flags))
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(storage,connection,output)):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            try:uc.emu_start((0x514e0 if uc is stock else syms['blcm_link_ctx_get'])|1,0x20000100,count=10000)
            except UcError:assert faults[id(uc)]
            else:
                assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
                assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            return None if faults[id(uc)] else uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(OUT,4)),bytes(uc.mem_read(STORAGE,16)),list(states[id(uc)]['events']),list(faults[id(uc)])
        def compare(**case):
            a=run(stock,**case);b=run(candidate,**case);assert a==b,(case,a,b);return a
        for pool,maximum,stride,index in itertools.product((0,POOL,0xfffffffc),(0,1,19,20,21,255),(0,1,2,3,4,8,0xfffc,0xffff),range(256)):
            connection=index if real_index else 0x12345678;result=compare(pool=pool,maximum=maximum,stride=stride,index=index,connection=connection);effective=index if not real_index or index<20 else 20;expected=14 if not pool else 7 if stride%4 else 5 if effective==20 else 4 if effective>=maximum else 0;assert result[0]==expected
            assert result[1]==struct.pack('<I',0 if expected else (pool+effective*stride)&0xffffffff)
            assert result[3]==([] if not pool or stride%4 else [('index',connection)]);counts['core']+=1
        for storage,output,index in itertools.product((0,STORAGE),(0,OUT),(0,19,20,255)):
            a=compare(storage=storage,output=output,index=index,connection=index if real_index else 0);assert a[0]==(14 if not storage or not output else 0 if index<20 else 5 if real_index or index==20 else 4);counts['nulls']+=1
        for output,maximum,stride,index in itertools.product((STORAGE,STORAGE+4,STORAGE+8),(0,1,20,255),(0,4,0xfffc),(0,1,20,255)):
            compare(output=output,maximum=maximum,stride=stride,index=index,connection=index if real_index else 0);counts['aliases']+=1
        for mutation,index,connection in itertools.product(((0,20,3),(POOL+32,0,4),(POOL+32,255,3),(0xfffffffc,255,0xffff)),(0,1,19,20,255,0x100,0x114,0xffffff01),(0,0xffff,0x10000,0xffffffff)):
            compare(mutation=mutation,index=index,connection=connection);counts['mutations']+=1
        for case in (dict(storage=0x20040000),dict(output=0x20040000)):
            assert compare(**case)[4];counts['faults']+=1
        if real_index:
            for handle,bits in itertools.product((*range(33),0xffff,0x10000,0xffffffff),(0,1,0x80000,0x000fffff,0xffffffff)):
                compare(connection=handle,valid_flags=bits);counts['core']+=1
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),object_sha256=sha(obj),actual_connection_index_executed=real_index,index_report_sha256=sha(index_report) if real_index else None,comparisons=sum(counts.values()),comparisons_by_kind=counts,scope='Unchanged pinned Nordic lookup; output clearing/null order, descriptor field offsets, word alignment, 20-index sentinel, low-byte index truncation, capacity, 32-bit address arithmetic, output/descriptor aliasing, callback mutation and full register arguments, saved registers/stack',limitations=[('Actual connection-index/validity/flag-read C bodies execute without provider interceptions; validity bitmap and storage are fixtures, with other registry/configuration/concurrency behavior open.' if real_index else 'ble_conn_state_conn_idx is intercepted; actual connection registry/configuration and concurrency remain open.'),'Descriptor fixtures are fully mapped eight-byte records. Original byte-versus-halfword alignment-check fault granularity is not established for partially mapped records.','Pointer arithmetic outside allocated C objects is observed for this pinned compiled target only; this is not a portable-C guarantee.','Physical BLE behavior, exact compiler output and whole-image linking remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} SDK link-context comparisons passed')
if __name__=='__main__':main()

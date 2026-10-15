#!/usr/bin/env python3
"""Stock differential for unchanged Nordic connection reads and reset/init."""
import hashlib,itertools,json,random,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
STATE=0x2002bdb0;FLAGS=0x20003000
ENTRIES={'ble_conn_state_conn_idx':0x51e04,'ble_conn_state_valid':0x51fa4,'nrf_atflags_get':0x7803e,'bcs_internal_state_reset':0x51440,'ble_conn_state_init':0x51e78}
def main():
    events_provider='--events-provider' in sys.argv
    receipt=BASE/('sdk-connection-events/index-verification.json' if events_provider else 'sdk-connection-index/verification.json');receipt.unlink(missing_ok=True);report_path=BASE/('sdk-connection-events/report.json' if events_provider else 'sdk-connection-index/report.json');report=json.loads(report_path.read_text());obj=BASE/('sdk-connection-events/connection-events.o' if events_provider else 'sdk-connection-index/connection-index-only.o');assert sha(obj)==report['selected_object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    memory_report=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(memory_report.read_text())['relocatable_sha256']
    counts={name:0 for name in ENTRIES};fault_count=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.m_bcs 0x2002bdb0 (NOLOAD) : { *(.bss.m_bcs) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=ble_conn_state_conn_idx',str(obj),str(memory),*(['--defsym=r1_adc_error=0x100e001'] if events_provider else []),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:(int(r.split()[0],16),int(r.split()[1],16)) for r in subprocess.check_output(['arm-none-eabi-nm','-S',str(elf)],text=True).splitlines() if len(r.split())==4};assert syms['m_bcs']==(STATE,124)
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(STATE,124))==bytes(candidate.mem_read(STATE,124))==bytes(124)
        faults={id(uc):[] for uc in (stock,candidate)}
        def fault(uc,access,address,size,value,user):faults[id(uc)].append((access,address,size));return False
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        state_seed=bytes((i*37+5)&255 for i in range(124));array_seed=bytes((i*71+19)&255 for i in range(516))
        def run(uc,name,args,bits,fill=None):
            uc.mem_write(STATE-4,b'LEFT');uc.mem_write(STATE+124,b'RGHT');uc.mem_write(STATE,state_seed if fill is None else fill);uc.mem_write(STATE+4,struct.pack('<I',bits));uc.mem_write(FLAGS,array_seed);before=bytes(uc.mem_read(STATE,124));faults[id(uc)].clear()
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            try:uc.emu_start((ENTRIES[name] if uc is stock else syms[name][0])|1,0x20000100,count=10000)
            except UcError:assert faults[id(uc)]
            else:
                assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
                assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            assert bytes(uc.mem_read(STATE-4,4))==b'LEFT' and bytes(uc.mem_read(STATE+124,4))==b'RGHT'
            assert bytes(uc.mem_read(STATE,124))==(bytes(124) if name in ('bcs_internal_state_reset','ble_conn_state_init') else before) and bytes(uc.mem_read(FLAGS,516))==array_seed
            return None if faults[id(uc)] or name in ('bcs_internal_state_reset','ble_conn_state_init') else uc.reg_read(UC_ARM_REG_R0),list(faults[id(uc)])
        def compare(name,args,bits,fill=None):
            a=run(stock,name,args,bits,fill);b=run(candidate,name,args,bits,fill);assert a==b,(name,args,bits,a,b);counts[name]+=1;return a
        for name in ('ble_conn_state_valid','ble_conn_state_conn_idx'):
            for handle in range(65536):
                a=compare(name,(handle,),0xa5a5a5a5);valid=handle<20 and bool(0xa5a5a5a5&(1<<handle));assert a[0]==(handle if valid else 20) if name.endswith('idx') else a[0]==int(valid)
            rng=random.Random(0x51fa4);patterns=[0,0xffffffff,*[1<<i for i in range(32)],*[0xffffffff^(1<<i) for i in range(32)],*[rng.getrandbits(32) for _ in range(64)]]
            for handle,bits in itertools.product((*range(33),0xffff,0x10000,0x80000000,0xffffffff),patterns):
                a=compare(name,(handle,),bits);valid=handle<20 and bool(bits&(1<<handle));assert a[0]==(handle if valid else 20) if name.endswith('idx') else a[0]==int(valid)
        for alignment,index in itertools.product(range(4),range(4096)):
            a=compare('nrf_atflags_get',(FLAGS+alignment,index),0);offset=alignment+(index//32)*4;word=struct.unpack_from('<I',array_seed,offset)[0];assert a[0]==int(bool(word&(1<<(index%32))))
        for pointer,index in itertools.product((0,0x20040000),(0,31,32,0xffffffff)):
            assert compare('nrf_atflags_get',(pointer,index),0)[1];fault_count+=1
        for name,fill_byte in itertools.product(('bcs_internal_state_reset','ble_conn_state_init'),range(256)):
            compare(name,(),(fill_byte*0x01010101)&0xffffffff,bytes([fill_byte])*124)
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),selected_object_sha256=sha(obj),events_provider=events_provider,memory_report_sha256=sha(memory_report),comparisons=sum(counts.values()),authenticated_native_reset_bytes=124,comparisons_by_entry=counts,unmapped_read_faults=fault_count,candidate_state_initial_zero_bytes_compared=124,valid_flags_address='0x2002bdb4',scope='No provider interceptions: actual unchanged Nordic index/validity/bit-read/reset/init bodies and source memory; all uint16 handles, walking/complement/random validity flags, wide register arguments, 4096-bit mapped arrays, state/array immutability and preserved registers/stack',limitations=['The native reset independently authenticates a 124-byte clear span and state base; this matches SDK size but does not establish every field meaning, all writers or live registry ownership.','Unaligned/raw register/out-of-object cases describe this pinned compiled target, not portable C or public API guarantees.','Other connection registry operations, live event ownership, concurrency, original instructions, whole-image and physical behavior remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} connection-index/validity/flag comparisons passed; {fault_count} faults')
if __name__=='__main__':main()

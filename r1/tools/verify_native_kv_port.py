#!/usr/bin/env python3
"""Native KV port cold table, binder and callback adapters against C."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PORT_SLOT=0x20006974;MUTEX=0x20006978;STORAGE=0x2000697c;RECORD=0x20006984;CURSOR=0x20019e49;OUTPUT=0x20003000;DEVICE=0x20003100
ENTRIES={'r1_kv_port_bind':0x73924,'r1_kv_port_lock':0x95138,'r1_kv_port_unlock':0x95150,'r1_kv_port_control':0x94df4,'r1_kv_port_zero_4':0x94e2c,'r1_kv_port_zero_8':0x95164,'r1_kv_port_zero_12':0x94df0}
TABLE=(('r1_kv_port_initialize',0x94e3c),('r1_kv_port_zero_4',0x94e2c),('r1_kv_port_zero_8',0x95164),('r1_kv_port_zero_12',0x94df0),('r1_kv_store_get',0x95168),('r1_kv_store_put',0x95304),('r1_kv_port_control',0x94df4),('r1_kv_port_lock',0x95138),('r1_kv_port_unlock',0x95150))
def main():
    out=BASE/'native-kv-port';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'native_kv_port.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
    for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';counts={n:0 for n in ENTRIES};states={};os_calls={}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';data=tmp/'record.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.kv.port_slot 0x20006974 (NOLOAD) : { *(.r1.kv.port_slot) } .r1.kv.mutex 0x20006978 (NOLOAD) : { *(.r1.kv.mutex) } .r1.kv.port_record 0x20006984 : { *(.r1.kv.port_record) } .r1.kv.block_cursor 0x20019e49 (NOLOAD) : { *(.r1.kv.block_cursor) } /DISCARD/ : { *(.comment) *(.note*) } }')
        bindings={'r1_kv_storage_context':STORAGE,'osMutexAcquire':0x100e001,'osMutexRelease':0x100e011,'r1_kv_port_initialize':0x100ed001,'r1_kv_store_get':0x100ed011,'r1_kv_store_put':0x100ed021};subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=r1_kv_port_bind',*['--defsym='+n+'='+hex(v) for n,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.kv.port_record='+str(data),str(elf)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_kv_native_port_record']==RECORD
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);os_calls[id(uc)]=0
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());candidate.mem_write(RECORD,data.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        for p,size in ((PORT_SLOT,4),(MUTEX,4),(CURSOR,1)):assert bytes(stock.mem_read(p,size))==bytes(candidate.mem_read(p,size))==bytes(size)
        assert struct.unpack('<9I',bytes(stock.mem_read(RECORD,36)))==tuple(a|1 for n,a in TABLE);assert struct.unpack('<9I',data.read_bytes())==tuple(syms[n]|1 for n,a in TABLE);initial_tables={id(uc):bytes(uc.mem_read(RECORD,36)) for uc in (stock,candidate)}
        def hook(uc,address,size,user):
            if address not in (0x7d488,0x7d536,0x100e000,0x100e010):return
            f=states[id(uc)];kind='acquire' if address in (0x7d488,0x100e000) else 'release';args=(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if kind=='acquire' else (uc.reg_read(UC_ARM_REG_R0),);f['trace'].append((kind,args,f['status']));os_calls[id(uc)]+=1
            if f['mutation']:uc.mem_write(MUTEX,struct.pack('<I',0x12345678))
            uc.reg_write(UC_ARM_REG_R0,f['status']);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def run(uc,name,args,mutex,cursor,storage,word,status,mutation):
            uc.mem_write(PORT_SLOT,struct.pack('<I',0x12345678));uc.mem_write(MUTEX,struct.pack('<I',mutex));uc.mem_write(STORAGE,struct.pack('<I',storage));uc.mem_write(CURSOR-1,b'X'+bytes([cursor])+b'Y');uc.mem_write(OUTPUT-4,b'LEFT');uc.mem_write(OUTPUT,b'\xa5'*12);uc.mem_write(OUTPUT+12,b'RGHT');uc.mem_write(DEVICE,struct.pack('<I',word));states[id(uc)]=dict(trace=[],status=status,mutation=mutation)
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1),args):uc.reg_write(reg,value)
            for i,reg in enumerate(saved):uc.reg_write(reg,0x12345600+i)
            uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000 and [uc.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
            assert bytes(uc.mem_read(CURSOR-1,1))==b'X' and bytes(uc.mem_read(CURSOR+1,1))==b'Y' and bytes(uc.mem_read(OUTPUT-4,4))==b'LEFT' and bytes(uc.mem_read(OUTPUT+12,4))==b'RGHT' and bytes(uc.mem_read(RECORD,36))==initial_tables[id(uc)]
            return None if name in ('r1_kv_port_bind','r1_kv_port_lock','r1_kv_port_unlock') else uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(PORT_SLOT,4)),bytes(uc.mem_read(MUTEX,4)),uc.mem_read(CURSOR,1)[0],bytes(uc.mem_read(OUTPUT,12)),list(states[id(uc)]['trace'])
        def compare(name,args=(),mutex=0,cursor=0,storage=0,word=0,status=0,mutation=False):
            a=run(stock,name,args,mutex,cursor,storage,word,status,mutation);b=run(candidate,name,args,mutex,cursor,storage,word,status,mutation);assert a==b,(name,args,mutex,cursor,storage,word,status,mutation,a,b);counts[name]+=1;return a
        for destination in (OUTPUT,OUTPUT+4,PORT_SLOT):a=compare('r1_kv_port_bind',(destination,));assert a[1]==struct.pack('<I',RECORD) if destination==PORT_SLOT else struct.unpack_from('<I',a[4],destination-OUTPUT)[0]==RECORD
        for name,mutex,status,mutation in itertools.product(('r1_kv_port_lock','r1_kv_port_unlock'),(0,1,0x20001000,0xffffffff),(0,8,0xffffffff),(False,True)):
            a=compare(name,mutex=mutex,status=status,mutation=mutation);assert len(a[5])==int(mutex!=0)
        for operation,cursor,storage,word,pointer in itertools.product((*range(256),0x10001,0xffffffff),range(256),(0,DEVICE),(0,0x12345678,0xffffffff),(0,OUTPUT)):
            a=compare('r1_kv_port_control',(operation,pointer),cursor=cursor,storage=storage,word=word);assert a[0]==(1 if operation==3 and not pointer else 0);assert a[3]==((cursor+1)&255 if operation==1 else cursor)
            if operation==3 and pointer:assert struct.unpack_from('<I',a[4])[0]==(word if storage else 0xa5a5a5a5)
        for name in ('r1_kv_port_zero_4','r1_kv_port_zero_8','r1_kv_port_zero_12'):
            for value in range(256):assert compare(name,(value,0xffffffff))[0]==0
    assert os_calls[id(stock)]==os_calls[id(candidate)]
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,os_mutex_calls=os_calls[id(candidate)],port_record_bytes_pointer_normalized=36,initial_zero_bytes_compared=9,scope='Native port binder/table, null-guarded mutex adapters and full-word control/zero callbacks; source C and typed data, counter wraps, source/null-output handling, CMSIS args/ignored return boundaries and guarded state/registers/stack',limitations=['Initializer/get/put table entries remain unresolved production providers and are test-only bindings in this executable.','CMSIS acquire/release replies are controlled; actual scheduler locking, backend pointer/initialization and flash persistence remain unresolved.','Only mapped valid pointers and bounded control output are claimed; full allocations/writers, byte identity and hardware remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} KV port comparisons passed; {os_calls[id(candidate)]} CMSIS mutex calls')
if __name__=='__main__':main()

#!/usr/bin/env python3
"""Actual SDK registry events and atomic writers versus locked stock execution."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
STATE=0x2002bdb0;EVENT=0x20002000;WORDS=0x20003000
ENTRIES={'r1_sdk_connection_event':0x5380c,'conn_handle_list_get':0x59ba0,'nrf_atflags_set':0x78054,'nrf_atflags_clear':0x77fbe,'nrf_atomic_u32_and':0x78086,'nrf_atomic_u32_or':0x780ba}
def main():
    receipt=BASE/'sdk-connection-events/verification.json';receipt.unlink(missing_ok=True);report_path=BASE/'sdk-connection-events/report.json';report=json.loads(report_path.read_text());obj=BASE/'sdk-connection-events/connection-events.o';assert sha(obj)==report['selected_object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    memory_report=BASE/'runtime/report.json';memory=BASE/'runtime/memory-runtime.o';assert sha(memory)==json.loads(memory_report.read_text())['relocatable_sha256']
    counts=dict(events=0,sequences=0,list=0,flag_writes=0,atomics=0,retries=0);retry_observations=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.m_bcs 0x2002bdb0 (NOLOAD) : { *(.bss.m_bcs) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections',*['--undefined='+n for n in ENTRIES],'--defsym=r1_adc_error=0x100e001',str(obj),str(memory),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3};assert syms['m_bcs']==STATE
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());states={};writes={}
        registers=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC]
        def hook(uc,address,size,user):
            f=states[id(uc)]
            if address in (0x4e5bc,0x100e000):f['errors'].append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,0x87654321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if size!=4 or not f['fail']:return
            first,second=struct.unpack('<HH',bytes(uc.mem_read(address,4)))
            if first&0xfff0!=0xe840:return
            target=(uc.reg_read(registers[first&15])+4*(second&255))&0xffffffff
            if not (STATE<=target<STATE+124 or WORDS<=target<WORDS+512):return
            old=struct.unpack('<I',bytes(uc.mem_read(target,4)))[0];uc.mem_write(target,struct.pack('<I',old^0x40000000));uc.reg_write(registers[(second>>8)&15],1);uc.reg_write(UC_ARM_REG_PC,(address+4)|1);f['fail']-=1;f['retries']+=1
        def write(uc,access,address,size,value,user):
            if STATE<=address<STATE+124:writes[id(uc)].append((address-STATE,size,value))
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_WRITE,write)
        saved=registers[4:12]
        def call(uc,name,args,fail=0):
            states[id(uc)]=dict(errors=[],fail=fail,retries=0);writes[id(uc)]=[];uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for r,v in zip(registers,args):uc.reg_write(r,v)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            uc.emu_start((ENTRIES[name] if uc is stock else syms[name])|1,0x20000100,count=2000000)
            assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
            assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            value=uc.reg_read(UC_ARM_REG_R0) if name.startswith('nrf_atomic_') else None
            return value,bytes(uc.mem_read(STATE,124)),list(writes[id(uc)]),list(states[id(uc)]['errors']),states[id(uc)]['retries']
        def model(words,event,handle,role,security,auth_status,auth_bits):
            result=list(words);errors=[]
            def setflag(group,on):
                word=group+handle//32;mask=1<<(handle%32)
                result[word]=(result[word]|mask) if on else result[word]&~mask&0xffffffff
            if event==16:
                stale=result[1]&~result[2]&0xfffff
                for h in range(20):
                    if stale&(1<<h):
                        for group in range(1,31):result[group]&=~(1<<h)&0xffffffff
                if handle>=20:errors.append(4)
                else:
                    setflag(2,True);setflag(1,True)
                    if role==2:setflag(3,True)
            elif event==17:setflag(2,False)
            elif event==26:
                level=security>>4
                for group,threshold in ((6,4),(5,3),(4,2)):setflag(group,level>=threshold)
            elif event==25 and auth_status==0:setflag(6,bool(auth_bits&8))
            return struct.pack('<31I',*result),errors
        def event_case(words,event=16,handle=0,role=1,security=0,auth_status=0,auth_bits=0,fail=0):
            raw=bytearray([0xa5]*64);struct.pack_into('<HHH',raw,0,event,64,handle);raw[15]=role
            if event==26:raw[8]=security
            if event==25:raw[8]=auth_status;raw[9]=auth_bits
            results=[]
            for uc in (stock,candidate):uc.mem_write(STATE,struct.pack('<31I',*words));uc.mem_write(EVENT,bytes(raw));results.append(call(uc,'r1_sdk_connection_event',(EVENT,0x12345678),fail))
            assert results[0]==results[1],(event,handle,role,security,auth_status,auth_bits,results)
            if not fail:
                expected,errors=model(words,event,handle,role,security,auth_status,auth_bits);assert results[0][1]==expected and results[0][3]==errors
            return results[0]
        rng=random.Random(0x5380c);patterns=[[0]*31,[0xffffffff]*31,[(1<<20)-1]*31,*[[rng.getrandbits(32) for _ in range(31)] for _ in range(8)]]
        for words,handle,role in itertools.product(patterns,(*range(20),20,31,32,0xffff),(0,1,2,255)):event_case(words,handle=handle,role=role);counts['events']+=1
        for words,handle in itertools.product(patterns,range(64)):event_case(words,event=17,handle=handle);counts['events']+=1
        for handle,security in itertools.product((*range(20),20,31,32,63),range(256)):event_case(patterns[3],event=26,handle=handle,security=security);counts['events']+=1
        for handle,status,bits in itertools.product((0,1,19,20,31,32,63),(0,1,255),range(256)):event_case(patterns[4],event=25,handle=handle,auth_status=status,auth_bits=bits);counts['events']+=1
        for event in (0,1,15,18,24,27,0xffff):event_case(patterns[5],event=event);counts['events']+=1
        for _ in range(128):
            words=list(patterns[3])
            for event,handle,role in ((16,0,2),(17,0,1),(16,1,1),(26,1,1),(25,1,1)):
                result=event_case(words,event=event,handle=handle,role=role,security=rng.randrange(256),auth_bits=rng.randrange(256));words=list(struct.unpack('<31I',result[1]));counts['sequences']+=1
        for flags in (0,1,0xfffff,0xffffffff,*[rng.getrandbits(32) for _ in range(128)]):
            lists=[]
            for uc in (stock,candidate):
                uc.mem_write(WORDS,bytes([0xa5])*44);call(uc,'conn_handle_list_get',(WORDS,flags));raw=bytes(uc.mem_read(WORDS,44));length=struct.unpack_from('<I',raw)[0];lists.append((length,struct.unpack_from('<'+str(length)+'H',raw,4)))
            expected=tuple(i for i in range(20) if flags&(1<<i));assert lists[0]==lists[1]==(len(expected),expected);counts['list']+=1
        for name,index,fail in itertools.product(('nrf_atflags_set','nrf_atflags_clear'),range(128),(0,1,2)):
            before=bytes(rng.randrange(256) for _ in range(512));outputs=[]
            for uc in (stock,candidate):uc.mem_write(WORDS,before);result=call(uc,name,(WORDS,index),fail);outputs.append((bytes(uc.mem_read(WORDS,512)),result[4]))
            assert outputs[0]==outputs[1];expected=bytearray(before);offset=(index//32)*4;word=struct.unpack_from('<I',expected,offset)[0]^(0x40000000 if fail%2 else 0);mask=1<<(index%32);struct.pack_into('<I',expected,offset,word|mask if name.endswith('set') else word&~mask&0xffffffff);assert outputs[0]==(bytes(expected),fail);counts['flag_writes']+=1;retry_observations+=fail
        for name,old,operand,fail in itertools.product(('nrf_atomic_u32_and','nrf_atomic_u32_or'),(0,1,0x80000000,0xffffffff,0x55aa55aa),(0,1,0x80000000,0xffffffff,0xaa55aa55),(0,1,2)):
            results=[]
            for uc in (stock,candidate):uc.mem_write(WORDS,struct.pack('<I',old));result=call(uc,name,(WORDS,operand),fail);results.append((result[0],bytes(uc.mem_read(WORDS,4)),result[4]))
            initial=old^(0x40000000 if fail%2 else 0);expected=initial&operand if name.endswith('and') else initial|operand;assert results[0]==results[1]==(expected,struct.pack('<I',expected),fail);counts['atomics']+=1;retry_observations+=fail
        for event,handle,fail in itertools.product((16,17,25,26),(0,1,19),(1,2)):
            result=event_case(patterns[3],event=event,handle=handle,role=2,security=0x40,auth_bits=8,fail=fail);assert result[4]==fail;retry_observations+=fail;counts['retries']+=1
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),selected_object_sha256=sha(obj),memory_report_sha256=sha(memory_report),comparisons=sum(counts.values()),comparisons_by_kind=counts,injected_failed_store_exclusives=retry_observations,scope='Actual unchanged SDK event/list/flag/atomic writers and memory; entire 124-byte registry plus write order, stale-record purge, CONNECTED role/range error policy, DISCONNECTED, security-level/auth flags, ordered sequences, lists and deterministic exclusive retry/interference',limitations=['Only the returning R1 error logger is intercepted in event execution. Event structures are fixtures; BLE observer routing and live stack delivery remain unproven.','Store-exclusive failures are deterministic instruction-hook injections, not hardware concurrency proof.','Unused/uninitialized list tail bytes are excluded; only length and initialized handles are compared.','Invalid/partial event pointers and accesses beyond the tested mapped ranges are outside this contract; original compiler output and whole-image/hardware proof remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} registry event/writer comparisons passed; {retry_observations} forced exclusive failures')
if __name__=='__main__':main()

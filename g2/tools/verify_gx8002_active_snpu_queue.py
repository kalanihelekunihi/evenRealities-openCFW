# SPDX-License-Identifier: MIT
"""Feed actual callback record words to authenticated decoded upstream FIFO."""
import json,subprocess,itertools
from verify_gx8002_active_snpu import verify as qualify,execute,ROOT,Elf32,sha,decode
from execute_gx8002_active_queue import execute as put
from compare_gx8002_tws import execute as initialize,expected as init_expected

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-source-candidate/queue_put/queue-size.o';elf=Elf32(path.read_bytes(),'put')
    report=json.loads((ROOT/'docs/research/gx8002-queue-put-comparison.json').read_text());section=next(s for s in elf.sections if s['name']=='.sram_text');assert sha(elf.contents(section))==report['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');queue=decode(subprocess.check_output([pre,'-dr','--section=.sram_text',str(path)],text=True));callback=decode((ROOT/'build/gx8002-board/active-snpu.disassembly.txt').read_text());cases=0;accepted=0;rejected=0
    init_path=ROOT/'build/gx8002-source-candidate/tws/tws.elf';init_elf=Elf32(init_path.read_bytes(),'tws');init_report=json.loads((ROOT/'docs/research/gx8002-tws-verification.json').read_text())
    for row in init_report['functions']:
        sec=next(s for s in init_elf.sections if s['name']==row['section_name']);assert sha(init_elf.contents(sec))==row['compiled_sha256']
    init_code=decode(subprocess.check_output([pre,'-d',str(init_path)],text=True))
    observed=initialize(init_code,0x10208670,0,0,0,0,91);assert observed==init_expected(0,0,0)
    queue_address,buffer_address,queue_bytes,record_bytes=observed['trace'][0][2]
    assert (queue_address,buffer_address,queue_bytes,record_bytes)==(0x2002e6ec,0x2002e700,56,8)
    for slots,head_slot,tail_slot,module,private in itertools.product((queue_bytes//record_bytes,),range(7),range(7),(0,256,0xffffffff),(0,0x20030000)):
        size=slots*8;head=head_slot*8;tail=tail_slot*8;outcomes=[]
        def enqueue(address,record):
            assert address==0x2002e6ec and record==(module,private)
            # Actual callback queue and stack addresses; buffer and capacity come from decoded TWS initialization.
            memory={buffer_address+i:(i*73+19)&255 for i in range(size)}
            for base,words in ((0x2002e6ec,(tail,head,buffer_address,size,8)),(0x2006fff4,record)):
                for n,value in enumerate(words):
                    for i in range(4):memory[base+4*n+i]=(value>>(8*i))&255
            before=memory.copy();result,trace=put(queue,memory,0,address,0x2006fff4);wanted=before.copy();full=(tail+8)%size==head
            if not full:
                for i in range(8):wanted[buffer_address+(tail+i)%size]=before[0x2006fff4+i]
                for i in range(4):wanted[0x2002e6ec+i]=(((tail+8)%size)>>(8*i))&255
            assert memory==wanted and result==int(not full);outcomes.append(result);return result
        assert execute(callback,0x10026340,module,1,private,0,91,queue_hook=enqueue)==(0,[('put',0x2002e6ec,(module,private))])
        assert len(outcomes)==1;accepted+=outcomes[0];rejected+=1-outcomes[0];cases+=1
    assert accepted and rejected
    return {'evidence':evidence,'cases':cases,'accepted':accepted,'rejected':rejected,'queue_object_sha256':sha(path.read_bytes()),'tws_elf_sha256':sha(init_path.read_bytes()),'initialization':observed,'executor_sha256':sha((ROOT/'tools/execute_gx8002_active_queue.py').read_bytes()),'source_admitted':False,'limits':['Actual callback payload feeds decoded source queue at actual queue and callback stack addresses with buffer/capacity observed from decoded TWS initialization. Independent complete memory oracle checks queue wrap/full behavior. Queue lifecycle and shared literal placement remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-active-snpu-queue.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['accepted'],r['rejected'])

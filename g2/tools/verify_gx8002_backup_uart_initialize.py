# SPDX-License-Identifier: MIT
"""Verify backup initializer using the established shared instruction model."""
import json,subprocess
from itertools import product
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_initialize import execute


def verify():
    report=json.loads((ROOT/'docs/research/gx8002-backup-uart-initialize.json').read_text())
    path=ROOT/'build/gx8002-backup-uart-initialize/initialize.elf';assert sha(path.read_bytes())==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3ce5c','--stop-address=0x3cec4',str(wrapper)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    clocks={0,1,0xffffffff}
    clocks.update(base+off for base in (0,1000000,24000000,4294000000) for off in (0,99,100,101,999899,999900,999901,999999) if base+off<=0xffffffff)
    targets={0x3c528:'gate',0x3c630:'frequency',0x3cce4:'configure'};delta=0x10003000-0x3b940;count=0
    for port,baud,clock,status in product((0,1,2,0x7fffffff,0x80000000,0xffffffff),(0,115200,0xffffffff),sorted(clocks),(0,7,0xffffffff)):
        remainder=clock%1000000
        rounded=clock-remainder if remainder<=100 else clock+1000000-remainder if remainder>=999900 else clock
        ptr=0x20016b84+port*128
        expected=(0xffffffff,[]) if port>=2 else (status,[('gate',17+port,1),('frequency',16),('write',ptr+12,rounded&0xffffffff),('write',ptr+16,baud),('configure',ptr)])
        assert execute(old,0x3ce5c,port,baud,clock,status,targets)==expected
        assert execute(new,0x1000451c,port,baud,clock,status,{k+delta:v for k,v in targets.items()})==expected
        count+=1
    result={'elf_sha256':report['elf_sha256'],'stock_sha256':IMAGE_SHA,'cases':count,'clock_values':sorted(clocks),'source_admitted':False,'limits':['Decoded stock/source with modeled gate, frequency and configure calls; verifies invalid-port early return, ordered state writes, MHz rounding boundaries and result propagation.','Does not execute helper implementations or physical hardware. Integration and reference qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-uart-initialize-execution.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['cases'])

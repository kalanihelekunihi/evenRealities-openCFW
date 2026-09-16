# SPDX-License-Identifier: MIT
"""Build and compare the complete shared FIFO-depth source for backup UART."""
import json,subprocess
from itertools import product
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_fifo_depth import execute


def build():
    out=ROOT/'build/gx8002-backup-uart-fifo';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_uart_fifo_depth.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'fifo.o'
    command=[pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(obj)];subprocess.run(command,check=True)
    ld=out/'fifo.ld';ld.write_text('SECTIONS { .text 0x1000433c : { *(.text*) } }\n')
    path=out/'fifo.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'fifo');sec=next(s for s in elf.sections if s['name']=='.text')
    assert sec['size']<=104 and sec['address']==0x1000433c
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';oldelf=Elf32(wrapper.read_bytes(),'stock')
    assert oldelf.contents(next(s for s in oldelf.sections if s['name']=='.data'))==stock
    text=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'fifo.disassembly.txt').write_text(text)
    new=decode(text);old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x3cc7c','--stop-address=0x3cce4',str(wrapper)],text=True))
    expected={1:16,2:32,4:64,8:128,16:256,32:512,64:1024,128:2048};count=0
    for encoding,other,port in product(range(256),(0,0xff00ffff,0xa5001234),(0,1)):
        device=0xa0100000+port*0x100000;descriptor=0x20016b84+port*128;parameter=(encoding<<16)|other
        wanted=(expected.get(encoding,0),[(descriptor+4,device),(device+0xf4,parameter)])
        assert execute(old,0x3cc7c,device,parameter,descriptor)==wanted
        assert execute(new,0x1000433c,device,parameter,descriptor)==wanted
        count+=1
    result={'source_sha256':sha(src.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_sha256':IMAGE_SHA,'code_bytes':sec['size'],'stock_envelope_bytes':104,'decoded_cases':count,'source_admitted':False,'limits':['All 256 field encodings with unrelated-bit patterns and both descriptor/device addresses; verifies ordered reads, value mapping and ABI.','Physical device parameter values, references and integration pending. No undefined code dependencies.']}
    (ROOT/'docs/research/gx8002-backup-uart-fifo.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['code_bytes'],r['decoded_cases'],r['elf_sha256'])

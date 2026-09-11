# SPDX-License-Identifier: MIT
import json,subprocess
from verify_gx8002_dma_configure import verify as configure,ROOT,decode
from verify_gx8002_dma_clear import verify as clear_verify,execute as clear_execute
from verify_gx8002_dma_bus_address import verify as bus_verify,execute as bus_execute

def verify():
    clear=clear_verify();bus=bus_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcd90','--stop-address=0xd200',str(stock)],text=True))
    new_clear=decode((ROOT/'build/gx8002-dma-clear/clear.disassembly.txt').read_text())
    new_bus=decode((ROOT/'build/gx8002-dma-bus-address/bus_address.disassembly.txt').read_text());counts={'clear':0,'bus':0}
    def clear_hook(channel):
        wanted=[('read',0x2002e93c,0xa1000000)]+[('write',0xa1000000+o,1<<channel) for o in (0x338,0x340,0x348,0x350,0x358)]
        for source in (False,True):
            result=clear_execute(new_clear if source else old,0x10203804 if source else 0xcd90,channel,0xa1000000)
            if result!=wanted:raise ValueError('Configuration clear effects')
            counts['clear']+=1
    def bus_hook(address):
        wanted=address&0xfffffff if 0x10000000<=address<0x30000000 else address
        for source in (False,True):
            result=bus_execute(new_bus if source else old,0x10203c60 if source else 0xd1ec,address)
            if result!=wanted:raise ValueError('Configuration bus result')
            counts['bus']+=1
        return wanted
    configuration=configure(clear_hook=clear_hook,bus_hook=bus_hook)
    return {'configuration':configuration,'clear_dependency':clear,'bus_dependency':bus,'decoded_leaf_calls':counts,'source_admitted':False,'hardware_qualified':False,'limits':['Separate leaf execution frames; clear effects checked against fixed device base rather than shared MMIO. Descriptor builder still modeled.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-configure-leaves.json').write_text(json.dumps(result,indent=2)+'\n');print('Configuration leaf calls:',result['decoded_leaf_calls'])

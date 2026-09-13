# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_backup_dma_configure import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_backup_dma_configure import execute

def verify(clear_hook=None,bus_hook=None,descriptor_hook=None):
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3d314','--stop-address=0x3d4ac',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-dma-configure/configure.disassembly.txt').read_text());cases=accepted=0
    for channel,length,master,handshake,width in product((0,1),(0,1,4095,4096,69615,69616,-1,-4095,0x7fffffff),(0,1,2,3),(0,1),(0,1,2,7)):
        fields=[width,3,1,6,master,handshake,4,0,0,master,handshake,2]
        a=execute(old,0x3d314,fields,length,channel,state_address=0x2002d3e8,helper_addresses={0x3db04:0x10203c60,0x3d210:0x10203828},clear_hook=clear_hook,bus_hook=bus_hook,descriptor_hook=descriptor_hook);b=execute(new,0x100049d4,fields,length,channel,state_address=0x2002d3e8,helper_addresses={0x100051c4:0x10203c60,0x100048d0:0x10203828},clear_hook=clear_hook,bus_hook=bus_hook,descriptor_hook=descriptor_hook)
        if a!=b:raise ValueError(('Configuration full mismatch',channel,length,master,handshake,width,a,b))
        quotient=abs(length)//4095*(-1 if length<0 else 1)
        count=(quotient+int(length!=quotient*4095))&0xffffffff
        rejected=(count*24)&0xffffffff>416
        if a[0]!=(0xffffffff if rejected else 0):raise ValueError('Configuration size result')
        writes=[x for x in a[1] if x[0]=='write']
        if len(writes)!=(10 if rejected else 11):raise ValueError('Configuration write count')
        base=0xa1000000+channel*88
        control=0x18000001|(4<<11)|(3<<14)|(width<<1)|(width<<4)|(1<<10)|(master<<23)|(master<<25)|(2<<20)
        low=(handshake<<10)|(handshake<<11)
        wanted=[('write',0xa1000000+off,1<<channel) for off in (0x338,0x340,0x348,0x350,0x358)]+[('write',base,0xa0000000),('write',base+8,0x50000),('write',base+24,control),('write',base+64,low),('write',base+68,(6<<7)|2)]
        if not rejected:wanted.append(('write',base+16,0x60000))
        if writes!=wanted:raise ValueError('Configuration independent registers')
        descriptors=[x for x in a[1] if x[0]=='descriptors']
        wanted=[] if rejected else [('descriptors',0x20060000,count,length&0xffffffff,(1<<width)&255,0xa0000000,0x50000,control)]
        if descriptors!=wanted:raise ValueError('Configuration descriptor arguments')
        cases+=1
    invalid_cases=0
    for field,maximum in ((7,1),(2,1),(9,3),(4,3),(10,1),(5,1)):
      for value,channel in product((maximum+1,0x80000000,0xffffffff),(0,1)):
        fields=[1,3,1,6,0,0,4,0,0,0,0,2];fields[field]=value
        a=execute(old,0x3d314,fields,4096,channel,state_address=0x2002d3e8,helper_addresses={0x3db04:0x10203c60,0x3d210:0x10203828})
        b=execute(new,0x100049d4,fields,4096,channel,state_address=0x2002d3e8,helper_addresses={0x100051c4:0x10203c60,0x100048d0:0x10203828})
        assert a==b and a[0]==0xffffffff
        assert all(event[0]=='read' for event in a[1])
        invalid_cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'invalid_configuration_cases':invalid_cases,'source_admitted':False,'hardware_qualified':False,'limits':['Continuous stock/source with ordered external reads/writes and helper calls. Nested helpers modeled; fixed device base. Widths 0/1/2/7; signed length boundary probes.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-dma-configure-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Configuration full cases:',result['decoded_cases'])

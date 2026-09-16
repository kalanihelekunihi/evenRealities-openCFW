# SPDX-License-Identifier: MIT
"""Execute backup UART baud setup with authenticated source arithmetic."""
import json
import subprocess
from verify_gx8002_double_pack_target import execute as execute_arithmetic
from itertools import product
from build_gx8002_backup_uart_configure import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_uart_configure import execute
from verify_gx8002_backup_request_irq import execute as execute_irq
from verify_gx8002_uart_fifo_depth import execute as execute_fifo


def verify():
    candidate = build()
    objdump = str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper = ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(wrapper.read_bytes(), 'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data'))) == IMAGE_SHA
    old = decode(subprocess.check_output([objdump,'-D','--start-address=0x3cc7c','--stop-address=0x3ce5c',str(wrapper)],text=True))
    path = ROOT/'build/gx8002-backup-uart-configure/configure.elf'
    assert sha(path.read_bytes()) == candidate['elf_sha256']
    new = decode(subprocess.check_output([objdump,'-d',str(path)],text=True))
    cluster_path=ROOT/'build/gx8002-backup-uart-interrupt/interrupt.elf'
    cluster_report=json.loads((ROOT/'docs/research/gx8002-backup-uart-cluster.json').read_text())
    assert sha(cluster_path.read_bytes())==cluster_report['elf_sha256']
    new.update(decode(subprocess.check_output([objdump,'-d',str(cluster_path)],text=True)))
    irq_path=ROOT/'build/gx8002-backup-request-irq/request.elf'
    irq_elf=Elf32(irq_path.read_bytes(),'source IRQ registration')
    irq_section=next(sec for sec in irq_elf.sections if sec['name']=='.text')
    composed_dir=ROOT/'build/gx8002-fft-q15-uart-cluster-integration-experiment'
    composed=(composed_dir/'firmware_codec.unadmitted.bin').read_bytes()
    composed_report=json.loads((composed_dir/'build-report.json').read_text())
    assert sha(composed)==composed_report['firmware_sha256']
    assert irq_section['address']==0x10004844 and irq_section['size']==40
    assert composed[0x3d184:0x3d1ac]==irq_elf.contents(irq_section)
    new.update(decode(subprocess.check_output([objdump,'-d',str(irq_path)],text=True)))
    old.update(decode(subprocess.check_output([objdump,'-D','--start-address=0x3d184','--stop-address=0x3d1a4',str(wrapper)],text=True)))
    delta = 0x10003000 - 0x3b940
    cases = 0
    arithmetic_path=ROOT/'build/gx8002-fixunsdfsi-cluster/fix.elf'
    arithmetic_elf=Elf32(arithmetic_path.read_bytes(),'source arithmetic')
    arithmetic_code=decode(subprocess.check_output([objdump,'-d',str(arithmetic_path)],text=True))
    arithmetic_memory={sec['address']+i:byte for sec in arithmetic_elf.sections if sec['flags']&2 and sec['size'] and sec['type']!=8 for i,byte in enumerate(arithmetic_elf.contents(sec))}
    integration=ROOT/'build/gx8002-fft-q15-uart-cluster-integration-experiment'
    image=(integration/'firmware_codec.unadmitted.bin').read_bytes()
    image_report=json.loads((integration/'build-report.json').read_text())
    assert sha(image)==image_report['firmware_sha256']
    for sec in arithmetic_elf.sections:
        if sec['flags']&2 and sec['size'] and sec['type']!=8:
            off=sec['address']-delta
            assert image[off:off+sec['size']]==arithmetic_elf.contents(sec)
    offsets={'uint':0x4ad0c,'divide':0x4a990,'multiply':0x4a790,'add':0x4a724,'fix':0x49da4}
    def arithmetic(kind,args):
        return execute_arithmetic(arithmetic_code,offsets[kind]+delta,bytes(20),arguments=args,return_pair=kind!='fix',readonly=arithmetic_memory,max_steps=100000)
    for rx,tx,depth,mode,changed in product((0,1,2,3,0xffffffff),(0,1,2,3,4),(0,16,128,2048),(0,1),(False,True)):
        base,device,other=0x20016b84,0xa0100000,0xa0200000
        d=[0x12340000+i for i in range(32)]
        d[1]=device;d[3]=(0,32768,24000000,0xffffffff)[cases%4];d[4]=(1,9600,115200,2048,0x0fffffff)[cases%5];d[7]=0 if cases%2 else 7;d[8]=0 if cases%3 else 2;d[9]=mode;d[15]=(6,7,31,32,0xffffffff)[cases%5]
        regs={dev+off:0xa5a50000+off for dev in (device,other) for off in range(0,256,4)}
        regs[device+0xf4]=((depth>>4)<<16)|0xa5001234
        current=other if changed else device;regs[current+0x9c]=rx;regs[current+0xa0]=tx
        results=[]
        for code,entry,shift in ((old,0x3cce4,0),(new,0x100043a4,delta)):
            helpers={0x3cc7c+shift:'fifo',0x3d184+shift:'irq'}
            helpers.update({off+shift:kind for kind,off in offsets.items()})
            def fifo(dev,param):
                return execute_fifo(code,0x3cc7c+shift,dev,param,base)
            def register_irq(number,handler,private):
                return execute_irq(code,0x3d184+shift,number,handler,private)
            results.append(execute(code,entry,d,regs,helpers,arithmetic,depth,current if changed else None,fifo_hook=fifo,irq_hook=register_irq,descriptor_base=base))
        assert results[0]==results[1], (cases,results[0][2],results[1][2])
        result,memory,trace=results[1]
        denominator=(d[4]<<4)&0xffffffff
        divisor,remainder=divmod(d[3],denominator)
        assert memory[base+20]==divisor
        # Exact integer nearest rounding for the 4-bit fractional divider.
        assert memory[base+24]==(32*remainder+denominator)//(2*denominator)
        assert result==0 and memory[base+7*4]==(d[7] or 8) and memory[base+8*4]==(d[8] or 1)
        assert memory[base+11*4]==1 and memory[base+12*4]==depth
        assert memory[base+26*4]==memory[base+31*4]==0xffffffff
        assert [x for x in trace if x[0]=='irq']==[('irq',d[15],0x10004250,base)]
        irq_index=next(i for i,x in enumerate(trace) if x[0]=='irq')
        wanted=[] if d[15]>=32 else [('write',0x200173a8+d[15]*8,4,0x10004250),('write',0x200173ac+d[15]*8,4,base),('write',0xe000e100,4,1<<d[15])]
        assert trace[irq_index+1:]==wanted
        cases+=1
    return {'arithmetic_elf_sha256':sha(arithmetic_path.read_bytes()),'firmware_sha256':sha(image),'elf_sha256':candidate['elf_sha256'],'fifo_cluster_elf_sha256':cluster_report['elf_sha256'],'fifo_executions':cases*2,'irq_elf_sha256':sha(irq_path.read_bytes()),'irq_executions':cases*2,'cases':cases,'source_admitted':False,'limits':['Stock configuration and source configuration both use the same decoded source arithmetic, authenticated against composed bytes; this is not a full-stock arithmetic comparison. Stock/source FIFO instructions executed in separate frames; stock/source IRQ registration executed in separate frames; device mutation follows FIFO return. Exact ordered descriptor/MMIO traces compared. Zero shifted denominators excluded. Hardware qualification remains outstanding.']}


if __name__=='__main__':
    result=verify()
    (ROOT/'docs/research/gx8002-backup-uart-configure-baud.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Backup configuration baud cases:',result['cases'])

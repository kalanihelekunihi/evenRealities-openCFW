# SPDX-License-Identifier: MIT
import hashlib,json,subprocess
from itertools import product
from build_gx8002_dma_release import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_dma_deallocate import verify as deallocate_verify,execute as deallocate,expected
from verify_gx8002_logging import check_paths

def execute(code,entry,channel,hook,deallocate_address=None):
    if code[entry]!=('push','r15',2) or code[entry+6]!=('pop','r15',2):raise ValueError('Release frame instructions')
    op,args,size=code[entry+2]
    targets=(0xd024,0x10203a98) if deallocate_address is None else (deallocate_address,)
    if op!='bsr' or size!=4 or int(args,0) not in targets:raise ValueError('Release target')
    return hook(channel)

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate=build(prefix,sdk,output);dependency=deallocate_verify();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd024','--stop-address=0xd0cc',str(wrapper)],text=True))
    out=output or ROOT/'build/gx8002-dma-release'
    new=decode((out/'release.disassembly.txt').read_text());leaf=decode((ROOT/'build/gx8002-dma-deallocate/deallocate.disassembly.txt').read_text());cases=0
    for source,helper,channel,allocation,token in product((False,True),(False,True),(0,1),product((0,1,2,255),repeat=2),(0,0x40,0xffffffff)):
        def hook(number):return deallocate(leaf if helper else old,0x10203a98 if helper else 0xd024,allocation,token,number)
        result=execute(new if source else old,0x10203b38 if source else 0xd0c4,channel,hook)
        if result!=expected(allocation,token,channel):raise ValueError('Release composition')
        cases+=1
    source_row=candidate['functions'][0]
    if not source_row['fits'] or source_row['compiled_sha256']!=source_row['stock_sha256']:
        raise ValueError('DMA release is not an exact in-envelope replacement')
    row={k:source_row[k] for k in ('symbol','compiled_bytes','compiled_sha256')};row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':row['symbol'],'package_offset':source_row['package_offset'],
        'bytes':source_row['envelope_bytes'],'sha256':source_row['stock_sha256'],'region':'image_a_sram_text'}]
    evidence={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in
        ('build_gx8002_dma_release.py','verify_gx8002_dma_release.py')}
    return {'functions':[row],'candidate':candidate,'deallocation_dependency':dependency,'decoded_cases':cases,
        'evidence_sha256':evidence,'source_admitted':True,'hardware_qualified':False,
        'limits':['Exact wrapper instructions and nested decoded deallocation qualification. IRQ and clock calls remain modeled; no physical concurrency proof.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-release-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Release cases:',result['decoded_cases'])

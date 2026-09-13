# SPDX-License-Identifier: MIT
"""Paired UART entry/body admission, gated on explicit udivdi3 transfer."""
import json,re,shutil
from verify_gx8002_uart_transmit_dma_placement import verify as setup
from verify_gx8002_uart_transmit_dma_placement_cleanup import verify as cleanup
from verify_gx8002_uart_transmit_dma_placement_helpers import verify as helpers
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None,*,proposal=False):
    check_paths(prefix,sdk)
    evidence={'setup':setup(),'cleanup':cleanup(),'helpers':helpers()}
    candidate=evidence['setup']['candidate']
    assert all(x['candidate']==candidate for x in evidence.values()),'Candidate changed during qualification'
    path=ROOT/'build/gx8002-uart-transmit-dma-placement/dma.elf';elf=Elf32(path.read_bytes(),'UART placement')
    expected={'.entry':(0xc694,136,'compiled_assembly'),'.text':(0x13200,356,'compiled_c')}
    sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==2 and not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for section in sections:
        offset,size,kind=expected[section['name']];data=elf.contents(section)
        assert section['flags']&4 and section['address']==offset+0x101f6a74
        assert len(data)<=size and not elf.relocations(section['index'])
        symbol='open_cfw_gx8002_uart_transmit_dma'+('_entry' if section['name']=='.entry' else '')
        rows.append({'symbol':symbol,'section_name':section['name'],'ownership_kind':kind,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_xip_text'}]})
    owner=json.loads((ROOT/'docs/research/gx8002-udivdi3-source-verification.json').read_text())
    row=next(r for r in owner['functions'] if r['section_name']=='.text');occ=row['stock_occurrences'][0]
    assert occ['package_offset']==0x13030 and occ['package_offset']+row['compiled_bytes']<=0x13200
    end=occ['package_offset']+occ['bytes']
    if proposal:assert end in (0x13200,0x13364)
    elif end!=0x13200:raise ValueError('Explicit udivdi3 ownership transfer is required before UART admission')
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-uart-transmit-dma-placement-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        other=json.loads(p.read_text())
        for r in other.get('functions',[other]):
            for o in r.get('stock_occurrences',r.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is None or n is None:continue
                for b,m,_ in expected.values():
                    if a<b+m and b<a+n:
                        if proposal and name=='gx8002-udivdi3-source-verification.json' and o==occ and b==0x13200:continue
                        raise ValueError(('Ownership overlap',name,hex(a),hex(b)))
    if output:
        if proposal:raise ValueError('Proposal must not supply production build output')
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'uart-transmit-dma-placement.elf')
    files=('build_gx8002_uart_transmit_dma_placement.py','verify_gx8002_uart_transmit_dma_placement.py','verify_gx8002_uart_transmit_dma_placement_cleanup.py','verify_gx8002_uart_transmit_dma_placement_helpers.py','verify_gx8002_uart_transmit_dma_placement_source.py','verify_gx8002_uart_transmit_dma.py')
    return {'functions':rows,'evidence':evidence,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':not proposal,'hardware_qualified':False,'ownership_transfer_complete':end==0x13200,'limits':['Paired entry/body qualification; invalid-port cleanup intentionally repairs stock behavior.','Physical DMA/timing and full source-only firmware remain unqualified.']}
if __name__=='__main__':
    r=verify(proposal=True);(ROOT/'docs/research/gx8002-uart-transmit-dma-placement-source-proposal.json').write_text(json.dumps(r,indent=2)+'\n');print('Paired UART proposal qualification passed')

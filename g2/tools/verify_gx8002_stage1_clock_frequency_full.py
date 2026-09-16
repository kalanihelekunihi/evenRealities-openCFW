# SPDX-License-Identifier: MIT
"""Stage-one frequency stock/source suites using compiled lookup output.

Run with --all to check low, high, PLL sweep, 32 kHz and changing selection paths.
"""
import json,struct,subprocess
from itertools import product
from model_gx8002_clock_pll_frequency import frequency
from execute_gx8002_backup_clock_frequency import execute,ROOT,Elf32,decode
from compare_gx8002_stage1_clock_lookup import execute as lookup
from build_gx8002_stage1_clock_frequency import IMAGE,IMAGE_SHA,sha
from build_gx8002_stage1_clock_frequency import build as frequency_build
from build_gx8002_stage1_clock_tables import build as tables_build


def verify(high=False, pll_sweep=False, slow=False, transitions=False):
    frequency_build();tables_build()
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([prefix+'objdump','-D','--start-address=0x38c54','--stop-address=0x38e48',str(wrapper)],text=True))
    candidate=ROOT/'build/gx8002-stage1-clock-frequency/frequency.elf'
    new=decode(subprocess.check_output([prefix+'objdump','-d',str(candidate)],text=True))
    e=Elf32(candidate.read_bytes(),'frequency');switch=struct.unpack('<19I',e.contents(next(s for s in e.sections if s['name']=='.rodata')))
    original_switch=struct.unpack_from('<19I',stock,0x39d0c)
    helper=ROOT/'build/gx8002-stage1-clock-tables/tables.elf'
    hcode=decode(subprocess.check_output([prefix+'objdump','-d',str(helper)],text=True))
    h=Elf32(helper.read_bytes(),'lookup')
    cells={}
    for s in h.sections:
        if s['name'].startswith('.data.'):
            body=h.contents(s)
            offset=s['address']-0x20000000+0x38954
            assert body==stock[offset:offset+len(body)]
            for i,v in enumerate(body):cells[s['address']+i,1]=v
    # Load multi-byte fields with their actual widths, not overlapping byte aliases.
    records=stock[0x39e1c:0x39fbc];ids=[struct.unpack_from('<I',records,i*16)[0] for i in range(26)]
    for i in range(26):
        for off in (8,12):
            address=0x200014c8+i*16+off
            for j in range(4):cells.pop((address+j,1))
            cells[address,4]=struct.unpack_from('<I',records,i*16+off)[0]
    for i in range(17):
        address=0x200016dc+i*4+2
        value=cells.pop((address,1))|(cells.pop((address+1,1))<<8);cells[address,2]=value
    hook=lambda module:lookup(hcode,0x10000138,module,0x1000,ids)
    count=0
    cases=product([*range(28),0x7fffffff,0x80000000,0xffffffff],(0,1<<18),(0,1,0xffffffff,0x12345678))
    cases=((m,s,w,None) for m,s,w in cases)
    if high:
        cases=product(range(26),(0,1),(0,1,0x1ffffff,0x8000000,0xffffffff),
                      ((0,59,0,0,0),(63,2047,0,0,48),(0,0,0,0,0),(1,95,1,7,16)))
    if pll_sweep:
        assert high
        words=[(div,feedback,0,output,band<<4)
               for div,band,feedback,output in product(range(64),range(4),(59,2047),(0,7))]
        cases=product((0,10,16,19,22),(1,),(0,0x8000000),words)
    if slow:
        assert not high and not pll_sweep
        cases=product((0,1,6,9),(0,1,1<<18,(1<<18)|1),
                      (0,1,0xffffffff,0x55555555,0xaaaaaaaa),(None,))
    if transitions:
        assert not high and not slow and not pll_sweep
        cases=product(range(26),range(64),(0,0x8000000),((0,59,0,0,0),))
    for module,source,word,pll_words in cases:
        state=cells.copy()
        for off in range(0,256,4):
            state[0xa0010000+off,4]=word;state[0xa0300000+off,4]=word
        state[0xa001008c,4]=source;state[0xa0300088,4]=0
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        if high and module not in (7,8):
            index=ids.index(mapped);offset=records[index*16+6]
            base=0xa0010000 if mapped<10 else 0xa0300000
            state[base+(0x8c if mapped<10 else 0x88),4]|=1<<offset
        if slow:
            index=ids.index(mapped);offset=records[index*16+6]
            state[0xa001008c,4]|=1<<(offset+1)
        traces=[[],[]]
        args=dict(module=module,lookup_result=0,offset_byte=0,source_word=source,source_cells=state,lookup_hook=hook,pll_words=pll_words,lookup_entry=0x10000138,jump_base=0x100013b8)
        if transitions:
            # Three independently varied two-bit selection samples, with fixed
            # suffixes to expose any extra reads rather than silently cycling.
            bits=[(source>>(2*i))&3 for i in range(3)]
            offset=records[ids.index(mapped)*16+6] if module not in (7,8) else 0
            selections=[(v<<offset)&0xffffffff for v in bits]
            pmu=[1<<18]+selections+[0]*4 if mapped<10 else [1<<18]*8
            args['mmio_sequences']={0xa001008c:pmu,0xa0300088:selections+[0]*5}
        actual=execute(new,switch,entry=0x10000300,mmio_trace=traces[0],**args)
        expected=execute(old,original_switch,entry=0x38c54,delta=0x10000000-0x38954,mmio_trace=traces[1],**args)
        assert actual==expected and traces[0]==traces[1],(module,source,word,actual,expected,traces)
        if transitions:
            count+=1
            continue
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        hz=(frequency(*pll_words) if source else 24576000) if high else (1024000 if source else 12288000)
        if slow:hz=32000
        if module in (7,8) or mapped>=26:
            hz=0
        elif hz!=0xffffffff:
            index=ids.index(mapped);base=0xa0010000 if mapped<10 else 0xa0300000
            if high:
                pointer=struct.unpack_from('<I',records,index*16+12)[0]
                if pointer:
                    value=state[base+state[pointer,1],4]
                    if not value&(1<<27):hz=((value&0x1ffffff)*hz)>>25
            if slow or high or (mapped<9 and (mapped&~4)!=2):
                pointer=struct.unpack_from('<I',records,index*16+8)[0]
                if pointer:
                    off=state[pointer,1];shift=state[pointer+1,1];mask=state[pointer+2,2]
                    value=(state[base+off,4]>>shift)&mask
                    if value:hz//=value+1
        assert actual[0]==hz,('independent frequency oracle',module,actual,hz)
        count+=1
    report={'cases':count,'high_frequency':high,'pll_sweep':pll_sweep,'slow_source':slow,'changing_selection_reads':transitions,'candidate_sha256':sha(candidate.read_bytes()),'lookup_sha256':sha(helper.read_bytes()),'ordered_mmio_compared':True,'independent_arithmetic_oracle':not transitions,
            'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in (
                'verify_gx8002_stage1_clock_frequency_full.py','execute_gx8002_backup_clock_frequency.py',
                'compare_gx8002_stage1_clock_lookup.py','model_gx8002_clock_pll_frequency.py',
                'build_gx8002_stage1_clock_tables.py')},'source_admitted':False,'hardware_qualified':False,'limits':['Finite low or high path suite; complete input partition pending. Lookup runs in a separately abstracted frame. Physical MMIO and concurrency unqualified.']}
    (ROOT/('docs/research/gx8002-stage1-clock-frequency-'+('transitions' if transitions else '32khz' if slow else 'pll-sweep' if pll_sweep else 'high' if high else 'low')+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all',action='store_true',help='Run every implemented frequency suite')
    args=parser.parse_args()
    if args.all:
        reports=[verify(),verify(high=True),verify(high=True,pll_sweep=True),verify(slow=True),verify(transitions=True)]
        print(json.dumps({'suite_cases':[r['cases'] for r in reports],
                          'total_cases':sum(r['cases'] for r in reports),
                          'source_admitted':False,'hardware_qualified':False},indent=2))
    else:print(json.dumps(verify(),indent=2))

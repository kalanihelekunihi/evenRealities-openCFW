# SPDX-License-Identifier: MIT
"""Low-power policy with decoded stateful query/switching helpers."""
import json,random,subprocess,struct
from verify_gx8002_memcpy_source import execute as copy
from execute_gx8002_clock_pll_wait import execute as pll_wait
from verify_gx8002_clock_pll import execute as pll_configure,oracle as pll_oracle,OFFSETS
from verify_gx8002_clock_switch_1m import verify as qualify, execute as switch_outer, expected as outer_expected
from execute_gx8002_clock_gate_query import execute as gate_query
from verify_gx8002_clock_lowpower_init import execute
from load_gx8002_clock_context import load,ROOT
from load_gx8002_clock_decoded_helpers import load_helpers
from execute_gx8002_clock_module_query import execute as query
from execute_gx8002_clock_module_source import execute as switch
from oracle_gx8002_clock_module_source import expected as transition
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import sha
from execute_gx8002_clock_source_select import execute as select
from verify_gx8002_power_initialize import word as memory_word
from load_gx8002_divider_decoded_helpers import load as load_leaves
from execute_gx8002_clock_module_divider import execute as divide
from oracle_gx8002_clock_module_divider import expected as divider_model

def verify():
    evidence=qualify();table,context=load();modules={x['module']:x for x in context['modules']};runners,helper_evidence=load_helpers();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');codes={};hashes={}
    for name,report_name in (('clock-lowpower-init-shared','gx8002-clock-lowpower-init-shared-source-verification.json'),('clock-gate-query-fixed','gx8002-clock-gate-query-fixed-source-verification.json'),('clock-module-query','gx8002-clock-module-query-source-verification.json'),('clock-module-source-fixed','gx8002-clock-module-source-fixed-source-verification.json')):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';elf=Elf32(p.read_bytes(),name);row=json.loads((ROOT/'docs/research'/report_name).read_text())['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256'];codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));hashes[name]=sha(p.read_bytes())
    leaves,leaf_evidence=load_leaves()
    for name in ('clock-source-select','clock-module-divider-set','audio-lowpower-divider','clock-pll','clock-pll-wait'):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';elf=Elf32(p.read_bytes(),name);report=json.loads((ROOT/f'docs/research/gx8002-{name}-source-verification.json').read_text())
        for row in report['functions']:
            section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
        codes[name]=decode(subprocess.check_output([pre,'-d',str(p)],text=True));hashes[name]=sha(p.read_bytes())
    copy_path=ROOT/'build/gx8002-memcpy-source/copy.o';copy_elf=Elf32(copy_path.read_bytes(),'copy');copy_report=json.loads((ROOT/'build/gx8002-memcpy-source/verification.json').read_text());copy_section=next(s for s in copy_elf.sections if s['name']=='.text.open_cfw_gx8002_memcpy');assert sha(copy_elf.contents(copy_section))==copy_report['compiled_sha256']
    codes['copy']=decode(subprocess.check_output([pre,'-dr',str(copy_path)],text=True));hashes['copy']=sha(copy_path.read_bytes())
    owner=Elf32((ROOT/'build/gx8002-board/clock-switch-1m-candidate.elf').read_bytes(),'switch');selector_data=owner.contents(next(s for s in owner.sections if s['name']=='.rodata'));pll_data=owner.contents(next(s for s in owner.sections if s['name']=='.pll'))
    assert sha(selector_data)==evidence['candidate']['source_data']['sha256'] and sha(pll_data)==evidence['candidate']['pll_state']['sha256']
    top=decode((ROOT/'build/gx8002-board/clock-switch-1m-candidate.disassembly.txt').read_text())
    outer=decode((ROOT/'build/gx8002-board/clock-lowpower-init-shared-candidate.disassembly.txt').read_text());rng=random.Random(556);cases=0
    for i in range(128):
        state={base+off:rng.getrandbits(32) for base in (0xa0010000,0xa0300000) for off in (0x18,0x1c,0x20,0x88,0x8c)};calls=[]
        for module in (7,8,10):
            ptr=modules[module]['divider'];state[(0xa0010000 if module<10 else 0xa0300000)+table[ptr]]=rng.getrandbits(32)
        for off in OFFSETS:state[0xa0005000+off]=rng.getrandbits(32)
        initial=dict(state)
        def get(module):
            value,trace=query(codes['clock-module-query'],0x10024d70,module,table,lambda m:(0,runners['lookup_runner'](m)),state)
            row=modules[module];off=row['clock_offset'];word=state[0xa001008c if module<10 else 0xa0300088];want=(word>>off)&1
            if module in (0,1,6,9) and word&(1<<(off+1)):want=2
            if module==7:want=3+int(want!=0)
            if module==8:want=5+int(want!=0)
            assert value==want;calls.append(('get',module,value));return value
        def set_source(module,source):
            result=switch(codes['clock-module-source-fixed'],0x10024be0,module,source,table,modules,state,**runners);assert result==transition(module,source,modules,state);state.update(result[3]);calls.append(('set',module,source));return result[0]
        # Independent policy replay using only descriptor-based transition model.
        model=dict(initial)
        model[0xa001008c]=(model[0xa001008c]&~(1<<28))|(1<<18)
        for module in range(26):
            source=0
            if module in (7,8):
                bit=(model[0xa001008c]>>modules[module]['clock_offset'])&1
                if bit:continue
                source=4 if module==7 else 6
            elif module==2:
                bit=(model[0xa001008c]>>modules[module]['clock_offset'])&1
                if bit and model[0xa001008c]&64:continue
            model=transition(module,source,modules,model)[3]
        expected_answers={}
        for module in range(11,26):
            value=model[0xa0300018];off=modules[module]['gate_all_offset']
            offsets=[modules[module+i]['gate_all_offset'] for i in (1,2)] if module in (16,19,22) else [off]
            expected_answers[module]=0xffffffff if off==0 else int(any(not ((value>>(v&31))&1) for v in offsets))
        low_calls=[]
        def lowpower():
            trace=execute(outer,0x1002599c,{2:0,7:0,8:0},0,get,set_source,lambda:state[0xa001008c])
            assert [x for x in trace if x[0]!='read']==calls
            assert state==model;low_calls.append(True)
        def gate(module):
            value,trace=gate_query(codes['clock-gate-query-fixed'],0x10025180,module,table,lambda m:(0,runners['lookup_runner'](m)),state)
            assert value==expected_answers[module];return value
        sequence=[]
        def selector(source,clk):
            memory={};param=0x20031000;address=0xa001008c;memory_word(memory,param,source);memory[param+4]=clk;memory_word(memory,address,state[address]);seen=[]
            def helper(target,args,m,events):
                assert target==0x10024a30 and args==[address,source,clk,1];seen.append(True)
                ret,after,ev=select(codes['clock-source-select'],0x10024a30,args,m,lambda *a:None);assert ret[0]=='return';m.clear();m.update(after);return 0
            ret,after,ev=select(codes['clock-source-select'],0x10024bcc,[param],memory,helper)
            want=(state[address]&~(1<<source))|(clk<<source);assert ret[0]=='return' and memory_word(after,address)==want and seen==[True];state[address]=want;sequence.append(('selector',source,clk))
        def divider(module,value):
            nonlocal model
            result=divide(codes['clock-module-divider-set'],0x10024df8,module,value,table,lambda m:(0,runners['lookup_runner'](m)),state,**leaves)
            want=divider_model(module,value,table,modules,model);assert result==want;state.update(result[1]);model=want[1];sequence.append(('divider',module,value))
        def audio():
            r={f'r{j}':0x12340000+j for j in range(32)};r['r14']=0x20060000;before=dict(r);pc=0x10025a00
            for _ in range(12):
                op,args,width=codes['audio-lowpower-divider'][pc];p=[v.strip() for v in args.split(',')]
                if op=='push':assert args=='r15';saved_lr=r['r15'];r['r14']-=4
                elif op=='pop':
                    assert args=='r15';r['r15']=saved_lr;r['r14']+=4;assert all(r[f'r{j}']==before[f'r{j}'] for j in (*range(4,12),14,15,16,17));return
                elif op=='movi':r[p[0]]=int(p[1],0)
                elif op=='bsr':
                    assert int(args,0)==0x10024df8;divider(r['r0'],r['r1'])
                    for j in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{j}']=0xdead0000+j
                else:raise ValueError((op,args))
                pc+=width
            raise AssertionError('Audio execution bound')
        saved=rng.getrandbits(32);enable=(0,1,2,0xffffffff)[i%4]
        copied=[];configured=[]
        def transfer(dst,src,count):
            assert src==0x10025cd0 and count==16
            memory={src+j:v for j,v in enumerate(selector_data)};memory.update({dst+j:0xa5 for j in range(-4,20)});before=dict(memory)
            ret,trace=copy(codes['copy'],memory,dst,src,count)
            assert ret==dst and bytes(memory[dst+j] for j in range(16))==selector_data
            assert all(memory[a]==v for a,v in before.items() if not dst<=a<dst+16);copied.append(True)
            return struct.unpack('<4I',bytes(memory[dst+j] for j in range(16)))
        def disable(actual):
            nonlocal model
            assert actual==0
            fields=list(struct.unpack('<14I',pll_data));fields[0]=actual
            registers={off:state[0xa0005000+off] for off in OFFSETS};want=pll_oracle(True,fields,registers,0)
            def configure(value):
                assert value==0
                result=pll_configure(codes['clock-pll'],0x10024b04,True,fields,registers,0);assert result==want
                for off,v in result[1].items():state[0xa0005000+off]=v
                for off,v in want[1].items():model[0xa0005000+off]=v
                configured.append(True);return result[0]
            result=pll_wait(codes['clock-pll-wait'],0x10025060,actual,0,actual,[],[],pll_runner=configure);assert result[0]=='return'
        result=switch_outer(top,0x10025a14,{},saved,enable,(28,0,18,1),gate_runner=gate,lowpower_runner=lowpower,selector_runner=selector,divider_runner=divider,audio_runner=audio,copy_runner=transfer,pll_runner=disable)
        assert result==outer_expected(expected_answers,saved,enable) and low_calls==[True]
        assert sequence==[('selector',28,0),('selector',18,1),('divider',7,0),('divider',8,0),('divider',10,0)]
        assert copied==[True] and len(configured)==int(enable==1)
        assert state==model;cases+=1
    return {'evidence':evidence,'cases':cases,'dependency_elf_sha256':hashes,'helpers':helper_evidence,'divider_leaves':leaf_evidence,'source_admitted':False,'limits':['Stateful decoded helper frames marshalled across policy calls; each transition and final state match independent models. Outer low-power call and subsequent decoded gate queries share state. Selector, low-power initialization, gate queries and dividers decoded with shared state. Copy and PLL wrapper/configuration also decoded; compiled selector/PLL data supplied directly. All outer helper boundaries execute recovered code, with private frames marshalled. Physical clock timing remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-switch-1m-shared.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])

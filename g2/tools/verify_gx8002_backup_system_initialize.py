# SPDX-License-Identifier: MIT
"""Execute complete startup control flow with explicit modeled helper calls."""
import json
import random
import re
import subprocess
from itertools import product
from verify_gx8002_backup_board_initialize import execute as execute_board
from build_gx8002_backup_board_initialize import build as build_board
from verify_gx8002_backup_preserve_memory import execute as execute_predicate
from build_gx8002_backup_preserve_memory import build as build_predicate
from build_gx8002_backup_system_initialize import build, ROOT, Elf32, sha
from build_gx8002_backup_cfft import IMAGE, IMAGE_SHA
from verify_gx8002_memcpy_source import decode


def execute(code,entry,controls,preserve,helpers,seed,predicate=None,board=None):
    rng=random.Random(seed);r={f'r{i}':rng.getrandbits(32) for i in range(32)}
    initial=r.copy();cr=dict(controls);trace=[];pc=entry;saved=None
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r15' and saved is None;saved=r['r15'];r['r14']=(r['r14']-4)&0xffffffff
        elif op=='pop':
            assert args=='r15' and saved is not None;r['r15']=saved;r['r14']=(r['r14']+4)&0xffffffff
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return cr,trace
        elif op in ('mfcr','mtcr'):
            m=re.fullmatch(r'(r\d+), cr<(\d+), 0>',args);assert m
            reg,num=m.groups();num=int(num)
            if op=='mfcr':r[reg]=cr[num];trace.append(('control_read',num,r[reg]))
            else:cr[num]=r[reg];trace.append(('control_write',num,r[reg]))
        elif op in ('lrw','movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ins':
            hi,lo=map(int,p[2:]);mask=((1<<(hi-lo+1))-1)<<lo
            r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('and','andi','andn','andni','ori','addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a&b if op in ('and','andi') else a&~b if op in ('andn','andni') else a|b if op=='ori' else a+b if op=='addi' else a-b)&0xffffffff
        elif op in ('br','bez','bnez'):
            if op=='br' or (r[p[0]]==0)==(op=='bez'):nxt=int(p[-1],0)
        elif op=='bsr':
            name=helpers[int(args,0)];trace.append(('call',name))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            if name=='preserve' and predicate is not None:
                value,reads=predicate();trace.extend(('predicate_read',address,data) for address,data in reads);r['r0']=value
            elif name=='board' and board is not None:
                trace.extend(board());r['r0']=0
            else:r['r0']=preserve if name=='preserve' else 0
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();trace.append(('write',(r[base]+int(off,0))&0xffffffff,r[reg]))
        elif op=='psrset':assert args=='ee, ie';trace.append(('enable','ee','ie'))
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('Startup execution bound')


def verify():
    candidate=build();path=ROOT/'build/gx8002-backup-system-initialize/system.elf'
    assert sha(path.read_bytes())==candidate['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x3ba8c','--stop-address=0x3bb30',str(wrapper)],text=True))
    new=decode(subprocess.check_output([tool,'-d',str(path)],text=True))
    helpers={0x3bbd4:'clock',0x3c93c:'preserve',0x3ba68:'clear_bss',0x3be14:'board'}
    source_helpers={pc-0x3b940+0x10003000:name for pc,name in helpers.items()}
    rng=random.Random(0x3ba8c);cases=0
    for seed in range(256):
        controls={i:rng.getrandbits(32) for i in (1,18,19,20,21)}
        for preserve in (0,1,2,0xffffffff):
            a=execute(old,0x3ba8c,controls,preserve,helpers,seed)
            b=execute(new,0x1000314c,controls,preserve,source_helpers,seed)
            assert a==b,(seed,preserve,a,b)
            expected={**controls,1:0x10003000,18:controls[18]|3,19:(controls[19]&0xfefffcfe)|0x300,20:(controls[20]&0xfc0)|63,21:controls[21]&~7}
            assert b[0]==expected
            calls=[x[1] for x in b[1] if x[0]=='call']
            assert calls==['clock','preserve']+(['clear_bss'] if not preserve else [])+['board']
            assert b[1][-1]==('enable','ee','ie')
            cases+=1
    predicate_evidence=build_predicate()
    predicate_path=ROOT/'build/gx8002-backup-preserve-memory/predicate.elf'
    predicate_elf=Elf32(predicate_path.read_bytes(),'preservation predicate')
    predicate_code=decode(subprocess.check_output([tool,'-d',str(predicate_path)],text=True))
    composed_dir=ROOT/'build/gx8002-fft-q15-uart-cluster-integration-experiment'
    composed=(composed_dir/'firmware_codec.unadmitted.bin').read_bytes()
    composed_report=json.loads((composed_dir/'build-report.json').read_text());assert sha(composed)==composed_report['firmware_sha256']
    for sec in predicate_elf.sections:
        if sec['flags']&2 and sec['size']:
            off=sec['address']-0x10003000+0x3b940
            assert composed[off:off+sec['size']]==predicate_elf.contents(sec)
    board_evidence=build_board()
    board_path=ROOT/'build/gx8002-backup-board-initialize/board.elf'
    assert sha(board_path.read_bytes())==board_evidence['elf_sha256']
    board_code=decode(subprocess.check_output([tool,'-d',str(board_path)],text=True))
    board_elf=Elf32(board_path.read_bytes(),'board source')
    for sec in board_elf.sections:
        if sec['flags']&2 and sec['size']:
            off=sec['address']-0x10003000+0x3b940
            assert composed[off:off+sec['size']]==board_elf.contents(sec)
    predicate_cases=0
    for flags,fallback,preserved in product(range(16),(0,1,0xffffffff),(0,1,2,0xffffffff)):
        values={0xa0000034:flags,0xa001002c:fallback,0xa0010058:preserved,0xa001005c:0x98765432}
        def predicate():return execute_predicate(predicate_code,0x10003ffc,values)
        def board():return execute_board(board_code,0x100034d4,values,0)
        a=execute(old,0x3ba8c,controls,0,helpers,0,predicate,board)
        b=execute(new,0x1000314c,controls,0,source_helpers,0,predicate,board)
        assert a==b
        calls=[x[1] for x in b[1] if x[0]=='call']
        assert ('clear_bss' in calls)==(flags==0 or not preserved&1)
        reads=[x[1:] for x in b[1] if x[0]=='predicate_read']
        addresses=[0xa0000034]+([0xa0010058,0xa001005c] if flags else [0xa001002c])
        assert reads==[(address,values[address]) for address in addresses]
        predicate_cases+=1
    return {'board_elf_sha256':board_evidence['elf_sha256'],'composed_board_cases':predicate_cases,'predicate_elf_sha256':sha(predicate_path.read_bytes()),'composed_predicate_cases':predicate_cases,'candidate':candidate,'cases':cases,'stock_sha256':IMAGE_SHA,'source_admitted':False,'limits':['Complete stock/source startup control flow, ordered control-register effects and helper call order compared. Independent MPU bitmask oracle included. Primary corpus models helper returns. Additional predicate corpus executes authenticated source predicate in a separate frame for both stock/source startup; the board cluster also executes in a separate decoded frame. Clock and BSS clear remain modeled. No complete handoff or hardware timing claim. Specialized source fits original envelope.']}


if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-backup-system-initialize-execution.json').write_text(json.dumps(result,indent=2)+'\n');print(result['cases'],'startup control-flow cases')

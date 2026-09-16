# SPDX-License-Identifier: MIT
"""Decoded backup board configure/setup with faithful failure loop."""
import json, subprocess
from itertools import product
from build_gx8002_backup_board_pin_setup import build, ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_backup_board_pin_setup import execute

def verify():
    evidence=build()
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x411cc','--stop-address=0x412b8',str(path)],text=True))
    old={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        old[pc+delta]=(op,args,width)
    new=decode((ROOT/'build/gx8002-backup-board-pin-setup/erase-linked.disassembly.txt').read_text())
    cases=0
    for flag,pin,function,result in product((0,1,0xffffffff),(0,1,2,31,32,0xffffffff),(0,1,7,0xffffffff),(0,1,0xffffffff)):
        memory={};word(memory,0x200176d8,flag)
        expected=[('read','ld.w',0x200176d8,flag)]
        if not flag:expected.append(('check',pin,int(pin!=2)))
        error=not flag and result!=0
        expected.append(('printf',0x10012ee8,pin) if error else ('set',pin,function))
        for code in (old,new):
            def callback(target,args,state,events):
                name={0x100086dc:'check',0x10008720:'set',0x10009934:'printf'}[target]
                events.append((name,*args[:2]));return result
            outcome,after,events=execute(code,0x1000888c,[pin,function],memory,callback)
            assert outcome[:2]==('return',0xffffffff if error else 0) and after==memory and events==expected
        cases+=1
    pins=[(0,7),(1,7),(3,0),(4,0),(5,0),(6,0),(11,0),(12,0),(7,3),(8,3),(9,3),(10,3)]
    returns=[[0xffffffff if mask&(1<<i) else 0 for i in range(12)] for mask in range(4096)]
    returns += [[1,0xffffffff]+[0]*10,[0x80000000,0x80000000]+[0]*10,[0xffffffff,1]+[0]*10]
    for values in returns:
        failed=bool(sum(values)&0xffffffff)
        expected=[('configure',*pair) for pair in pins]
        if failed:expected += [('set',pin,0) for pin in (5,6,11,12)]+[('printf',0x10012f04)]
        for code in (old,new):
            index=[0]
            def callback(target,args,state,events):
                if target==0x1000888c:
                    events.append(('configure',*args[:2]));value=values[index[0]];index[0]+=1;return value
                if target==0x10008720:events.append(('set',*args[:2]));return 0xffffffff
                assert target==0x10009934;events.append(('printf',args[0]));return 0xffffffff
            outcome,after,events=execute(code,0x100088cc,[],{},callback)
            assert outcome[0]==('terminal_loop' if failed else 'return') and after=={} and events==expected
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Configure tests model pad helpers; setup tests model configure, fallback and printf.','Terminal loop is preserved stock behavior after diagnostic, not a replacement for missing code.','Diagnostic/flag storage and full hardware composition remain separate.']}
    (ROOT/'docs/research/gx8002-backup-board-pin-setup-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(verify()['cases'])

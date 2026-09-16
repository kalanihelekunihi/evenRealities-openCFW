# SPDX-License-Identifier: MIT
"""Check decoded reset control-register/stack setup up to modeled call boundaries."""
import json,re,subprocess,struct
from build_gx8002_stage1_source_cluster import build,ROOT,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,start,control,seed,source):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};cr={0:seed,1:seed,31:control};trace=[];pc=start
    for _ in range(32):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op in ('mfcr','mtcr'):
            m=re.fullmatch(r'(r\d+), cr<(\d+), 0>',args);assert m
            reg,num=m.groups();num=int(num)
            if op=='mfcr':r[reg]=cr[num];trace.append(('read_cr',num,cr[num]))
            else:cr[num]=r[reg];trace.append(('write_cr',num,cr[num]))
        elif op=='bsr':
            target=int(args,0)
            if not source:target=target-0x38954+0x10000000
            trace.append(('call',target,r['r14']))
            if target==0x10003100:return trace
            assert target==0x10000df0
            # A returning dispatcher preserves SP but may clobber caller-saved registers.
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')


def verify():
    evidence=build();out=ROOT/'build/gx8002-stage1-source-cluster';path=out/'cluster.elf'
    elf=Elf32(path.read_bytes(),'source');assert struct.unpack_from('<I',path.read_bytes(),24)[0]==0x10000100
    new=decode((out/'cluster.disassembly.txt').read_text())
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x38a54','--stop-address=0x38a78',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    cases=0
    for control in (*range(256),0x80000000,0xffffffff,0x87654321):
        for seed in (0,0x12345678):
            a=execute(old,0x38a54,control,seed,False);b=execute(new,0x10000100,control,seed,True)
            expected=[('write_cr',0,0x80000200),('read_cr',31,control),('write_cr',31,control&~8),('write_cr',1,0x10000000),('call',0x10000df0,0x20002ffc),('call',0x10003100,0x20002ffc)]
            assert a==b==expected;cases+=1
    report={'cases':cases,'build':evidence,'limits':['Decoded control-register and stack setup checked against independent oracle; dispatcher return and later-image reset are boundaries, not executed bodies. No physical processor, full startup or fallback-image qualification.']}
    (ROOT/'docs/research/gx8002-stage1-reset-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'reset cases passed')

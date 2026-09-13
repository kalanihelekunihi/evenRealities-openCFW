# SPDX-License-Identifier: MIT
"""Decoded LVP startup helper arguments, state paths, and target ABI."""
import json,re,subprocess
from itertools import product
from gx8002_lvp_system_oracle import expected
from build_gx8002_system_initialize import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
SYMBOLS=json.loads((ROOT/'docs/research/gx8002-system-initialize-symbol-map.json').read_text())
NAMES={v:k for k,v in SYMBOLS.items() if not k.startswith('sys_')}

def execute(code,entry,mode,chip,control,trim,seed,control_runner=None,probe_runner=None,timer_runner=None):
    r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();saved=None;pc=entry;condition=False;events=[];stack=0x2006fff0;memory={stack+i:seed&255 for i in range(4)};stock=IMAGE.read_bytes()
    for _ in range(240):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r5, r15' or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in ('r4','r5','r15')};r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return events,memory
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='rotli':
            count=int(p[2],0);value=r[p[1]];r[p[0]]=((value<<count)|(value>>(32-count)))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('ld.w','ld.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0);size=4 if op=='ld.w' else 1
            r[reg]=sum(memory[address+i]<<(i*8) for i in range(size))
        elif op in ('ldr.h','ldr.hs'):
            reg,base,index=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 1\)',args).groups();address=r[base]+2*r[index]
            if not SYMBOLS['sys_trim_millivolts']<=address<SYMBOLS['sys_trim_millivolts']+24:raise ValueError('Table read')
            value=int.from_bytes(stock[address-0x101f6a74:address-0x101f6a74+2],'little',signed=op=='ldr.hs');r[reg]=value&MASK
        elif op=='sexth':r[p[0]]=((r[p[1]]&65535)-(65536 if r[p[1]]&32768 else 0))&MASK
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&MASK;name=NAMES[target];value=(seed*0x1234567)&MASK
            if name=='printf':
                fmt=r['r0'];offset=fmt-0x101f6a74;string=stock[offset:stock.index(0,offset)]
                events.append((name,fmt,r['r1']) if b'%' in string else (name,fmt))
            elif name=='gx_console_init':events.append((name,r['r0'],r['r1']))
            elif name=='gx_spi_flash_probe':events.append((name,*(r[f'r{i}'] for i in range(4))));value=probe_runner(tuple(r[f'r{i}'] for i in range(4)),0x20010000+seed*4) if probe_runner else 0x20010000+seed*4
            elif name=='gx_spi_flash_getinfo':events.append((name,r['r0'],r['r1']));value=chip if r['r1']==2 else (seed*65536)&MASK
            elif name=='gx_spi_flash_gettype':events.append((name,r['r0']));value=0x20020000+seed*4
            elif name=='gx_clock_get_module_frequence':events.append((name,r['r0']));value=(seed*1000000+r['r0'])&MASK
            elif name=='gx_pmu_get_wakeup_source':events.append((name,));value=mode
            elif name=='gx_analog_get_ldo_dig_ctrl':events.append((name,));value=control_runner() if control_runner else control
            elif name=='gx_pmu_ctrl_get':
                if r['r1']!=stack:raise ValueError('PMU output')
                events.append((name,r['r0']));config=(seed<<8)|trim
                for i in range(4):memory[stack+i]=(config>>(i*8))&255
            elif name=='gx_timer_init':
                events.append((name,))
                if timer_runner is not None:timer_runner()
            elif name=='gx_rtc_set_tick':events.append((name,r['r0']))
            else:events.append((name,))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError(('Opcode',op))
        pc=nxt
    raise ValueError('Bound')

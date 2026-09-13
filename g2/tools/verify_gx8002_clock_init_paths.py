# SPDX-License-Identifier: MIT
"""Decoded full initialization stock/source call routing and state comparison."""
import json,subprocess,struct
from build_gx8002_clock_init_pointer_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from execute_gx8002_clock_init import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from oracle_gx8002_clock_init import expected


def verify(copy_runner=None,mode_runner=None,modes=(0,1,2,0xffffffff),trim_runner=None,trims=(0,1,2,0xffffffff),pll_retry_runner=None,pll_block_runner=None,selector_runner=None,module_runner=None,divider_runner=None,dto_runner=None,gate_runner=None,analog_runner=None,digital_runner=None,voltage_state_runner=None,selector_state_runner=None,module_state_runner=None,module_state_model=None,divider_state_runner=None,divider_state_model=None,divider_addresses=(),gate_state_runner=None,gate_state_model=None,pll_state_runner=None,pll_state_model=None,trim_state_runner=None):
    candidate=build();image=IMAGE.read_bytes();assert sha(image)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x17a9c','--stop-address=0x17cd0',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-init-pointer-candidate.disassembly.txt').read_text());cases=0
    for mode in modes:
        for trim in trims:
            for success in range(6):
                initial={}
                for off,n,delta in ((0x188dc,220,0x2000dfec),(0x17cf4,36,0x1000dfec)):
                    initial.update({off+delta+i:v for i,v in enumerate(image[off:off+n])})
                word(initial,0x20027318,(0,0xffffffff,0xa5a55a5a,0x5a5aa5a5)[success%4]);word(initial,0x20026900,trim)
                word(initial,0x200268dc,(3071,0,0xffffffff,5,0xfffffff8,15)[success])
                for off in (0x40,0x44,0x48,0x4c,0x60,0x84):word(initial,0xa0005000+off,0xffffffff)
                if pll_state_runner:
                    for off in (0x1c,0x20,0x24,0x28,0x2c,0x30,0x3c):word(initial,0xa0005000+off,(0,0xffffffff,0xaaaaaaaa,0x55555555)[success%4])
                for address in divider_addresses:word(initial,address,(0,0xffffffff,0xaaaaaaaa,0x55555555)[success%4])
                if module_state_runner or gate_state_runner:
                    assert module_state_model is not None or gate_state_model is not None
                    for base in (0xa0010000,0xa0300000):
                        for off in (0x18,0x1c,0x20,0x88,0x8c):word(initial,base+off,(0,0xffffffff,0xaaaaaaaa,0x55555555)[success%4])
                if selector_state_runner:word(initial,0xa001008c,(0,0xffffffff,0xaaaaaaaa,0x55555555)[success%4])
                if voltage_state_runner:
                    word(initial,0xa0005054,(0,0xffffffff,0xaaaaaaaa,0x55555555)[success%4])
                    word(initial,0xa0000038,0xdeadbeef)
                def run(code,entry):
                    count=[];calls=[]
                    def helper(target,args,memory,events):
                        if target==0x10025738:
                            dst,src,n=args[:3];assert n in (16,20)
                            if copy_runner:return copy_runner(memory,dst,src,n)
                            for i in range(n):memory[dst+i]=memory[src+i]
                            return dst
                        if target==0x10024984:result=mode_runner(mode) if mode_runner else mode;call=('mode',)
                        elif target==0x10024a1c:
                            result=trim_state_runner(trim,memory,events,gate_state_runner) if trim_state_runner else (trim_runner(trim) if trim_runner else trim);call=('trim',)
                        elif target==0x1002500c:
                            assert args[0]==0x200268c8 and args[1]==40;call=('pll_retry',word(memory,args[0]+20));result=0 if len(count)==success else 0xffffffff;count.append(True)
                            if pll_retry_runner:result=pll_retry_runner([word(memory,args[0]+i*4) for i in range(14)],args[1],result)
                        elif target==0x10025060:
                            call=('pll',word(memory,args[0]));result=0
                            if pll_block_runner:pll_block_runner([word(memory,args[0]+i*4) for i in range(14)])
                        elif target==0x10024bcc:
                            call=('selector',word(memory,args[0]),memory[args[0]+4]);result=0
                            if selector_runner:selector_runner(call[1],call[2])
                        else:
                            arities={0x10024df8:2,0x10024f44:3,0x10024be0:2,0x10025080:2,0x100246f0:1,0x10024730:1};assert target in arities;call=(target,*args[:arities[target]]);result=0xffffffff
                        if target==0x10024be0 and module_runner:result=module_runner(args[0],args[1])
                        if target==0x10024df8 and divider_runner:divider_runner(args[0],args[1])
                        if target==0x10024f44 and dto_runner:dto_runner(args[0],args[1],args[2])
                        if target==0x10025080 and gate_runner:gate_runner(args[0],args[1])
                        if target==0x100246f0 and analog_runner:result=analog_runner(args[0])
                        if target==0x10024730 and digital_runner:result=digital_runner(args[0])
                        if voltage_state_runner and target in (0x100246f0,0x10024730):result=voltage_state_runner(target,args,memory,events)
                        if selector_state_runner and target==0x10024bcc:result=selector_state_runner(args,memory,events)
                        if module_state_runner and target==0x10024be0:result=module_state_runner(args,memory,events)
                        if divider_state_runner and target in (0x10024df8,0x10024f44):divider_state_runner(target,args,memory,events)
                        if gate_state_runner and target==0x10025080:gate_state_runner(args,memory,events)
                        if pll_state_runner and target in (0x1002500c,0x10025060):result=pll_state_runner(target,args,memory,events,result)
                        calls.append(call);return result
                    result,after,events=execute(code,entry,[],initial,helper)
                    return result[0],after,calls,events
                a=run(old,0x17a9c);b=run(new,0x10025a88);assert a==b==expected(mode,trim,success,initial,voltage_state_runner is not None,selector_state_runner is not None,module_state_model,divider_state_model,gate_state_model,pll_state_model,trim_state_runner is not None),(mode,trim,success,a,b,expected(mode,trim,success,initial,voltage_state_runner is not None,selector_state_runner is not None,module_state_model,divider_state_model,gate_state_model,pll_state_model,trim_state_runner is not None));cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Full decoded stock/source helper order, state and MMIO writes agree. Helpers modeled and initializer memcpy marshalled; independent full policy oracle agrees; decoded dependency integration remains pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-paths.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])

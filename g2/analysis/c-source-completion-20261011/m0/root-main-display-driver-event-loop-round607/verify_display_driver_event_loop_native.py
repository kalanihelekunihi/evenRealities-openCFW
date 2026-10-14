#!/usr/bin/env python3
"""Bounded native control-flow oracle for one received display-driver message."""
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

root = Path(__file__).resolve().parents[4]
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
helpers = {
    0x4739fc:'queue_init', 0x473abc:'init_a', 0x4c9f32:'init_b', 0x473ac6:'init_c',
    0x473ad0:'init_d', 0x43c0e4:'zero', 0x449b3c:'receive', 0x46d816:'before',
    0x46d826:'after', 0x46ca14:'prelude', 0x47386a:'sync', 0x46b238:'gate',
    0x4ca18a:'case0', 0x4ca010:'case1a', 0x473b34:'case1b', 0x4c9fb4:'case2',
    0x4ca564:'case3', 0x46c410:'case4read', 0x4ca1ee:'case4apply',
    0x473b46:'case5a', 0x4ca126:'case5b', 0x4ca5be:'case6guard',
    0x4ca60e:'case8', 0x43d0ce:'logflags', 0x43d574:'textlog', 0x43ce9e:'compactlog'
}
def run(mid, enabled=1, gate=1, tail=0, guard=0, log_flags=0):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000); cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x20000000,0x100000)
    cpu.mem_write(0x20000664,(0x20002000).to_bytes(4,'little'))
    cpu.mem_write(0x200744ec,enabled.to_bytes(4,'little'))
    calls=[]; visits=0
    def hook(uc,address,_size,_user):
        nonlocal visits
        if address==0x473c62:
            visits+=1
            if visits==2: uc.emu_stop(); return
        name=helpers.get(address)
        if name is None:return
        calls.append(name)
        r0=uc.reg_read(UC_ARM_REG_R0)
        if name=='zero':
            uc.mem_write(r0,b'\0'*0x24)
        elif name=='receive':
            assert r0==0x20002000 and uc.reg_read(UC_ARM_REG_R2)==0 and uc.reg_read(UC_ARM_REG_R3)==0xffffffff
            dest=uc.reg_read(UC_ARM_REG_R1)
            words=[mid]+list(range(0x11,0x18))+[tail]
            uc.mem_write(dest,b''.join(w.to_bytes(4,'little') for w in words))
            uc.reg_write(UC_ARM_REG_R0,0)
        elif name=='gate':uc.reg_write(UC_ARM_REG_R0,gate)
        elif name=='case6guard':uc.reg_write(UC_ARM_REG_R0,guard)
        elif name=='logflags':uc.reg_write(UC_ARM_REG_R0,log_flags)
        elif name=='textlog':
            sp=uc.reg_read(UC_ARM_REG_SP)
            def cs(a):return bytes(uc.mem_read(a,128)).split(b'\0')[0].decode('ascii')
            assert r0==(3 if mid==6 else 2)
            assert cs(uc.reg_read(UC_ARM_REG_R1))=='task.displaydrvmgr'
            assert cs(uc.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\platform\display_mgr\displaydrv_manager.c'
            assert cs(uc.reg_read(UC_ARM_REG_R3))=='Disp_Mgr_ThreadHandler'
            assert int.from_bytes(uc.mem_read(sp,4),'little')==(0x10d if mid==6 else 0x117)
            assert cs(int.from_bytes(uc.mem_read(sp+4,4),'little'))==('uled recovery and reflash ok\r\n' if mid==6 else 'unknow async command type = %d\r\n')
            if mid!=6:assert int.from_bytes(uc.mem_read(sp+8,4),'little')==mid
        elif name=='compactlog':
            def cs(a):return bytes(uc.mem_read(a,128)).split(b'\0')[0].decode('ascii')
            assert r0==(0x0c000000 if mid==6 else 0x08400000)
            expected=('[task.displaydrvmgr]uled recovery and reflash ok\r\n' if mid==6 else '[task.displaydrvmgr]unknow async command type = %d\r\n')
            assert cs(uc.reg_read(UC_ARM_REG_R1))==expected,(mid,cs(uc.reg_read(UC_ARM_REG_R1)),expected)
            assert cs(uc.reg_read(UC_ARM_REG_R2))==expected
            if mid!=6:assert uc.reg_read(UC_ARM_REG_R3)==mid
        elif name=='case4read':
            assert r0==0x17
            uc.mem_write(uc.reg_read(UC_ARM_REG_R1),(0x1234).to_bytes(4,'little'))
            uc.mem_write(uc.reg_read(UC_ARM_REG_R2),(0x5678).to_bytes(4,'little'))
        elif name=='case4apply':
            assert (r0,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2))==(0x17,0x5678,0x1234)
        elif name=='case8':assert r0==0x17
        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000)
    cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.emu_start(0x473c45,0x600000,count=1000)
    assert visits==2, (mid,visits,calls)
    final=int.from_bytes(cpu.mem_read(0x200744ec,4),'little')
    return calls,final
base=['queue_init','init_a','init_b','init_c','init_d','zero','receive','before','gate']
expected={
 0:['case0'],1:['case1a','case1b'],2:['case2'],
 3:['case3'],4:['case4read','case4apply'],
 5:['case5a','case5b'],6:['case6guard','prelude','sync','case3','logflags','logflags','logflags'],
 8:['case8'],7:['logflags','logflags','logflags']}
for mid,case in expected.items():
    prefix=base[:]
    if mid==3:prefix=base[:-1]+['prelude','sync','gate']
    calls,final=run(mid)
    assert calls==prefix+case+['after'],(mid,calls)
    assert final==({1:1,5:0}.get(mid,1)),(mid,final)
for mid in (0,2,4,5,6,8):
    calls,final=run(mid,enabled=0)
    assert calls==base+(['case0'] if mid==0 else [])+['after'],(mid,calls)
    assert final==0
calls,_=run(0,gate=0,tail=0)
assert calls==base+['after'],calls
print('PASS_DISPLAY_DRIVER_EVENT_LOOP_NATIVE',len(expected)+6+1)

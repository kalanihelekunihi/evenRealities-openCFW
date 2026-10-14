#!/usr/bin/env python3
"""Compare bounded native and compiled-C display-driver event-loop effects."""
from pathlib import Path
import subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP
from verify_display_driver_event_loop_native import run as native_run

source=Path(__file__).with_name('display_driver_event_loop.c')
name_to_label={
'audio_display_driver_queue_init':'queue_init','display_driver_init_473abc':'init_a',
'display_driver_init_4c9f32':'init_b','display_driver_init_473ac6':'init_c',
'display_driver_init_473ad0':'init_d','audio_uart_buffer_zero':'zero',
'audio_uart_queue_receive':'receive','task_vote_acquire_current':'before',
'task_vote_release_current':'after','display_driver_case3_prelude':'prelude',
'display_driver_case3_sync':'sync','display_driver_dispatch_gate':'gate',
'display_driver_case0':'case0','display_driver_case1_a':'case1a',
'display_driver_case1_b':'case1b','display_driver_case2':'case2',
'display_driver_case3':'case3','display_driver_case4_read':'case4read',
'display_driver_case4_apply':'case4apply','display_driver_case5_a':'case5a',
'display_driver_case5_b':'case5b','display_driver_case6_guard':'case6guard',
'display_driver_case8':'case8','audio_log_flags':'logflags',
'audio_log_extended':'textlog','compressed_log_output':'compactlog'}
with tempfile.TemporaryDirectory() as d:
    d=Path(d)
    asm=d/'stubs.s'
    asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
        f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in name_to_label)+
        '.bss\n.global audio_display_driver_manager\naudio_display_driver_manager:\n.space 16\n'
        '')
    elfpath=d/'event.elf'
    subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
        '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_event_loop',str(source),str(asm),
        '-o',str(elfpath)],check=True,capture_output=True)
    with elfpath.open('rb') as f:
        elf=ELFFile(f)
        segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    hooks={symbols[n]&~1:label for n,label in name_to_label.items()}
    for mid,enabled,gate,tail,guard,log_flags in [(i,1,1,0,0,0) for i in (0,1,2,3,4,5,6,7,8)]+[
        (i,0,1,0,0,0) for i in (0,2,4,5,6,8)]+[(0,1,0,0,0,0),(0,1,0,1,0,0),(6,1,1,0,1,0)]+[(mid,1,1,0,0,flags) for mid in (6,7) for flags in (1,2,4,5,6,7)]:
        native_calls,native_enabled=native_run(mid,enabled,gate,tail,guard,log_flags)
        cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        cpu.mem_map(0x100000,0x200000)
        cpu.mem_map(0x20000000,0x100000)
        for address,data in segments:cpu.mem_write(address,data)
        manager=symbols['audio_display_driver_manager']; flag=symbols['display_driver_enabled']
        cpu.mem_write(manager+12,(0x20002000).to_bytes(4,'little'))
        cpu.mem_write(flag,enabled.to_bytes(4,'little'))
        calls=[]
        def hook(uc,address,_size,_user):
            # Counter is mutable because Python has no nonlocal at module scope.
            label=hooks.get(address)
            if label is None:return
            if label=='receive':
                receive_count[0]+=1
                if receive_count[0]==2:uc.emu_stop();return
            calls.append(label)
            r0=uc.reg_read(UC_ARM_REG_R0)
            if label=='zero':uc.mem_write(r0,b'\0'*0x24)
            elif label=='receive':
                assert r0==0x20002000 and uc.reg_read(UC_ARM_REG_R2)==0 and uc.reg_read(UC_ARM_REG_R3)==0xffffffff
                words=[mid]+list(range(0x11,0x18))+[tail]
                uc.mem_write(uc.reg_read(UC_ARM_REG_R1),b''.join(w.to_bytes(4,'little') for w in words))
                uc.reg_write(UC_ARM_REG_R0,0)
            elif label=='gate':uc.reg_write(UC_ARM_REG_R0,gate)
            elif label=='case6guard':uc.reg_write(UC_ARM_REG_R0,guard)
            elif label=='logflags':uc.reg_write(UC_ARM_REG_R0,log_flags)
            elif label=='textlog':
                sp=uc.reg_read(UC_ARM_REG_SP)
                def cs(a):return bytes(uc.mem_read(a,128)).split(b'\0')[0].decode('ascii')
                assert r0==(3 if mid==6 else 2)
                assert cs(uc.reg_read(UC_ARM_REG_R1))=='task.displaydrvmgr'
                assert cs(uc.reg_read(UC_ARM_REG_R2))==r'D:\01_workspace\s200_ap510b_iar_git\platform\display_mgr\displaydrv_manager.c'
                assert cs(uc.reg_read(UC_ARM_REG_R3))=='Disp_Mgr_ThreadHandler'
                assert int.from_bytes(uc.mem_read(sp,4),'little')==(0x10d if mid==6 else 0x117)
                assert cs(int.from_bytes(uc.mem_read(sp+4,4),'little'))==('uled recovery and reflash ok\r\n' if mid==6 else 'unknow async command type = %d\r\n')
                if mid!=6:assert int.from_bytes(uc.mem_read(sp+8,4),'little')==mid
            elif label=='compactlog':
                def cs(a):return bytes(uc.mem_read(a,128)).split(b'\0')[0].decode('ascii')
                assert r0==(0x0c000000 if mid==6 else 0x08400000)
                expected=('[task.displaydrvmgr]uled recovery and reflash ok\r\n' if mid==6 else '[task.displaydrvmgr]unknow async command type = %d\r\n')
                assert cs(uc.reg_read(UC_ARM_REG_R1))==expected
                assert cs(uc.reg_read(UC_ARM_REG_R2))==expected
                if mid!=6:assert uc.reg_read(UC_ARM_REG_R3)==mid
            elif label=='case4read':
                assert r0==0x17
                uc.mem_write(uc.reg_read(UC_ARM_REG_R1),(0x1234).to_bytes(4,'little'))
                uc.mem_write(uc.reg_read(UC_ARM_REG_R2),(0x5678).to_bytes(4,'little'))
            elif label=='case4apply':
                assert (r0,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2))==(0x17,0x5678,0x1234)
            elif label=='case8':assert r0==0x17
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        receive_count=[0]
        cpu.hook_add(UC_HOOK_CODE,hook)
        cpu.reg_write(UC_ARM_REG_SP,0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR,0x600001)
        cpu.emu_start(symbols['display_driver_event_loop']|1,0x600000,count=2000)
        assert receive_count[0]==2,(mid,enabled,gate,tail,guard,receive_count,calls)
        # Compiled C reaches its next zero before the second receive; native oracle stops at loop top.
        assert calls[:-1]==native_calls and calls[-1]=='zero',(mid,enabled,gate,tail,guard,native_calls,calls)
        actual_enabled=int.from_bytes(cpu.mem_read(flag,4),'little')
        assert actual_enabled==native_enabled,(mid,actual_enabled,native_enabled)
print('PASS_DISPLAY_DRIVER_EVENT_LOOP_C_NATIVE',30)

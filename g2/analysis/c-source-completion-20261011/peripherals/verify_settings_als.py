"""Actual C/native ALS clamp and previous-source selection."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
    state=ROOT/'components/audio/uart_thread_source_candidate/display_als_state.c'
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_settings_apply_als',str(ROOT/'components/audio/uart_thread_source_candidate/display_settings_als_apply.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_als_calculation.c'),str(state),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    cells=[('audio_als_active_previous',0x200741e0),('audio_als_default_previous',0x200741dc),('audio_als_scale_clamped',0x20000060),('audio_als_scale_active',0x20000064),('audio_als_scale_shadow',0x20000068),('audio_als_recompute_pending',0x20074200),('audio_als_curve_index',0x200741e4),('audio_als_curve_nominal',0x200741e8),('audio_als_curve_adjusted',0x200741ec)]
    def run(candidate,requested,active):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for addr,payload in segments:u.mem_write(addr,payload)
        u.mem_map(0x20000000,0x100000)
        for name,address in cells:
            value=active if name=='audio_als_active_previous' else (900 if name=='audio_als_default_previous' else 777)
            u.mem_write(address,struct.pack('<I',value));u.mem_write(symbols[name],struct.pack('<I',value))
        u.reg_write(UC_ARM_REG_R0,requested);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.emu_start((symbols['audio_settings_apply_als'] if candidate else 0x4ae8e8)|1,0x600000,count=500)
        return [bytes(u.mem_read(symbols[name] if candidate else address,4)) for name,address in cells]
    for case in [(0,0),(614,400),(615,0),(1433,400),(1434,0),(2000,400),(800,10),(800,250),(800,500),(800,1200),(800,1500)]:
        native=run(False,*case);compiled=run(True,*case)
        assert native==compiled,(case,native,compiled)
        print('PASS settings ALS',case)

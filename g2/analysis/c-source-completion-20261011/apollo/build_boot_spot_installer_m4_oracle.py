#!/usr/bin/env python3
"""Rebuild the isolated Cortex-M4 selected-C SPOT installer oracle input."""
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SOURCE=ROOT/'g2/components/bootloader/initializer_callbacks/startup_runtime.c'
OUT=HERE/'spot-m4-oracle'
OUT.mkdir(exist_ok=True)
OBJECT=OUT/'startup_runtime.o'
ELF=OUT/'startup_runtime.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
 '-ffunction-sections','-fdata-sections','-c',str(SOURCE),'-o',str(OBJECT)],check=True)
bindings={
 'spotmgr_init_42abbc_native':0x42abbd,
 'opencfw_boot_spotmgr_power_state_update_a':0x42a879,
 'opencfw_pcm22_temperature_init':0x42ac55,
 'opencfw_pcm22_profile_apply':0x42ab7d,
 'opencfw_pcm22_post_lptohp':0x42a037,
 'opencfw_pcm22_timer_service':0x42a04b,
 'hw_state_compose_42bdf0_native':0x42bdf1,
 'opencfw_boot_spot_state_power_event':0x42ba01,
 'opencfw_boot_hardware_readiness_gate':0x42bf55,
 'pcm21_boost_service':0x42ae9d,
 'bl_bl009_dispatch_native':0x42d6c1,
 'state_event_dispatch_42d562_native':0x42d563,
 'state_event_flag_set_42d5c2_native':0x42d5c3,
 'state_event_finalize_42d5cc_native':0x42d5cd,
 'autosw_initialize_42d63a_native':0x42d63b,
 'startup_noop_42f670_native':0x42f671,
 'opencfw_boot_ton_state_event':0x42f38f,
 'opencfw_boot_ton_trim_cache':0x42f41b,
 'opencfw_boot_ton_trim_apply':0x42f4b3,
}
subprocess.run(['arm-none-eabi-ld','--gc-sections','-Ttext=0x435000','-e',
 'opencfw_boot_startup_spot_dispatch',
 *(f'--defsym={name}={address:#x}' for name,address in bindings.items()),
 str(OBJECT),'-o',str(ELF)],check=True)
subprocess.run([sys.executable,str(HERE/'verify_boot_spot_installer_compiled_m4.py')],check=True)

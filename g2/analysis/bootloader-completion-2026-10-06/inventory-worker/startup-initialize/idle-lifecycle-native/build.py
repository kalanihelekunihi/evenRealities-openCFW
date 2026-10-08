"""Compile the bounded native chain addon; never modify shared candidate."""
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists())
inputs=[(HERE/'idle_chain.c','/tmp/opencfw-idle-chain.o'),(HERE/'tickless_native.c','/tmp/opencfw-idle-tickless.o'),(HERE.parent/'idle-sleep-policy/sleep_policy.c','/tmp/opencfw-idle-policy.o'),(ROOT/'g2/components/bootloader/thread_creation/kernel_runtime.c','/tmp/opencfw-idle-kernel.o')]
for n in ['scheduler_resume','scheduler_tick','idle_cleanup','thread_termination','rtos_heap','timer_wait']:
 inputs.append((ROOT/('g2/components/bootloader/thread_creation/'+n+'.c'),'/tmp/opencfw-idle-'+n+'.o'))
inputs.append((HERE/'sysctrl_sleep.c','/tmp/opencfw-idle-sysctrl.o'))
inputs.append((HERE/'sleep_helpers.c','/tmp/opencfw-idle-sleephelpers.o'))
inputs.append((ROOT/'g2/components/bootloader/initializer_callbacks/startup_ton_gate.c','/tmp/opencfw-idle-ton-gate.o'))
for src,obj in inputs:
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfloat-abi=soft','-O1','-ffreestanding','-fno-builtin',*(['-ffunction-sections'] if src.name not in ['idle_chain.c','tickless_native.c','sysctrl_sleep.c','sleep_helpers.c'] else []),'-c',str(src),'-o',obj],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-T',str(HERE/'module.ld'),*[obj for src,obj in inputs],'-o','/tmp/opencfw-idle-chain.elf'],check=True)

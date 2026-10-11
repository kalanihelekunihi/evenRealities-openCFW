#!/usr/bin/env python3
"""Compare the Clang archive export with original CASE and actual original peers."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'g2/components/case/source_candidate_20261010/event_set_task.c'
PREVIOUS = ROOT / 'g2/analysis/case-event-waiters-closure-2026-10-08/verify.py'
GCC = Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
CLANG = Path('/usr/bin/clang')
OUT = HERE / 'build'
OUT.mkdir(exist_ok=True)
OBJ = OUT / 'event_set_task.o'
ELF = OUT / 'event_set_task.elf'
LINK = OUT / 'link.ld'
LINK.write_text('case_suspend_scheduler = 0x0800c381; case_resume_scheduler = 0x0800cc0d; case_unblock_waiter = 0x0800c1cd; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
compile_cmd = [str(CLANG), '--target=arm-none-eabi', '-mcpu=cortex-m0plus', '-mthumb', '-mfloat-abi=soft', '-std=c11', '-Os', '-ffreestanding', '-fno-builtin', '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-c', str(SOURCE), '-o', str(OBJ)]
link_cmd = [str(GCC), '-mcpu=cortex-m0plus', '-mthumb', '-nostdlib', '-T', str(LINK), str(OBJ), '-o', str(ELF)]
subprocess.run(compile_cmd, check=True)
subprocess.run(link_cmd, check=True)
archive_object = ROOT / 'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__event_set_task.c.o'
assert hashlib.sha256(OBJ.read_bytes()).digest() == hashlib.sha256(archive_object.read_bytes()).digest()
prior = PREVIOUS.read_text()
assert "ns['symbols']['case_event_set_waiters']" in prior
modified = prior.replace("ns['symbols']['case_event_set_waiters']", "ns['symbols']['xEventGroupSetBits']")
sys.argv = [str(PREVIOUS), str(ELF)]
exec(compile(modified, str(PREVIOUS), 'exec'), {'__file__': str(HERE / 'verify.py'), '__name__': '__main__'})
result = HERE / 'results.json'
data = json.loads(result.read_text())
data['candidate_source_sha256'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
data['archive_object_sha256'] = hashlib.sha256(archive_object.read_bytes()).hexdigest()
data['compiler_sha256'] = hashlib.sha256(CLANG.read_bytes()).hexdigest()
data['compile_command'] = compile_cmd
data['link_command'] = link_cmd
data['scope'] = 'Current Clang export wrapper; same coherent one-waiter fixtures and limits as prior verifier.'
result.write_text(json.dumps(data, indent=2) + '\n')

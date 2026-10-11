#!/usr/bin/env python3
"""Build a co-placed Boot source ELF; this is a layout experiment, not firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, default=HERE / 'boot-coplacement-experiment')
args = parser.parse_args()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
objects = out / 'objects'
subprocess.run([sys.executable,
    str(ROOT / 'g2/components/bootloader/source_candidate_20261010/build.py'),
    '--output', str(objects)], check=True)
sources = [ROOT / f'g2/components/bootloader/source_candidate_20261010/{name}'
           for name in ('tlsf_printf_candidate.c', 'generic_log_float_candidate.c',
                        'mspi_interrupt_service_candidate.c')]
experimental = []
for index, source in enumerate(sources):
    obj = out / f'experimental-{index}.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
        '-mfpu=fpv5-sp-d16', '-mfloat-abi=softfp', '-std=c11', '-ffreestanding',
        '-fno-builtin', '-O2', '-fshort-enums', '-fwrapv', '-ffunction-sections',
        '-fdata-sections', '-c', str(source), '-o', str(obj)], check=True)
    experimental.append(obj)
elf = out / 'boot.elf'
linker = HERE / 'boot_coplacement_experiment.ld'
command = ['arm-none-eabi-ld', '--gc-sections', '--emit-relocs', '-T', str(linker),
    '-Map', str(out / 'boot.map'), '-o', str(elf),
    '-u', 'opencfw_boot_install_initialized_data', '-u', 'opencfw_boot_vectors',
    # The scheduler enters this task through a control block. Retain its
    # source-owned registration chain even when static GC cannot follow it.
    '-u', 'opencfw_boot_manager_task',
    '--whole-archive', str(objects / 'libbootloader_source_candidate_m55.a'),
    '--no-whole-archive', *(str(obj) for obj in experimental)]
link = subprocess.run(command, capture_output=True, text=True)
(out / 'link.log').write_text(link.stdout + link.stderr)
if link.returncode:
    raise SystemExit(link.returncode)
receipt = out / 'receipt.json'
subprocess.run([sys.executable, str(HERE / 'verify_boot_coplacement.py'),
                '--elf', str(elf), '--receipt', str(receipt)], check=True)
data = json.loads(receipt.read_text())
inventory = json.loads((objects / 'inventory.json').read_text())
selected = [ROOT / unit['source'] for unit in inventory['units']
            if unit['status'] == 'selected']
source_files = selected + sources + [linker, Path(__file__),
    HERE / 'verify_boot_coplacement.py', HERE / 'boot-vector-census.json',
    HERE / 'scatter-full-relocations-receipt.json']
data['source_sha256'] = {str(path.relative_to(ROOT)):
    hashlib.sha256(path.read_bytes()).hexdigest() for path in source_files}
data['selected_units'] = inventory['counts']['selected']
data['source_providers'] = len(inventory['global_weak_providers'])
data['link_command'] = command
receipt.write_text(json.dumps(data, indent=2) + '\n')
print(json.dumps({'status': data['status'], 'selected_units': data['selected_units'],
                  'image_file_bytes': data['image_file_bytes'],
                  'callback_relocations': len(data['callbacks_relocated_to_live_source_symbols'])}))

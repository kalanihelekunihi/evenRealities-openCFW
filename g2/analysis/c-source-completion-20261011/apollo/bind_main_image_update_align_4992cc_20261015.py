#!/usr/bin/env python3
"""Bind native-compared LVGL image alignment updater."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
HERE = Path(__file__).resolve().parent
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_image_update_align_4992cc.c'
OUT = G2 / 'build/c-firmware/20261015/main-image-update-align-4992cc'
BASE = G2 / 'build/c-firmware/20261015/main-image-text-style-498640/apollo-main-image-text-style-498640.o'
ORACLE = HERE / 'verify_main_image_update_align_4992cc_oracle_20261015.py'
OWNED = 'audio_uart_lv_image_update_align_4992cc'
CHILDREN = {'audio_uart_lv_image_set_rotation_4988dc',
            'audio_uart_lv_image_set_pivot_498a14',
            'audio_uart_lv_image_scale_update_4991e0'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'display_image_update_align_4992cc.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                    '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                    '-O2', '-Wall', '-Wextra', '-Werror', '-c', str(SOURCE),
                    '-o', str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True)
    oracle = json.loads((OUT / 'oracle.json').read_text())
    if oracle['status'] != 'PASS_EXPERIMENTAL_MAIN_IMAGE_UPDATE_ALIGN_ORACLE' or \
            oracle['cases'] != 180 or oracle['source_sha256'] != sha(SOURCE):
        raise RuntimeError('image alignment oracle changed')
    before = symbols(BASE, '-u')
    defined = symbols(BASE, '--defined-only')
    if OWNED not in before or symbols(obj, '--defined-only') != {OWNED} or \
            symbols(obj, '-u') - defined != CHILDREN:
        raise RuntimeError('image alignment provider contract changed')
    linked = OUT / 'apollo-main-image-update-align-4992cc.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj),
                    '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if len(before) != 211 or len(after) != 213 or \
            before - after != {OWNED} or after - before != CHILDREN or \
            OWNED not in symbols(linked, '--defined-only'):
        raise RuntimeError('image alignment linked contract changed')
    receipt = {
        'status': 'PASS_EXPERIMENTAL_MAIN_IMAGE_UPDATE_ALIGN_C',
        'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
        'object_sha256': sha(obj), 'oracle_sha256': sha(OUT / 'oracle.json'),
        'upstream': 'third-party/upstream/lvgl/src/widgets/image/lv_image.c',
        'upstream_revision': '344c7c318047b7348e1be8572a9fd4260c251cfa',
        'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
        'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
        'unresolved_before': len(before), 'unresolved_after': len(after),
        'source_owned_symbols': [OWNED], 'imports_resolved': [OWNED],
        'imports_added': sorted(CHILDREN), 'source_complete': False,
        'full_payload_linked': False, 'hardware_proof': False,
        'limits': ['180 controlled native stretch/tile/default branch comparisons.',
                   'Rotation, pivot and scale children remain unresolved.',
                   'No live image decoder or hardware proof.'],
    }
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], len(before), len(after), sha(path))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Bind two bounded PCM registration rows into experimental Main candidate."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-pcm-registration-rows'
PRIOR = BASE / 'main-ble-registration-state-alias/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_pcm_registration_rows_20073c20_20261017.c'
REGISTER = ROOT / 'g2/components/audio/pcm_register_source_candidate/register.c'
UNREGISTER = ROOT / 'g2/components/audio/pcm_unregister_source_candidate/unregister.c'
OBJECT, CURRENT, OUT = HERE / 'pcm-rows.o', HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    assert 'index >= 2u' in REGISTER.read_text()
    assert '3u * index' in REGISTER.read_text()
    assert 'struct g2_pcm_registration_slot' in UNREGISTER.read_text()
    assert 'audio_terminal_ui_timer_state_20073c38' in symbols(PRIOR, '--defined-only')
    assert 0x20073c20 + 2 * 12 == 0x20073c38
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    sections = subprocess.check_output(['arm-none-eabi-objdump', '-h', str(OBJECT)], text=True)
    assert '.g2_bss_20073c20 00000018' in sections
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['g2_pcm_registration_rows'] and not added
    assert len(prior) == 91 and len(after) == 90
    record = {'status': 'PASS_MAIN_PCM_REGISTRATION_ROWS_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'register_source': ref(REGISTER),
              'unregister_source': ref(UNREGISTER),
              'stock_base': '0x20073c20', 'exclusive_end': '0x20073c38',
              'row_count': 2, 'row_stride': 12, 'extent_bytes': 24,
              'unresolved_before': 91, 'unresolved_after': 90,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Two complete PCM registration row extents compile as BSS, adjacent to the known timer state. Initializer, final RAM placement, concurrent lifetime and whole-image behavior remain open.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()

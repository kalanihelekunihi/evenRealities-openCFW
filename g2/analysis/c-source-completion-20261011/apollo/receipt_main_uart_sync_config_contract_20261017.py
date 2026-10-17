#!/usr/bin/env python3
"""Qualify the observed UART sync configuration prefix without inventing RAM contents."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / 'g2/build/c-firmware/20261017/uart-sync-config-contract'
SRC = ROOT / 'g2/components/audio/uart_thread_source_candidate'
HEADER = SRC / 'sync_uart_config_contract.h'
DRIVER = SRC / 'sync_driver_buffer.c'
RESET = SRC / 'sync_reset.c'
ORACLE = ROOT / 'g2/analysis/c-source-completion-20261011/peripherals/verify_audio_uart_sync_reset.py'
OUT = HERE / 'receipt.json'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    objects = []
    for source, name in ((DRIVER, 'driver.o'), (RESET, 'reset.o')):
        obj = HERE / name
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-ffreestanding', '-fno-builtin', '-c', str(source), '-o', str(obj)], check=True)
        objects.append(obj)
    combined = HERE / 'combined.o'
    subprocess.run(['arm-none-eabi-ld', '-r', *(str(x) for x in objects), '-o', str(combined)], check=True)
    result = subprocess.check_output(['/tmp/opencfw-oracle-venv/bin/python', str(ORACLE)], text=True).strip()
    assert result == 'PASS_AUDIO_UART_SYNC_RESET 13'
    definitions = subprocess.check_output(['arm-none-eabi-nm', '--defined-only', str(combined)], text=True)
    assert ' audio_uart_sync_driver_buffer' in definitions
    assert ' audio_uart_sync_reset0' in definitions
    rec = {'status': 'PASS_MAIN_UART_SYNC_CONFIG_PREFIX_C',
           'header': ref(HEADER), 'sources': [ref(DRIVER), ref(RESET)],
           'objects': [ref(x) for x in objects], 'relocatable_object': ref(combined),
           'native_oracle_source': ref(ORACLE), 'native_oracle_result': result,
           'observed_prefix_bytes': 13,
           'remaining_gate': 'The stock UART configuration RAM object at 0x20000d9c has no authenticated extent or initialization bytes; this prefix compilation does not rebind the previously linked Main candidate.',
           'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(rec, indent=2, sort_keys=True) + '\n')
    print(rec['status'], sha(OUT))

if __name__ == '__main__': main()

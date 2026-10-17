#!/usr/bin/env python3
"""Compare the stock clock entry with the C helper reached through its R5 adapter."""
import hashlib
import itertools
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LEGACY = ROOT / 'g2/analysis/audio-gpio-providers-2026-10-08'
HERE = ROOT / 'g2/build/c-firmware/20261017/main-clock-mux-entry'
ADAPTER = ROOT / 'g2/components/audio/clock_reset_active_offline/stock_clock_mux_reset_entry.c'
HELPER = ROOT / 'g2/components/audio/clock_reset_active_offline/recovery.c'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    scope = runpy.run_path(str(LEGACY / 'verify_clock.py'))
    symbols = scope['sym']
    assert 'stock_clock_mux_reset' in symbols
    assert 'clock_reset_recover' in symbols
    run = scope['run']
    original = symbols['clock_reset_recover']
    symbols['clock_reset_recover'] = symbols['stock_clock_mux_reset']
    count = 0
    try:
        for flags, ref, ready, scratch, pattern in itertools.product(
                [16, 32, 48], [0, 1], [0, 1],
                [0, 0x12345678, 2 << 10, 3 << 10, 0xffffffff],
                [0, 0xffffffff]):
            case = dict(flags=flags, ref=ref, ready=ready,
                        scratch=scratch, pattern=pattern)
            assert run(False, **case) == run(True, **case), case
            count += 1
    finally:
        symbols['clock_reset_recover'] = original
    assert count == 120
    record = {
        'status': 'PASS_MAIN_CLOCK_MUX_ENTRY_R5_ADAPTER_STOCK_MATCH',
        'cases': count,
        'adapter_source_sha256': sha(ADAPTER),
        'helper_source_sha256': sha(HELPER),
        'native_elf_sha256': sha(scope['elf']),
        'stock_payload_sha256': '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701',
        'stock_entry': '0x44b158',
        'comparison': 'register R5, peripheral writes, provider calls and retained state',
        'limits': ['Peripheral readiness is modeled, not observed on G2 hardware.',
                   'This verifies the clock entry only, not the complete startup chain.'],
        'source_complete': False, 'flashable': False, 'hardware_proof': False,
    }
    output = HERE / 'entry-oracle.json'
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], count, sha(output))


if __name__ == '__main__':
    main()

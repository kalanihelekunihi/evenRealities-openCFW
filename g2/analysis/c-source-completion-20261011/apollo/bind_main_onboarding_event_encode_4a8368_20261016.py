#!/usr/bin/env python3
"""Bind stock-checked onboarding event encoder and four-node nanopb graph."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/onboarding_event_encode_4a8368.c'
SCHEMA = G2 / 'components/audio/uart_thread_source_candidate/onboarding_event_pb_descriptor_779c94.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-onboarding-event-encode-4a8368/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-onboarding-wear-notify-47e320/apollo-main-onboarding-wear-notify-47e320.o'
OUT = G2 / 'build/c-firmware/20261015/main-onboarding-event-encode-4a8368'
OWNED = {'audio_onboarding_event_encode_4a8368',
         'audio_onboarding_event_descriptor_779c94',
         'audio_onboarding_event_packet_200f612c',
         'audio_onboarding_event_state_200f623c',
         'audio_onboarding_event_sequence_20074ffb'}
RESOLVED = {'audio_onboarding_event_encode_4a8368'}
IMPORTS = {'audio_log_extended', 'audio_log_flags', 'audio_pb_encode',
           'audio_pb_ostream_from_buffer', 'audio_ring_pb_assert_509b48',
           'audio_ring_pb_tx_ble_475c1a', 'audio_uart_buffer_zero',
           'audio_uart_checksum_copy', 'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_ONBOARDING_EVENT_ENCODE_4A8368'
            or oracle['cases'] != 120 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['descriptor_source_sha256'] != sha(SCHEMA)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Onboarding event encoder evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    objs = []
    for src, name in ((SOURCE, 'onboarding_event_encode_4a8368.o'),
                      (SCHEMA, 'onboarding_event_pb_descriptor_779c94.o')):
        obj = OUT / name
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                        '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                        '-Wextra', '-Werror', '-c', str(src), '-o', str(obj)], check=True)
        objs.append(obj)
    defined = set().union(*(symbols(obj, '--defined-only') for obj in objs))
    imported = set().union(*(symbols(obj, '-u') for obj in objs))
    if defined != OWNED or imported != IMPORTS | {'audio_onboarding_event_descriptor_779c94'}:
        raise RuntimeError('Onboarding event encoder object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 191 or before & OWNED != RESOLVED or not IMPORTS <= provided:
        raise RuntimeError('Onboarding event encoder base contract changed')
    linked = OUT / 'apollo-main-onboarding-event-encode-4a8368.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), *(str(obj) for obj in objs),
                    '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != RESOLVED or after - before or len(after) != 190:
        raise RuntimeError('Onboarding event encoder link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_ONBOARDING_EVENT_ENCODE_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'descriptor_source': str(SCHEMA.relative_to(ROOT)),
               'descriptor_source_sha256': sha(SCHEMA),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'objects': [{ 'path': str(obj.relative_to(ROOT)), 'sha256': sha(obj)} for obj in objs],
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(RESOLVED),
               'imports_added': [], 'unresolved_before': 191, 'unresolved_after': 190,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['The packet, state and sequence RAM cells need final placement; nanopb and BLE transport calls are controlled in the oracle.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 191, 190, sha(path))

if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Bind stock-checked dominant-hand master connection handler."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/ble_master_hand_changed_4a2948.c'
ORACLE = G2 / 'build/c-firmware/20261016/main-ble-master-hand-changed-4a2948/oracle-receipt.json'
BASE = G2 / 'build/c-firmware/20261015/main-ble-master-set-target-hand-4a2068/apollo-main-ble-master-set-target-hand-4a2068.o'
OUT = G2 / 'build/c-firmware/20261015/main-ble-master-hand-changed-4a2948'
OWNED = {'audio_ble_master_hand_changed_4a2948'}
ADDED = {'audio_ble_master_begin_failure_notify_4a1546',
         'audio_ble_master_reset_scene_pending_4a2658',
         'audio_ble_peer_ring_status_47d8f0',
         'audio_ble_ring_policy_cancel_connect_timeout_49f5f8',
         'audio_ble_ring_policy_schedule_connect_timeout_49f4a8',
         'audio_ble_ring_policy_schedule_reconnect_timeout_49f552'}
IMPORTS = ADDED | {
    'audio_ble_master_auth_mode_set', 'audio_ble_master_clear_failure_notify',
    'audio_ble_master_connect_event', 'audio_ble_master_context',
    'audio_ble_master_disconnect_delayed', 'audio_ble_master_link_matches_target',
    'audio_ble_master_open_connection', 'audio_ble_master_reset_retry_count',
    'audio_ble_master_schedule_connect', 'audio_ble_master_set_target_hand_4a2068',
    'audio_ble_master_start_try_connect_ring', 'audio_ble_ring_link_state',
    'audio_ble_ring_link_state_name', 'audio_ble_ring_policy_notify_success_49f646',
    'audio_ble_set_ring_link_state', 'audio_event_loop_push_delayed',
    'audio_event_loop_remove_delayed', 'audio_log_extended', 'audio_log_flags',
    'audio_queue_copy_bytes', 'audio_ring_address_is_unset_4a26e8',
    'audio_setting_unit_record_get_466010', 'audio_uart_ring_active',
    'compressed_log_output'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle['status'] != 'PASS_NATIVE_MAIN_BLE_MASTER_HAND_CHANGED_4A2948'
            or oracle['cases'] != 280 or oracle['source_sha256'] != sha(SOURCE)
            or oracle['official_payload_sha256'] != '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'):
        raise RuntimeError('Hand-changed oracle evidence changed')
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / 'ble_master_hand_changed_4a2948.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-Wall',
                    '-Wextra', '-Werror', '-c', str(SOURCE), '-o', str(obj)], check=True)
    if symbols(obj, '--defined-only') != OWNED or symbols(obj, '-u') != IMPORTS:
        raise RuntimeError('Hand-changed object contract changed')
    before = symbols(BASE, '-u'); provided = symbols(BASE, '--defined-only')
    if len(before) != 189 or before & OWNED != OWNED or not (IMPORTS - ADDED) <= provided:
        raise RuntimeError('Hand-changed base contract changed')
    linked = OUT / 'apollo-main-ble-master-hand-changed-4a2948.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(obj), '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if before - after != OWNED or after - before != ADDED or len(after) != 194:
        raise RuntimeError('Hand-changed link frontier changed')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_BLE_MASTER_HAND_CHANGED_C',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'oracle': str(ORACLE.relative_to(ROOT)), 'oracle_sha256': sha(ORACLE),
               'oracle_cases': oracle['cases'], 'native_body_sha256': oracle['native_body_sha256'],
               'object': str(obj.relative_to(ROOT)), 'object_sha256': sha(obj),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'source_owned_symbols': sorted(OWNED), 'imports_resolved': sorted(OWNED),
               'imports_added': sorted(ADDED), 'unresolved_before': 189, 'unresolved_after': 194,
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['Six exposed peer-status, failure-notify, scene-reset and timeout-policy children need independent C bodies; final RAM placement and hardware execution remain open.']}
    path = OUT / 'receipt.json'; path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 189, 194, sha(path))

if __name__ == '__main__': main()

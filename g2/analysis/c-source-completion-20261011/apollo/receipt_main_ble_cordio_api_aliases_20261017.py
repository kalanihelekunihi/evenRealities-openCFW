#!/usr/bin/env python3
"""Bind Cordio names to stock-oracled DM and HCI Main providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'g2/build/c-firmware/20261017'
HERE = BASE / 'main-ble-cordio-api-aliases'
PRIOR = BASE / 'main-att-cfg/candidate.o'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_cordio_api_aliases_20261017.c'
DM_SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_dm_conn_check_idle_4b73a2_20261017.c'
HCI_SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_hci_max_rx_acl_len_530d4c_20261017.c'
DM_ORACLE = BASE / 'main-ble-dm-conn-check-idle/oracle-receipt.json'
HCI_ORACLE = BASE / 'main-ble-hci-max-rx-acl-len/oracle-receipt.json'
OBJECT, CURRENT, OUT = HERE / 'aliases.o', HERE / 'candidate.o', HERE / 'receipt.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', option, str(path)], text=True).splitlines() if line.strip()})


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    dm, hci = json.loads(DM_ORACLE.read_text()), json.loads(HCI_ORACLE.read_text())
    assert dm['status'] == 'PASS_BOUNDED_MAIN_BLE_DM_CONN_CHECK_IDLE_C'
    assert hci['status'] == 'PASS_BOUNDED_MAIN_BLE_HCI_MAX_RX_ACL_LEN_C'
    assert dm['cases'] == 108 and hci['cases'] == 11
    assert dm['source_sha256'] == sha(DM_SOURCE)
    assert hci['source_sha256'] == sha(HCI_SOURCE)
    defined = set(symbols(PRIOR, '--defined-only'))
    assert {'audio_ble_dm_conn_check_idle_4b73a2',
            'audio_ble_hci_max_rx_acl_len_530d4c'}.issubset(defined)
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    subprocess.run(['arm-none-eabi-ld', '-r', str(PRIOR), str(OBJECT),
                    '-o', str(CURRENT)], check=True)
    prior, after = set(symbols(PRIOR, '-u')), set(symbols(CURRENT, '-u'))
    removed, added = sorted(prior - after), sorted(after - prior)
    assert removed == ['DmConnCheckIdle', 'HciGetMaxRxAclLen'] and not added
    assert len(prior) == 96 and len(after) == 94
    record = {'status': 'PASS_MAIN_BLE_CORDIO_API_ALIASES_C_INTEGRATION',
              'prior_candidate': ref(PRIOR), 'candidate_object': ref(CURRENT),
              'source': ref(SOURCE), 'dm_oracle': ref(DM_ORACLE),
              'hci_oracle': ref(HCI_ORACLE),
              'unresolved_before': 96, 'unresolved_after': 94,
              'removed_imports': removed, 'new_imports': added,
              'remaining_gate': 'Cordio DM idle and HCI maximum RX ACL API names delegate to bounded stock-oracled providers. Whole-image ABI, layout, startup and remaining imports stay open.',
              'source_complete': False, 'flashable': False, 'hardware_proof': False}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], len(after), sha(OUT))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Check all 39 aligned native Thumb-pointer source leads in a C ELF."""
from pathlib import Path
import argparse, json, subprocess

HERE = Path(__file__).resolve().parent
NATIVE = json.loads((HERE / 'case-indirect-pointer-targets.json').read_text())
ROOTS = {
    '0x080000b8': 'case_startup_entry_00b8',
    '0x08000102': 'case_vector_pendsv_0102',
    '0x08000144': 'case_reset_entry_0144',
    '0x08000156': 'case_vector_default_0156',
    '0x080006c4': 'case_vector_irq_06c4',
    '0x08003bc8': 'case_vector_irq_3bc8',
    '0x08003c2c': 'case_vector_irq_3c2c',
    '0x08003d24': 'case_vector_irq_3d24',
    '0x08006778': 'case_vector_hardfault_6778',
    '0x08006d70': 'case_vector_nmi_6d70',
    '0x08006e08': 'case_vector_irq_6e08',
    '0x08006e18': 'case_vector_svc_6e18',
    '0x08006e1c': 'case_boot_transport_cb_6e1c',
    '0x08007200': 'case_policy_task_7200',
    '0x08007f2c': 'case_boot_transport_cb_7f2c',
    '0x080082ec': 'case_boot_transport_cb_82ec',
    '0x08008420': 'case_vector_systick_8420',
    '0x080084ae': 'case_early_hook_84ae',
    '0x080084b0': 'case_vector_irq_84b0',
    '0x08008558': 'case_boot_transport_entry_8558',
    '0x080086e0': 'case_boot_sensor_cancel_callback',
    '0x08008758': 'case_boot_sensor_callback_8758',
    '0x08008808': 'case_boot_sensor_callback_8808',
    '0x08008998': 'case_boot_sensor_callback_8998',
    '0x08008a48': 'case_boot_sensor_callback_8a48',
    '0x08008f98': 'case_vector_irq_8f98',
    '0x08009684': 'case_boot_transport_cb_9684',
    '0x08009d70': 'case_boot_transport_cb_9d70',
    '0x0800a380': 'case_log_output_char',
    '0x0800a598': 'case_application_entry_a598',
    '0x0800ab70': 'case_boot_transport_cb_ab70',
    '0x0800ae5c': 'case_boot_idle_task_entry',
    '0x0800b31c': 'case_boot_task_return',
    '0x0800b360': 'case_boot_service_task_entry',
    '0x0800b7ec': 'case_boot_transport_cb_b7ec',
    '0x0800bb90': 'case_boot_transport_cb_bb90',
    '0x0800bb4c': 'case_boot_transport_cb_bb4c',
    '0x0800bf84': 'vEventGroupClearBitsCallback',
    '0x0800bf8c': 'vEventGroupSetBitsCallback',
}
expected = {r['target'] for r in NATIVE['rows']}
assert expected == set(ROOTS), (expected - set(ROOTS), set(ROOTS) - expected)
parser = argparse.ArgumentParser()
parser.add_argument('elf', type=Path)
args = parser.parse_args()
nm = subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-nm', '--defined-only', str(args.elf)], text=True)
symbols = {parts[-1]: int(parts[0], 16) for line in nm.splitlines()
           if (parts := line.split()) and len(parts) >= 3 and all(c in '0123456789abcdefABCDEF' for c in parts[0])}
rows = [{'native': address, 'source_symbol': symbol, 'linked_address': hex(symbols[symbol]) if symbol in symbols else None}
        for address, symbol in ROOTS.items()]
result = {'status': 'SOURCE_LINK_ROOT_CHECK_ONLY', 'elf': str(args.elf.resolve()),
          'native_pointer_target_count': len(expected), 'source_entry_present': sum(x['linked_address'] is not None for x in rows),
          'rows': rows, 'limits': ['Aligned stock pointer target role remains bounded to retained consumer evidence.',
                                    'Runtime-constructed pointers and peripheral/ROM callback registration are not covered.',
                                    'Presence of a linked source symbol does not prove stock address or behavior equality.']}
out = args.elf.with_suffix('.indirect-roots.json')
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'present': result['source_entry_present'], 'expected': len(rows),
                  'missing': [x for x in rows if x['linked_address'] is None]}, indent=2))

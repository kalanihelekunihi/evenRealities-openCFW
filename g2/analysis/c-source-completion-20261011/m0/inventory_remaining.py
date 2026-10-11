#!/usr/bin/env python3
"""Classify every unresolved symbol in the deterministic CASE experiment."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
build=json.loads((HERE/'case_full_experiment.o.receipt.json').read_text())
send={'case_binary_14_send','case_binary_local_send','case_binary_send51','case_binary_send5f'}
ack={'case_binary_3e_ack','case_binary_3f_ack','case_binary_56_ack','case_binary_local_ack'}
flash={}
sensor={}
other={
 'case_kernel_invariant_failure':('0x0800c686 / 0x0800c7a8','Original invalid queue arguments enter an architectural fault loop; platform fault policy remains an explicit noreturn contract.'),
 'case_kernel_nesting_underflow':('0x0800c014','Original zero-depth exit enters an architectural fault loop; platform fault policy remains an explicit contract.'),
}
rows=[]
for name in build['undefined_symbols']:
    if name in send:
        row={'original_entry':'0x0800680c','group':'send_return_abi',
             'selected_provider':'case_send',
             'missing':'Selected send source is void; this candidate returns its R0. Residual return register under UART/logger paths needs original/source proof.'}
    elif name in ack:
        row={'original_entry':'0x080068d0','group':'ack_return_abi',
             'selected_provider':'case_ack',
             'missing':'Selected ACK source is void; this candidate returns its R0. Residual return register after send needs original/source proof.'}
    elif name=='case_binary_5e_hex':
        row={'original_entry':'0x080067c8','group':'hex_return_abi',
             'selected_provider':'log_hex_buffer',
             'missing':'Selected hex logger is void while binary 0x5e returns its R0; final register/effect contract needs proof.'}
    elif name=='case_legacy_gpio_bit0':
        row={'original_entry':'0x08006b80','group':'gpio_return_abi',
             'selected_provider':'case_control_a',
             'missing':'Selected GPIO setter is void while legacy 0xa1 returns its R0; physical pin and residual return ABI need proof.'}
    elif name in flash:
        entry,missing=flash[name];row={'original_entry':entry,'group':'flash_product_state','missing':missing}
    elif name in sensor:
        entry,missing=sensor[name];row={'original_entry':entry,'group':'sensor_transport','missing':missing}
    elif name in other:
        entry,missing=other[name];row={'original_entry':entry,'group':'other_hardware_or_task','missing':missing}
    else:
        raise SystemExit('unclassified CASE import: '+name)
    rows.append({'symbol':name,**row})
receipt={'build_sha256':build['sha256'],'unresolved_count':len(rows),
         'source':'fixed CASE image g2-2.2.6.10; selected/candidate source and bounded oracle reports',
         'contracts':rows}
(HERE/'remaining_contracts.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('CLASSIFIED_CASE_IMPORTS',len(rows))

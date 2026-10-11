#!/usr/bin/env python3
"""Classify test-link unresolved aliases against selected CASE source providers."""
from pathlib import Path
import subprocess,json,hashlib
D=Path(__file__).resolve().parent;root=D.parents[2]
names=[line.split()[-1] for line in subprocess.check_output(['arm-none-eabi-nm','-u',str(D/'binary_known_linked.o')],text=True).splitlines()]
groups={
 'send':('case_send','g2/components/case/source_candidate_20261010/send_provider.c',['case_binary_14_send','case_binary_5e_send','case_binary_local_send','case_binary_send51','case_binary_send5f'],'void source return; candidate declares uint32_t, so return ABI requires review'),
 'ack':('case_ack','g2/components/case/source_candidate_20261010/ack_provider.c',['case_binary_3e_ack','case_binary_3f_ack','case_binary_56_ack','case_binary_5e_ack','case_binary_local_ack'],'void source return; candidate declares uint32_t, so return ABI requires review'),
 'logger':('g2_log_printf','g2/components/case/source_candidate_20261010/log_wrapper_provider.c',['case_binary_3d_logger','case_binary_3e_logger','case_binary_3f_logger','case_binary_3f_program_log','case_binary_56_logger','case_binary_56_exit_log','case_binary_5e_logger','case_binary_logger'],'32-bit return ABI; case_vformat lower unresolved'),
 'event_control':('case_forward_event','g2/components/case/source_candidate_20261010/evidenced_providers.c',['case_binary_3d_control','case_binary_3e_control','case_binary_forward_control'],'same two-word input and uint32_t return; event flags lower hardware/task semantics bounded'),
 'hex_logger':('log_hex_buffer','g2/components/case/source_candidate_20261010/hex_log_provider.c',['case_binary_5e_hex'],'void source return; candidate declares uint32_t, so return ABI requires review'),
 'gpio':('case_control_a/b','g2/components/case/source_candidate_20261010/control_providers.c',['case_binary_local_control_a','case_binary_local_control_b','case_binary_56_clear_a','case_binary_56_clear_b'],'void source return; candidate ignores child return; physical GPIO excluded'),
}
rows=[]
for group,(provider,source,aliases,note) in groups.items():
 h=hashlib.sha256((root/source).read_bytes()).hexdigest()
 for name in aliases:rows.append(dict(alias=name,group=group,selected_provider=provider,selected_source=source,selected_source_sha256=h,abi_note=note))
mapped={x['alias'] for x in rows};assert len(names)==31 and len(mapped)==26 and mapped<=set(names)
remaining=sorted(set(names)-mapped);assert len(remaining)==5
underlying_lowers=['case_binary_sensor_transaction','case_binary_sensor_delay_count','case_binary_3f_bus','case_binary_56_cancel'];assert set(underlying_lowers)<=set(remaining)
original_children=[x for x in remaining if x not in underlying_lowers];assert len(original_children)==1
out=dict(status='CLASSIFIED_TEST_LINK_LOWER_NAMES',test_lower_names=len(names),mapped_to_selected_source_aliases=len(mapped),remaining_original_child_names=len(original_children),new_underlying_lower_names=len(underlying_lowers),mapped=rows,remaining_original_children=original_children,underlying_lowers=underlying_lowers,unmapped=remaining,limits=['Test aliases are not 31 distinct production providers.','Mapping by original target address and selected source does not resolve return ABI or lower effects.','No adapter is selected into the public archive.'])
(D/'binary-lower-census.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(names),len(mapped),len(remaining));print('original children',', '.join(original_children));print('new underlying lowers',', '.join(underlying_lowers))

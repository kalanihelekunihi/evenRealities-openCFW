#!/usr/bin/env python3
"""Static, source-pinned blocker census for the CASE candidate."""
from pathlib import Path
import json, subprocess
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
symbols=json.loads((HERE/'receipt.json').read_text())['unresolved_symbols']
source_root=ROOT/'g2/components/case'
report={
 'binary_forward_offline':'case-binary-forward-closure-2026-10-08',
 'deferred_consumer_offline':'case-deferred-consumer-closure-2026-10-08',
 'deferred_event_offline':'case-deferred-event-closure-2026-10-08',
 'event_flags_offline':'case-event-flags-closure-2026-10-08',
 'event_waiters_offline':'case-event-waiters-closure-2026-10-08',
 'frame_callback_offline':'case-frame-callback-closure-2026-10-08',
 'frame_dispatch_offline':'case-frame-dispatch-closure-2026-10-08',
 'local_commands_offline':'case-local-commands-closure-2026-10-08',
 'scheduler_list_candidate_20261010':'case-scheduler-list-candidate-20261010',
 'uart_error_atomic_offline':'case-uart-error-atomic-closure-2026-10-08',
 'uart_receive_offline':'case-uart-receive-closure-2026-10-08',
 'uart_start_offline':'case-uart-start-closure-2026-10-08'}
report['source_candidate_20261010']='case-frame-dispatch-closure-2026-10-08'
classes={
 'HAL_UARTEx_RxEventCallback':'product callback; retained ST weak definition is not evidence for case override',
 'HAL_UART_ErrorCallback':'HAL weak callback candidate; verify selected library revision and product override',
 'HAL_UART_RxCpltCallback':'product callback; frame callback may be related but signature and registration are unproven',
 'case_ack':'case product reply encoder/transport',
 'case_binary_command':'case full binary command dispatch; selected nonlocal/local fragments do not cover it',
 'case_bulk_receive':'HAL synchronous receive and timeout behavior',
 'case_clear_event':'CMSIS clear wrapper and FreeRTOS event group provider',
 'case_control_a':'case hardware/control path',
 'case_control_b':'case hardware/control path',
 'case_disinherit':'FreeRTOS queue mutex priority inheritance',
 'case_enter_critical':'FreeRTOS critical section and nesting context',
 'case_increment_tick':'FreeRTOS tick advancement and delayed-task wake effects',
 'case_event_post':'CMSIS event set wrapper; compare with existing case_event_flags_set ABI before binding',
 'case_exit_critical':'FreeRTOS critical section and nesting context',
 'case_forward_event':'CMSIS event set wrapper; compare with existing case_event_flags_set ABI before binding',
 'case_legacy_command':'case legacy command dispatch',
 'case_mask_restore':'FreeRTOS ISR interrupt-mask restore',
 'case_mask_save':'FreeRTOS ISR interrupt-mask save',
 'case_remove_waiter':'FreeRTOS task/list waiter removal and wake effects',
 'case_resume_scheduler':'FreeRTOS scheduler resume with possible yield',
 'case_scheduler_state':'FreeRTOS scheduler state',
 'case_send':'case UART response transport',
 'case_write_controller_blocking':'CASE lower HAL UART byte write',
 'case_tick_word2':'CASE lower tick getter for UART timeout',
 'case_wait_condition':'CASE lower UART flag wait and timeout',
 'g2_log_printf':'CASE lower diagnostic logger',
 'case_vformat':'CASE lower variadic formatter',
 'log_hex_buffer':'CASE lower diagnostic hex dump',
 'case_suspend_scheduler':'FreeRTOS scheduler suspension',
 'case_uart_dma_boundary':'HAL DMA RX/error continuation; selected comparator excluded DMAR',
 'case_uart_other_irq':'HAL remaining UART IRQ branches beyond selected prefix',
 'case_unblock_waiter':'FreeRTOS event waiter removal/unblock plus event-bit return',
 'case_yield_request':'FreeRTOS pending yield/scheduler request',
 'xEventGroupSetBits':'FreeRTOS task-context event group set; upstream source is version lead only',
 'xEventGroupClearBits':'FreeRTOS task-context event group clear',
 'xEventGroupClearBitsFromISR':'FreeRTOS ISR deferred clear enqueue',
 'xEventGroupGetBitsFromISR':'FreeRTOS ISR event bits snapshot',
 'vEventGroupClearBitsCallback':'FreeRTOS deferred event-group clear callback',
 'xTimerPendFunctionCallFromISR':'FreeRTOS ISR timer command enqueue',
}
blockers={
 'HAL_UARTEx_RxEventCallback':'No retained CASE callback entry binding; vendor weak body alone does not establish selected target override.',
 'HAL_UART_RxCpltCallback':'Frame callback 0x08006544 body exists, but HAL callback relocation/name binding to that entry is not established.',
 'case_ack':'Original child entry 0x080068d0 is a test boundary; reply bytes and send side effects have not been reconstructed.',
 'case_binary_command':'Selected nonlocal/local children exist, but original 0x08000e1c full dispatch and excluded branches remain unbound.',
 'case_bulk_receive':'Original 0x080063ec is a stop-before-entry boundary; timed receive return and buffer mutations are untested.',
 'case_clear_event':'Wrapper 0x0800a7d2 disassembly is retained; full 0x0800c44c kernel clear, ISR path, and ABI integration are missing.',
 'case_control_a':'Original 0x08006b80 is a stop-before-entry hardware/control child.',
 'case_control_b':'Original 0x08006b98 is a stop-before-entry hardware/control child.',
 'case_disinherit':'Original 0x0800cb38 mutex priority state is outside selected queue fixtures.',
 'case_enter_critical':'Original 0x0800bffc critical nesting/state is used in fixtures but no source provider is integrated.',
 'case_exit_critical':'Original 0x0800c014 critical nesting/state is used in fixtures but no source provider is integrated.',
 'case_increment_tick':'Original 0x0800ca78 executes as an authenticated lower peer in resume fixtures; source ownership must cover tick wrap, delayed-list wake and ready/yield effects.',
 'case_legacy_command':'Original 0x08000928 is a stop-before-entry command child.',
 'case_mask_restore':'Original 0x080000fc PRIMASK behavior appears in queue fixtures but separate source provider and all contexts are unverified.',
 'case_mask_save':'Original 0x080000f4 PRIMASK behavior appears in queue fixtures but separate source provider and all contexts are unverified.',
 'case_remove_waiter':'Original 0x0800cba0 list/TCB wake behavior runs as peer in fixtures; source integration requires kernel list/TCB ownership.',
 'case_resume_scheduler':'Original 0x0800cc0c runs as peer; nesting and pending-yield state need coherent source integration.',
 'case_scheduler_state':'Original 0x0800ca4c runs as peer; scheduler global initialization/state not sourced in CASE archive.',
 'case_send':'Original 0x0800680c transport routine stops at child boundary; reply ownership/UART effects missing.',
 'case_write_controller_blocking':'Original 0x080066ac timed UART writer is intercepted by the send comparator; full state machine and hardware behavior remain unsourced.',
 'case_tick_word2':'Original 0x08004eac tick getter is intercepted by the UART writer comparator; source ABI and timing remain to be established.',
 'case_wait_condition':'Original 0x08008ec4 UART flag wait is intercepted by the writer comparator; timeout/peripheral behavior remains unsourced.',
 'g2_log_printf':'Original 0x08009170 logger is intercepted by the send comparator; full formatting and output state remain unsourced in CASE.',
 'case_vformat':'Original 0x08009210 formatter is intercepted by the logger-wrapper comparator; conversion, state and output behavior remain unsourced.',
 'log_hex_buffer':'Original 0x080067c8 hex dump is intercepted by the send comparator; lower logger and output behavior remain unsourced.',
 'case_suspend_scheduler':'Original 0x0800c380 runs as peer; nesting and pending-yield state need coherent source integration.',
 'case_uart_dma_boundary':'Selected UART comparator explicitly excludes DMAR; no original DMA continuation comparison.',
 'case_uart_other_irq':'Selected UART comparator stops before remaining IRQ path; no original full IRQ comparison.',
 'case_unblock_waiter':'Original 0x0800c1cc list/TCB wake path runs as peer; complete source ownership absent.',
 'case_yield_request':'Original 0x0800c0a0 runs as peer; scheduler/PendSV source context absent.',
 'xEventGroupSetBits':'Foundation FreeRTOS V10.5.1 source is a version lead; CASE 0x0800c4de event/list/TCB ABI and scheduler bindings not demonstrated.'}
blockers.update({
 'xEventGroupClearBits':'Original 0x0800c44c kernel clear body retained, but critical nesting/return-before-clear state source integration is absent.',
 'xEventGroupClearBitsFromISR':'Original 0x0800c478 deferred clear enqueue body not fully captured; timer queue command and borrowed event lifetime unbound.',
 'xEventGroupGetBitsFromISR':'Original 0x0800c4cc ISR bits read critical-mask sequence not fully captured as source.'})
blockers.update({
 'vEventGroupClearBitsCallback':'Original callback pointer 0x0800bf85 is authenticated in the clear wrapper, but callback body and deferred lifetime are not source integrated.',
 'xTimerPendFunctionCallFromISR':'Original 0x0800ce0c lower queue command provider is a bounded child call; timer daemon and enqueue state are not source integrated.'})
records=[]
for symbol in symbols:
 callers=[]
 for path in source_root.glob('*/*.c'):
  for no,line in enumerate(path.read_text().splitlines(),1):
   if symbol in line and not (path.parent.name=='uart_error_offline'):
    callers.append({'path':str(path.relative_to(ROOT)),'line':no,'report':f'g2/analysis/{report[path.parent.name]}/REPORT.md'})
 providers=[]
 for base in (ROOT/'g2/components/foundation',ROOT/'g2/components/bootloader'):
  if not base.exists(): continue
  for path in base.rglob('*.c'):
   if symbol in path.read_text(errors='ignore'): providers.append(str(path.relative_to(ROOT)))
 addresses=[]
 import re
 for path in (ROOT/'g2/analysis').glob('case-*/build_offline.py'):
  for match in re.finditer(r'\b'+re.escape(symbol)+r'\s*=\s*(0x[0-9a-fA-F]+)',path.read_text(errors='ignore')):
   addresses.append({'thumb_address':match.group(1),'hook':str(path.relative_to(ROOT))})
 if symbol=='vEventGroupClearBitsCallback':
  addresses.append({'thumb_address':'0x0800bf85','hook':'g2/analysis/case-event-clear-isr-20261010/verify.py'})
 if symbol=='xTimerPendFunctionCallFromISR':
  addresses.append({'thumb_address':'0x0800ce0d','hook':'g2/analysis/case-event-clear-isr-20261010/verify.py'})
 if symbol=='case_increment_tick':
  addresses.append({'thumb_address':'0x0800ca79','hook':'g2/analysis/case-scheduler-list-candidate-20261010/verify_resume.py'})
 records.append({'symbol':symbol,'candidate_callers':callers,'foundation_bootloader_source_matches':providers,'original_address_candidates':addresses,'classification':classes[symbol], 'blocker':blockers[symbol], 'status':'unresolved'})
assert len(records)==len(symbols) and all(r['candidate_callers'] for r in records)
(HERE/'provider-census.json').write_text(json.dumps({'count':len(records),'symbols':records},indent=2)+'\n')
print(len(records),'classified; foundation/bootloader source name matches',sum(bool(r['foundation_bootloader_source_matches']) for r in records))

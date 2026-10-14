#!/usr/bin/env python3
"""Build a non-flashable Cortex-M0+ CASE source candidate from existing bounded sources."""
from pathlib import Path
import subprocess, json, hashlib, shlex, sys
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
REPORT=ROOT/'g2/analysis/case-source-candidate-round2-20261010'
SOURCES=[
 'source_candidate_20261010/evidenced_providers.c', 'source_candidate_20261010/control_providers.c', 'source_candidate_20261010/ack_provider.c', 'source_candidate_20261010/mask_providers.c', 'source_candidate_20261010/scheduler_state.c', 'source_candidate_20261010/yield_request.c', 'source_candidate_20261010/critical_providers.c', 'source_candidate_20261010/suspend_scheduler.c', 'source_candidate_20261010/event_get_isr.c', 'source_candidate_20261010/event_clear_isr.c', 'source_candidate_20261010/event_clear_callback.c', 'source_candidate_20261010/event_clear_task.c', 'binary_forward_offline/forward.c','deferred_consumer_offline/consumer.c',
 'scheduler_list_candidate_20261010/waiter.c',
 'scheduler_list_candidate_20261010/resume.c',
 'scheduler_list_candidate_20261010/tick.c',
 'scheduler_list_candidate_20261010/disinherit.c',
 'scheduler_list_candidate_20261010/unblock.c',
 'source_candidate_20261010/send_provider.c',
 'source_candidate_20261010/hex_log_provider.c',
 'source_candidate_20261010/log_wrapper_provider.c',
 'source_candidate_20261010/uart_write_provider.c',
 'source_candidate_20261010/tick_word_provider.c',
 'source_candidate_20261010/uart_wait_provider.c',
 'source_candidate_20261010/uart_read_provider.c',
 'source_candidate_20261010/uart_event_callback.c',
 'source_candidate_20261010/uart_rx_complete_callback.c',
 'source_candidate_20261010/timer_pend_export.c','event_flags_offline/events.c',
 'source_candidate_20261010/event_set_task.c','frame_callback_offline/frame.c',
 'frame_dispatch_offline/dispatch.c','local_commands_offline/local.c',
 'uart_error_atomic_offline/uart.c',
 'source_candidate_20261010/uart_irq_continuations.c',
 'source_candidate_20261010/uart_irq_toidle_dma.c',
 'source_candidate_20261010/uart_irq_toidle_no_dma.c',
 'source_candidate_20261010/uart_irq_mixed_tail.c',
 'source_candidate_20261010/dma_abort_provider.c',
 'source_candidate_20261010/tx_complete_provider.c',
 'uart_receive_offline/receive.c',
 'uart_start_offline/start.c']
SOURCES += [
 'startup_candidate_20261011/application_boot_sensor_simple_callbacks_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_stream_callbacks_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_callback_finish_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_bind_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_bind_core_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_finish_guard_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_finish_probe_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_finish_reset_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_finish_signal_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_finish_signal_isr_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_finish_signal_task_candidate.c',
 'startup_candidate_20261011/application_boot_sensor_open_ready_candidate.c',
 'startup_candidate_20261011/application_policy_adc_register_candidate.c',
 'startup_candidate_20261011/application_policy_event_scheduler_helpers_candidate.c',
 'startup_candidate_20261011/application_policy_sleep_exit_candidate.c',
 'startup_candidate_20261011/application_policy_scheduler_primitives_candidate.c',
 'startup_candidate_20261011/application_policy_task_message_special_candidate.c',
 'startup_candidate_20261011/application_policy_task_queue_candidate.c',
 'startup_candidate_20261011/application_boot_pool_wake_waiter_candidate.c',
 'startup_candidate_20261011/application_policy_wake_cleanup_candidate.c',
 'startup_candidate_20261011/application_policy_tick_candidate.c',
 'startup_candidate_20261011/application_policy_message_copy_candidate.c',
 'startup_candidate_20261011/application_policy_task_notify_resume_candidate.c',
 'startup_candidate_20261011/event_set_callback_candidate.c',
]
# The native-backed public command and formatter graph is now selected as C
# source. The full graph is compiled here so archive/member provenance and
# unresolved-symbol accounting cover the actual public providers.
SOURCES += [str(p.relative_to(HERE.parent)) for p in
            sorted((HERE.parent/'legacy_default_candidate_20261010').glob('*.c'))]
SOURCES += ['semantic_strings_candidate_20261011/case_semantic_strings.c']
CLANG='/usr/bin/clang'; AR='/opt/homebrew/bin/arm-none-eabi-ar'; NM='/opt/homebrew/bin/arm-none-eabi-nm'; LD='/opt/homebrew/bin/arm-none-eabi-ld'
FLAGS=['--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-mfloat-abi=soft','-std=c11','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-Wall','-Wextra']
OUT=HERE/'build'; OUT.mkdir(exist_ok=True)
receipts=[]; objects=[]
for rel in SOURCES:
 src=HERE.parent/rel; obj=OUT/(rel.replace('/','__')+'.o')
 dep=OUT/(rel.replace('/','__')+'.d')
 cmd=[CLANG,*FLAGS,'-MD','-MF',str(dep),'-c',str(src),'-o',str(obj)]
 run=subprocess.run(cmd,text=True,capture_output=True)
 deps=dep.read_text().replace('\\\n',' ').split(':',1)[1].split() if run.returncode==0 else []
 receipts.append({'source':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'command':shlex.join(cmd),'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'dependencies':[{'path':str(Path(d).resolve().relative_to(ROOT)) if Path(d).resolve().is_relative_to(ROOT) else str(Path(d).resolve()),'sha256':hashlib.sha256(Path(d).read_bytes()).hexdigest()} for d in deps]})
 if run.returncode: raise SystemExit(json.dumps(receipts[-1],indent=2))
 objects.append(obj)
archive=OUT/'libcase_source_candidate.a'
archive.unlink(missing_ok=True)
cmd=[AR,'rcsD',str(archive),*[str(x) for x in objects]]
run=subprocess.run(cmd,text=True,capture_output=True)
if run.returncode: raise SystemExit(run.stderr)
first_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
archive.unlink()
rebuild=subprocess.run(cmd,text=True,capture_output=True)
if rebuild.returncode: raise SystemExit(rebuild.stderr)
second_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
if first_hash!=second_hash: raise SystemExit('nondeterministic archive rebuild')
relocatable=OUT/'case_source_candidate.o'
cmdld=[LD,'-r','--whole-archive',str(archive),'--no-whole-archive','-o',str(relocatable)]
linked=subprocess.run(cmdld,text=True,capture_output=True)
if linked.returncode: raise SystemExit(linked.stderr)
cmdnm=[NM,'-A','-g',*[str(x) for x in objects]]
nm=subprocess.run(cmdnm,text=True,capture_output=True,check=True).stdout
(REPORT/'nm.txt').write_text(nm)
provides=set(); needs=set()
for line in nm.splitlines():
 parts=line.split()
 if len(parts)<3: continue
 typ,sym=parts[-2:]
 if typ=='U': needs.add(sym)
 elif typ.upper() in ('T','D','B','R','C','W'): provides.add(sym)
link_undefined={line.split()[-1] for line in subprocess.run([NM,'-u',str(relocatable)],text=True,capture_output=True,check=True).stdout.splitlines() if line.split()}
if link_undefined != needs-provides: raise SystemExit('relocatable undefined symbols differ from member census')
receipt={'target':'arm-none-eabi cortex-m0plus thumb soft float','python_interpreter':sys.executable,'python_version':sys.version.split()[0],'tool_versions':{x:subprocess.run([v,'--version'],capture_output=True,text=True).stdout.splitlines()[0] for x,v in [('clang',CLANG),('ar',AR),('nm',NM),('ld',LD)]},'tool_sha256':{x:hashlib.sha256(Path(v).read_bytes()).hexdigest() for x,v in [('clang',CLANG),('ar',AR),('nm',NM),('ld',LD)]},'flags':FLAGS,'sources':receipts,'archive':str(archive.relative_to(ROOT)),'archive_sha256':second_hash,'archive_rebuild_same_sha256':first_hash==second_hash,'archive_command':shlex.join(cmd),'relocatable':str(relocatable.relative_to(ROOT)),'relocatable_sha256':hashlib.sha256(relocatable.read_bytes()).hexdigest(),'relocatable_command':shlex.join(cmdld),'nm_command':shlex.join(cmdnm),'provided_symbols':sorted(provides),'unresolved_symbols':sorted(needs-provides),'source_count':len(SOURCES),'object_count':len(objects),'source_complete':False,'limits':['Public CASE command and formatter source is selected with bounded native/C evidence.','Malformed pointers and unbounded formatter width/precision/callback behavior lack full stock equivalence proof.','Product linker placement and physical flash, PMIC, reset, sensor and transport effects are not validated.']}
(REPORT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'source_count':len(SOURCES),'provided':len(provides),'unresolved':receipt['unresolved_symbols']},indent=2))

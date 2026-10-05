#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Snapshot source/targets and deduplicate original trace bytes by payload+PC."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ledger={};evidence=[]
def add(payload,trace):
 count=0
 if isinstance(trace,dict):items=[{'pc':pc,'bytes':raw} for pc,raw in trace.items()]
 else:items=trace
 for x in items:
  pc=x['pc'];pc=int(pc,0) if isinstance(pc,str) and pc.startswith('0x') else int(pc)
  for i,b in enumerate(bytes.fromhex(x['bytes'])):
   key=(payload,pc+i)
   if key in ledger:assert ledger[key]==b,(key,ledger[key],b)
   else:ledger[key]=b;count+=1
 return count

def evidence_add(path,payload,extract):
 p=ROOT/path;d=json.loads(p.read_text());before=len(ledger);previous=set(ledger);assert d['status']=='PASS'
 for trace in extract(d):add(payload,trace)
 if '/radio-timer-stop-simulator/' in path:
  (OUT/'new-code-evidence.jsonl').write_text(''.join(json.dumps(dict(payload=k[0],address=hex(k[1]),byte=ledger[k],evidence=path))+'\n' for k in sorted(set(ledger)-previous)))
 evidence.append(dict(path=path,sha256=sha(p),new_unique_trace_bytes=len(ledger)-before,payload=payload,status=d['status']))
evidence_add('g2/build/foundation/touch-scb-trigger-final/comparison-reviewed.json','touch',lambda d:[c['original']['trace'] for name in ['comparison_cases','fifo_comparison_cases','tx_comparison_cases'] for c in d[name]])
evidence_add('g2/analysis/touch-mmio-cycle-2026-10-05/next-fifo/results.json','touch',lambda d:[c['executed_original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/ambiq-mspi-simulator/comparison-heldout.json','apollo_main',lambda d:[c['original']['trace'] for c in d['cases']])
evidence_add('g2/build/foundation/ambiq-critical-simulator/comparison-interface-final.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/ambiq-gpio-simulator/comparison-final.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/radio-gpio-simulator/comparison-reviewed.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/wsf-radio-simulator/comparison-final.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/event-group-wsf-simulator/comparison-first.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/timer-queue-wsf-simulator/comparison-reviewed.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/timer-daemon-wsf-simulator/comparison-final.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/rtos-ready-wsf-simulator/comparison-final.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/rtos-resume-wsf-simulator/comparison-final.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/rtos-tick-wsf-simulator/comparison-verified.json','apollo_main',lambda d:[c['original_trace'] for c in d['cases']])
evidence_add('g2/build/foundation/ambiq-gpio-config-simulator/comparison-reviewed.json','apollo_main',lambda d:[d['original_trace']])
evidence_add('g2/build/foundation/ambiq-gpio-board-simulator/comparison-first.json','apollo_main',lambda d:[d['original_trace']])
evidence_add('g2/build/foundation/radio-gpio-control-simulator/control-comparison-reviewed.json','apollo_main',lambda d:[d['original_trace']])
evidence_add('g2/build/foundation/radio-timer-stop-simulator/timer-comparison-first.json','apollo_main',lambda d:[d['original_trace']])
counts={p:sum(k[0]==p for k in ledger) for p in ['touch','apollo_main']}
sources=[]
for p in sorted((ROOT/'g2/components/foundation').rglob('*')):
 if p.suffix not in ['.c','.h']:continue
 rel=str(p.relative_to(ROOT));ignored=subprocess.run(['git','check-ignore','--no-index',rel],capture_output=True).returncode==0
 sources.append(dict(path=rel,sha256=sha(p),bytes=p.stat().st_size,role='simulator-entry-or-seam' if '/simulator/' in rel else 'implementation' if p.suffix=='.c' else 'interface-or-compatibility',ignored=ignored))
targets=[]
for name,path,providers in [
 ('ambiq-gpio-config-simulator','g2/build/foundation/radio-timer-stop-simulator/gpio_config.elf','Pinned GPIO plus WSF timer stop/unlink and actual stock port; reconstructed timer-to-GPIO shutdown slice, actual PRIMASK, synthetic raw MMIO state with preserved ordering and final-state model; physical pinmux/clock/NVIC/board sequencing remain unproven'),
 ('rtos-tick-wsf-simulator','g2/build/foundation/rtos-tick-wsf-simulator/rtos_tick_wsf.elf','Actual tick expiry/defer/rollover plus resume/ready and prior radio chain; newtick/resume/list O0 simulator profile; tick ISR/startup/task selection/context switch remain external'),
 ('rtos-resume-wsf-simulator','g2/build/foundation/rtos-resume-wsf-simulator/rtos_resume_wsf.elf','Actual nested suspend/resume and pending-ready drain, deferred tick replay and PendSV requests; tick expiry/selection/context switch remain external'),
 ('rtos-ready-wsf-simulator','g2/build/foundation/rtos-ready-wsf-simulator/rtos_ready_wsf.elf','Actual ordered event-list removal and ready/pending insertion; pending drain/selection/suspend/resume remain fixtures'),
 ('touch-scb-simulator','g2/build/foundation/touch-scb-trigger-final/touch_scb.elf','Touch RX/TX/trigger + callable entry; synthetic MMIO'),
 ('ambiq-mspi-simulator','g2/build/foundation/ambiq-cmdq-regression/ambiq_mspi.elf','MSPI interrupt/lifecycle; synthetic CQ and delay'),
 ('ambiq-cmdq-simulator','g2/build/foundation/ambiq-critical-cq-regression/ambiq_mspi.elf','Real MSPI/CMDQ, synthetic critical-enter/delay'),
 ('ambiq-critical-simulator','g2/build/foundation/ambiq-critical-simulator/ambiq_mspi.elf','Real MSPI/CMDQ/PRIMASK, synthetic delay'),
 ('ambiq-gpio-simulator','g2/build/foundation/ambiq-gpio-simulator/ambiq_gpio.elf','Real GPIO IRQ/register/service/PRIMASK, synthetic callbacks and W1C'),
 ('radio-gpio-simulator','g2/build/foundation/radio-gpio-simulator/radio_gpio.elf','Radio pin117 register, GPIO bank3 ISR and actual reconstructed counter/event consumer; synthetic scheduler submission and W1C'),
 ('wsf-radio-simulator','g2/build/foundation/wsf-radio-simulator/wsf_radio.elf','Real WSF producer/critical/wake/dispatcher and linked radio/GPIO; synthetic RTOS/queue/timer/app providers'),
 ('timer-daemon-wsf-simulator','g2/build/foundation/timer-daemon-wsf-simulator/timer_daemon_wsf.elf','Real nonblocking receive/copy/negative daemon and task critical plus prior radio/WSF/EventGroup/queue; scheduler/providers remain fixtures'),
 ('timer-queue-wsf-simulator','g2/build/foundation/timer-queue-wsf-simulator/timer_queue_wsf.elf','Real queue ISR producer/copy/BASEPRI plus event-group/WSF/radio/GPIO; synthetic scheduler/consumer/daemon'),
 ('event-group-wsf-simulator','g2/build/foundation/event-group-wsf-simulator/event_group_wsf.elf','Real event-group task setter/ISR deferred wrapper/callback and WSF/radio/GPIO; synthetic scheduler/queue copy/wait/app providers')]:
 p=ROOT/path;nm=subprocess.run(['arm-none-eabi-nm',str(p)],capture_output=True,text=True,check=True)
 targets.append(dict(target=name,elf=path,sha256=sha(p),global_text_symbols=[line.split()[-1] for line in nm.stdout.splitlines() if len(line.split())==3 and line.split()[1]=='T'],provider_limits=providers,production_firmware=False))
result=dict(source_files=sources,source_file_count=len(sources),implementation_c_count=sum(x['role']=='implementation' for x in sources),interface_header_count=sum(x['role']=='interface-or-compatibility' for x in sources),simulator_c_count=sum(x['role']=='simulator-entry-or-seam' for x in sources),callable_targets=targets,unique_original_trace_bytes=counts,unique_original_trace_total=len(ledger),evidence_inputs=evidence,new_unique_timer_stop_trace_bytes=evidence[-1]["new_unique_trace_bytes"],additional_gpio_static_unreachable_bytes=6,new_exact_compiled_match_bytes_this_cycle=0,prior_critical_exact_compiled_match_bytes=8,fully_blob_free_firmware_payloads=0,source_built_byte_identical_bundle_proven=False,limits=['Source/target counts do not measure firmware completeness; variants share many source functions.','Counts use unique payload identity+runtime byte address and verify identical overlapping byte values; shared critical/lifecycle/CMDQ bodies counted once.','Touch standalone trace includes trapped BKPT observation; this is not completed-path/hardware proof.','GPIO6 unreachable bytes are static evidence, excluded from trace counts.','Failed scatter decoder diagnostic excluded; static decoded ITCM24 bytes excluded from stored original execution count.','Snapshot only; historical evidence retains its own compiler/source hash limits.'])
(OUT/'cumulative-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(source_files=len(sources),implementation_c=result['implementation_c_count'],headers=result['interface_header_count'],simulator_c=result['simulator_c_count'],trace_bytes=counts,total=len(ledger),increments=[(x['path'],x['new_unique_trace_bytes']) for x in evidence]),indent=2))

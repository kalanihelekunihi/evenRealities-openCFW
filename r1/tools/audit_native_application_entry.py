#!/usr/bin/env python3
"""Audit application entry control flow, explicit provider fixtures and reuse evidence."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-application-entry';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();bp=BASE/'native-application-startup-runtime/report.json';bundle=read(bp)
 expected=['ble_dfu_buttonless_async_svci_init','cm_backtrace_init','nrf_drv_clock_init','nrf_log_default_backends_init','nrf_log_frontend_std_0','nrf_log_init','r1_adc_error','r1_boot_ctor_run','r1_device_module_init','r1_peripheral_module_init','r1_reset_reason_nordic_adapter','r1_structured_log_format','r1_structured_log_mode_get']
 assert r['comparisons']==27648 and r['trace_sha256']=='80002fa28a387751eb7de6b14839a4015618b40d9d636b8129dc5ca42b4c842e'
 counts={name:27648 for name in expected};counts.update(r1_adc_error=138240,r1_structured_log_mode_get=69120,r1_structured_log_format=20736,nrf_log_frontend_std_0=13824,initialized_callback=27648);assert r['call_counts']==counts
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_application_entry.py') and r['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a' and r['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
 assert r['report_sha256']==sha(rp) and r['object_sha256']==sha(OUT/'native_application_entry.o')==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout'])
 assert r['unresolved_source_providers']==e['unresolved_imports']==sorted(report['units'][0]['undefined'])==bundle['undefined_symbols']==expected and not r['runtime_no_unresolved'] and not r['provider_executable_bodies_supplied'] and not r['initialized_callback_source_owned'] and not r['instruction_identity']
 for flag in ['provider_and_initialized_callback_fixtures','source_application_entry_body','candidate_native_body_execution_forbidden','all_three_status_success_error_combinations','mode_queue_triples_zero_to_seven','two_scr_initial_states','three_post_callback_fatal_iterations','typed_call_arguments_order_mmio_write_and_nonstack_ram_checked','callback_pointer_relocation_normalized','unicorn_memory_write_hooks_disabled']:assert r[flag]
 for data in [report,bundle]:
  for p,h in data['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 assert bundle['provider_reports']=={p:sha(BASE/p) for p in ['native-application-entry/report.json','native-scatter-runtime/report.json']} and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in e['ghidra'].items():assert sha(OUT/p)==h,p
 for a,n in [(0x75f64,146),(0x75ff8,144)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 assert e['rea_sha256']==sha(OUT/'rea-75f64.json');rea=read(OUT/'rea-75f64.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['error']['code']=='invalid_request' and 'No procedure exists' in str(rea)
 assert e['native_body_bytes']==146 and e['source_configuration_bytes']==r['source_numeric_and_string_bytes']==144 and not e['provider_source_integration_verified'] and not e['initialized_callback_source_owned'] and not e['locked_ownership_changed']
 assert e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv')
 from audit_source_frontier import section_bytes
 for name,a,n in [('scr',0x75ff8,4),('version',0x75ffc,12),('hardware',0x76008,12),('build',0x76014,44),('ring',0x76040,32),('log_bounds',0x76060,8),('sdk',0x76068,28),('callback_cell',0x76084,4)]:assert section_bytes(OUT/'native_application_entry.o','.r1.app.entry.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 label=read(OUT/'mode-queue-label-clarification.json');initial=read(OUT/'initial-mode-label-verification.json');assert e['mode_label_clarification_sha256']==sha(OUT/'mode-queue-label-clarification.json') and e['initial_mode_receipt_sha256']==label['initial_receipt_sha256']==sha(OUT/'initial-mode-label-verification.json') and label['actual_mode_get_calls']==69120 and initial['trace_sha256']==r['trace_sha256']==label['trace_sha256'] and 'all_three_mode_values_zero_to_seven' not in r
 reuse=read(OUT/'upstream-backtrace-reuse.json');assert reuse['manifest_sha256']==sha(ROOT/'third-party/fetched/manifest.json') and reuse['source_sha256']==sha(ROOT/reuse['source'])==reuse['provider']['source_sha256'] and reuse['license_sha256']==sha(ROOT/reuse['license']) and reuse['provider']['license']=='MIT' and not reuse['provider']['exact_vendor_checkout_proven'] and not reuse['application_entry_integration_verified']
 assert subprocess.check_output(['git','-C',str(ROOT/reuse['provider']['path']),'rev-parse','HEAD'],text=True).strip()==reuse['observed_checkout']==reuse['provider']['commit']
 print('Source application entry authenticated with27648 typed provider-fixture cases;13 imports, callback ownership, raw ABI and image integration remain open')
if __name__=='__main__':audit()

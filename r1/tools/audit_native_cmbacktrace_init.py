#!/usr/bin/env python3
"""Authenticate upstream CMB initializer behavior and bounded source integration."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-cmbacktrace-init';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');report=read(OUT/'report.json');e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes()
 assert r['comparisons']==10240 and r['source_copy_calls_per_side']==30720 and r['error_log_calls_per_side']==2048 and r['trace_sha256']=='83e2dd2d8c274d178b37f22faa135cd0a177f33c7078f550fecf30d5a1c4e3ae'
 for flag in ['full_nonstack_ram_write_order_copy_args_callee_integer_and_stack_checked','executed_store_observer_with_full_ram_reconciliation','source_upstream_init_and_source_copy_provider','upstream_unmodified','retained_error_logger_fixture','error_log_pointer_content_normalized','linker_bound_values_are_explicit_fixtures','canonical_bound_case_present','zero_stack_and_zero_code_distinguished','wrapped_range_cases','prior_init_flag_sticky_on_error','array_twenty_first_bytes_preserved','raw_void_return_not_equivalence_claim','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['raw_r0_equal'] and not r['instruction_identity'] and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_cmbacktrace_init.py') and r['report_sha256']==sha(OUT/'report.json') and r['runtime_object_sha256']==report['linked_sha256']==sha(OUT/'cmbacktrace-init-runtime.o') and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app) and r['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 assert report['upstream_source_sha256']==sha(ROOT/report['upstream_source'])=='6e444224af3ef223067849b88f61281ec0661e3f38425e84758bf12be057e01c' and report['upstream_license_sha256']==sha(ROOT/report['upstream_license']) and report['upstream_commit']=='73714489f9d8af130aacb515586b397b604a5768' and not report['exact_vendor_checkout_proven'] and report['full_upstream_translation_unit_compiled'] and not report['application_linked'] and not report['original_instruction_identity']
 assert subprocess.check_output(['git','-C',str((ROOT/report['upstream_source']).parents[1]),'rev-parse','HEAD'],text=True).strip()==report['upstream_commit']
 for unit in report['units']:
  assert '-O0' in unit['command'] and '-fno-inline' in unit['command'] and sha(ROOT/unit['source'])==unit['source_sha256'];name='cm_backtrace.o' if 'cm_backtrace.c' in unit['source'] else 'copy_port.o';assert sha(OUT/name)==unit['object_sha256']
 assert report['selected_object_sha256']==sha(OUT/'cmbacktrace-init.o') and report['provider_object_sha256']==sha(BASE/'native-libc-sequences/native_libc_sequences.o')
 for p,h in report['provider_reports'].items():assert sha(BASE/p)==h
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h
 for a,n in [(0x588a4,84),(0x588f8,28),(0x9cabc,4),(0xc37f4,98)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 rea=read(OUT/'rea-588a4.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['error']['code']=='invalid_request' and 'No procedure exists' in str(rea)
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['native_body_bytes']==84 and e['native_literal_bytes']==28 and not e['whole_image_identity']
 bp=BASE/'native-cmbacktrace-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-cmbacktrace-runtime.o') and len(bundle['application_imports_resolved'])==12 and bundle['remaining_application_imports']==['ble_dfu_buttonless_async_svci_init'] and len(bundle['undefined_symbols'])==68 and not bundle['full_provider_execution_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-cmbacktrace-runtime.o')[0]==bundle['undefined_symbols'] and 'r1_retained_log_printf_sink' in bundle['undefined_symbols'] and not any(s.startswith('r1_cmb_') for s in bundle['undefined_symbols'])
 print('Upstream CMB initializer authenticated:10240 cases; twelve direct app imports source-linked; DFU/68 total imports and raw ABI/image gates remain')
if __name__=='__main__':audit()

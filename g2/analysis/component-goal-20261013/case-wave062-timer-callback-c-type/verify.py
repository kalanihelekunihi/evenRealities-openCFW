from pathlib import Path
import json,hashlib,subprocess,shutil,tempfile
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;B=H.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();S=R/'g2/components/case/startup_candidate_20261011';changes=json.loads((H/'source-changes.json').read_text());names=['9d70','bb4c','9684','b7ec','bb90','ab70']
header=H/'callback-contract.h';header.write_text('#include <stdint.h>\ntypedef void (*case_timer_callback_contract)(uint32_t);\n'+''.join(f'extern void case_boot_transport_cb_{n}(uint32_t);\n_Static_assert(__builtin_types_compatible_p(__typeof__(&case_boot_transport_cb_{n}),case_timer_callback_contract), "callback type mismatch");\n' for n in names));checks=[]
for row in changes:
 p=R/row['path'];assert sha(p)==row['after_sha256'];before=H/'before'/p.name;assert sha(before)==row['before_sha256']
 cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-std=c11','-ffreestanding','-Wall','-Wextra','-Werror','-fsyntax-only','-I',str(S),'-include',str(header)]
 good=subprocess.run(cmd+[str(p)],capture_output=True,text=True);bad=subprocess.run(cmd+[str(before)],capture_output=True,text=True)
 assert good.returncode==0,good.stderr;assert bad.returncode!=0 and 'conflicting types for' in bad.stderr,bad.stderr
 checks.append(dict(source=row['path'],corrected_pass=True,original_rejected_incompatible_callback_type=True,original_diagnostic=bad.stderr))
assert sha(H/'final/case.elf')==sha(B/'case-wave039-list-cursor-contract/final/case.elf')
fixture=Path(tempfile.mkdtemp(prefix='case062-affected-tests-'));rel=B.relative_to(R);fb=fixture/rel
native=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';dest=fixture/native.relative_to(R);dest.parent.mkdir(parents=True);shutil.copyfile(native,dest)
elf=fb/'case-wave039-list-cursor-contract/final/case.elf';elf.parent.mkdir(parents=True);shutil.copyfile(H/'final/case.elf',elf)
reproductions=[]
for n,slug in [(56,'timer-trampoline-binding'),(57,'timer-registration-lifetime'),(58,'registered-timer-delete')]:
 source=B/f'case-wave{n:03d}-{slug}'/'check.py';target=fixture/source.relative_to(R);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
for n,slug in [(56,'timer-trampoline-binding'),(57,'timer-registration-lifetime'),(58,'registered-timer-delete')]:
 target=fb/f'case-wave{n:03d}-{slug}'/'check.py'
 #056 validates historical catalogue exclusion as well as trampoline; pin it.
 catalogue=R/'g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl';cp=fixture/catalogue.relative_to(R);cp.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(catalogue,cp)
 run=subprocess.run(['/tmp/iar-c-runtime-venv/bin/python',str(target)],capture_output=True,text=True);assert run.returncode==0,run.stderr;out=H/f'affected-wave{n:03d}.json';shutil.copyfile(target.parent/'verification.json',out);reproductions.append(dict(wave=n,status=run.stdout.strip(),test_script_sha256=sha(target),result_sha256=sha(out),fixture_ELF_sha256=sha(elf)))
r=dict(status='PASS_SOURCE_CALLBACK_C_TYPE_REPAIR_AND145_AFFECTED_PAIRS',source_type_checks=checks,affected_tests=reproductions,source_ELF_sha256=sha(H/'final/case.elf'),whole_ELF_byte_identical_to_CASE039=True,build_source_units=401,limits=['Corrected compatible C type; ignored argument preserves native ABI and behavior','Whole source ELF identical to039, not equal to locked native firmware; no native coverage/physical acceptance promotion','Entry-cut comparisons do not prove callback bodies or asynchronous lifetime'])
(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['source_ELF_sha256'])

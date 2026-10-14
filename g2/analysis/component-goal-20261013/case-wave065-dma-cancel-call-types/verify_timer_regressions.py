from pathlib import Path
import json,hashlib,subprocess,shutil,tempfile
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;B=H.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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
(H/'timer-regressions.json').write_text(json.dumps(dict(status='PASS145_AFFECTED_TIMER_REGRESSIONS',tests=reproductions),indent=2)+'\n');print('PASS145_AFFECTED_TIMER_REGRESSIONS')

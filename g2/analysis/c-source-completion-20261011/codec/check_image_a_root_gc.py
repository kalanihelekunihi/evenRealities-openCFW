#!/usr/bin/env python3
"""Check section GC against all authenticated selected image-A code/table roots."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
TOOL=ROOT/'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
BIN=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
LD=Path(__file__).with_name('image_a_root_gc_probe.ld')

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--closure',type=Path,required=True);p.add_argument('--eligibility',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 c=json.loads(a.closure.read_text());sha=hashlib.sha256(a.candidate.read_bytes()).hexdigest();assert c['candidate_sha256']==sha
 needed={s['section'] for s in c['all_source_roots_closure']['sections']};all_sections={s['section'] for s in c['all_alloc_progbits']['sections']};excluded=sorted(all_sections-needed)
 obj=a.output/'root-gc.o';cmd=['docker','run','--rm','--network=none','--read-only','--platform','linux/amd64','--mount',f'type=bind,src={TOOL},dst=/tool,readonly','--mount',f'type=bind,src={ROOT},dst=/repo,readonly','--mount',f'type=bind,src={a.output.resolve()},dst=/out','--tmpfs','/tmp:rw','opencfw/iar-base:10.10.2-local','/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-r','-Wl,--gc-sections','-Wl,-e,gx8002_resident_reset_entry_23500','-Wl,-A,ck803',f'-Wl,-T,/repo/{LD.relative_to(ROOT)}',f'/repo/{a.candidate.resolve().relative_to(ROOT)}','-o','/out/root-gc.o'];run=subprocess.run(cmd,capture_output=True,text=True);assert run.returncode==0,run.stderr[-1500:]
 sections=subprocess.check_output([str(BIN/'csky-elfabiv2-readelf'),'-SW',str(obj)],text=True);preserved={m[1] for line in sections.splitlines() if (m:=re.search(r'^\s*\[\s*\d+\]\s+(\S+)\s+',line))};survivors=sorted(set(excluded)&preserved);assert not survivors
 sym=subprocess.check_output([str(BIN/'csky-elfabiv2-nm'),str(obj)],text=True);actual={line.split()[-1] for line in sym.splitlines() if line.split()};e=json.loads(a.eligibility.read_text());expected={d['name'] for slot in e['native_function_slots'] for d in slot['direct_symbols']};missing=sorted(expected-actual);assert not missing
 und=subprocess.check_output([str(BIN/'csky-elfabiv2-nm'),'-u',str(obj)],text=True);undefined=sorted({line.split()[-1] for line in und.splitlines() if line.split()})
 out={'candidate_sha256':sha,'linker_sha256':hashlib.sha256(LD.read_bytes()).hexdigest(),'gc_object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'source_root_reachable_sections':len(needed),'selected_alloc_sections':len(all_sections),'discarded_sections':excluded,'discarded_count':len(excluded),'discarded_raw_bytes':sum(s['bytes'] for s in c['all_alloc_progbits']['sections'] if s['section'] in excluded),'native_direct_symbols_preserved':len(expected),'native_direct_symbols_missing':missing,'undefined_symbols_after_gc':undefined,'limits':['This proves selected source-root relocation GC behavior, not absence of unmodelled stock indirect entry paths.','The roots include named XIP and resident bodies, vector/reset and every source-owned gx8002 product/registration section.','Final nonrelocatable XIP/SRAM linker placement, loader copy, runtime alias and hardware behavior are not established.']}
 (a.output/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print({k:out[k] for k in ('discarded_count','discarded_raw_bytes','native_direct_symbols_preserved','undefined_symbols_after_gc')})
if __name__=='__main__':main()

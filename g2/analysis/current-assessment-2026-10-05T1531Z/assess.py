#!/usr/bin/env python3
"""Re-run the saved coverage definitions into a NEW directory on the authorized Mac.
No generator, decompiler, compiler, device or shared campaign mutation is invoked.
"""
from pathlib import Path
import argparse,subprocess,importlib.util,json,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,help='New output directory under g2/build/audits');args=parser.parse_args();out=Path(args.output).resolve();assert out.is_relative_to(ROOT/'g2/build/audits'),out;out.mkdir(parents=True,exist_ok=False)
oldout=str(ROOT/'g2/build/audits/2026-10-05T1531Z-current')
for p in (HERE/'methods').glob('*.py'):
 source=p.read_text().replace(oldout,str(out));(out/p.name).write_text(source)
def run(name,*extra):
 p=subprocess.run(['python3',str(out/name),*map(str,extra)],capture_output=True,text=True);(out/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
run('measure.py',out);run('bundle_metrics.py',out)
s=importlib.util.spec_from_file_location('repair',out/'review_repair.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);assert m.fixtures()==12;m.repair(out,out/'repaired')
run('instruction_measure.py',out);run('freeze_and_finish.py');run('app_text_measure.py')
review=json.loads((out/'repaired/summary.json').read_text());inst=json.loads((out/'instruction-metrics.json').read_text());print(json.dumps({'snapshot':str(out),'cutoff':review['snapshot_scan_utc'],'reviewed_bytes':review['bundle_reviewed_bytes'],'assembly_export_bytes':inst['current_combined_instruction_export_bytes'],'baseline':'00:13:53 UTC audit','limit':'Stored-byte evidence footprints, not whole-code or semantic completion. Current source/build/classification/upstream report must be re-evaluated separately if inputs change.'},indent=2))

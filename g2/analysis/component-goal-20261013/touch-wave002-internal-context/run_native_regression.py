#!/usr/bin/env python3
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[4]
OUTPUT=Path(__file__).resolve().parent
p=ROOT/"g2/analysis/touch-active-timer-closure-2026-10-08/verify.py"
sys.argv=[str(p),str(OUTPUT/"active-timer.elf" )]
s=p.read_text().replace("(D/'results.json').write_text", "(OUTPUT/'native-regression.json').write_text")
s=s.replace('[0,1,2]','[0,1]').replace('vals[0]==vals[1]==vals[2]','vals[0]==vals[1]').replace('vals==[1,1,1]','vals==[1,1]')
exec(compile(s,str(p),'exec'),{'__file__':str(p),'OUTPUT':OUTPUT})
f=OUTPUT/'native-regression.json';r=json.loads(f.read_text());r['validation_modes']['active_setter_and_null']='Two-way stock/selected-C; optional separately compiled public comparator is absent from this selected archive and excluded.';r['harness_adaptation']='Only output redirected and absent public comparator removed; original/source domains retained.';f.write_text(json.dumps(r,indent=2)+'\n')

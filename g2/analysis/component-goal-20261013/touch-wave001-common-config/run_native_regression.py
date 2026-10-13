#!/usr/bin/env python3
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[4]
OUTPUT=Path(__file__).resolve().parent
p=ROOT/"g2/analysis/touch-all-slot-closure-2026-10-08/verify.py"
sys.argv=[str(p),str(OUTPUT/"all-slots.elf" )]
s=p.read_text().replace("(D/'results.json').write_text", "(OUTPUT/'native-regression.json').write_text")
exec(compile(s,str(p),'exec'),{'__file__':str(p),'OUTPUT':OUTPUT})

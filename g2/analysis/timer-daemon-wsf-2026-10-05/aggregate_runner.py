#!/usr/bin/env python3
"""Run unchanged Makefile core modules with exact success/error/skip counts."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
text=(ROOT/'Makefile').read_text()
block=re.search(r'CORE_TESTS := (.*?)(?=\n\n)',text,re.S).group(1)
names=block.replace('\\\n',' ').split()
class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.passed=0
    def addSuccess(self,test):super().addSuccess(test);self.passed+=1
records=[]
for name in names:
    print('MODULE '+name,flush=True)
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=name+'.py',top_level_dir=str(ROOT))
    r=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    records.append({'module':name,'tests_run':r.testsRun,'passed':r.passed,'failed':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),'skip_details':[{'test':str(t),'reason':why} for t,why in r.skipped]})
    (ROOT/'build/foundation/timer-daemon-wsf-simulator/aggregate.json').write_text(json.dumps({'modules':records,'total_modules':len(names),'completed_modules':len(records),'totals':{k:sum(x[k] for x in records) for k in ['tests_run','passed','failed','errors','skipped']},'unrun_modules':names[len(records):]},indent=2)+'\n')
sys.exit(1 if any(x['failed'] or x['errors'] for x in records) else 0)

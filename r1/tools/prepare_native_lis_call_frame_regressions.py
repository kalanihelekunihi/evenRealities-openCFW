#!/usr/bin/env python3
"""Prepare full-runtime copies for the three direct LIS regression drivers."""
import hashlib,json,shutil
from pathlib import Path
from build_native_lis_registers import FUNCTIONS
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 base=BASE/'native-lis-call-frames';report=json.loads((base/'report.json').read_text());runtime=base/'native-lis-call-frames-runtime.o';assert sha(runtime)==report['linked_sha256'];prepared={}
 for key,objname in [('registers','registers-source.o'),('setup','setup-source.o'),('fifo','lis-fifo-source.o')]:
  out=base/('direct-'+key);out.mkdir(exist_ok=True);shutil.copy2(runtime,out/objname);r=dict(report);r['graph_object_sha256']=report['linked_sha256'];r['parent_call_frames_report_sha256']=sha(base/'report.json')
  if key=='registers':r['roots']=['lis2dw12_'+x for x in FUNCTIONS.values()]+['lis2dw12_write_reg']
  (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');prepared[key]=dict(report_sha256=sha(out/'report.json'),object_sha256=sha(out/objname),driver_sha256=sha(ROOT/('r1/tools/verify_native_lis_call_frames_'+key+'.py')))
 receipt=dict(builder_sha256=sha(Path(__file__)),parent_report_sha256=sha(base/'report.json'),prepared=prepared);(base/'regression-preparation.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Prepared register/setup/FIFO direct regression runtime copies')
if __name__=='__main__':main()

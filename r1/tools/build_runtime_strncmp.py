#!/usr/bin/env python3
"""Compile attributable same-pin musl strncmp without changing existing runtime receipts."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vendor=ROOT/'third-party/upstream/musl-strncmp-1.2.5';pin=json.loads((vendor/'provenance.json').read_text());assert pin['commit']=='0784374d561435f7c787a555aeab8ede699ed298'
 for n,d in pin['files'].items():assert sha(vendor/n)==d,n
 out=BASE/'runtime-strncmp';out.mkdir(exist_ok=True);source=vendor/'strncmp.c';obj=out/'strncmp.o';dep=out/'strncmp.d';mr=BASE/'runtime/report.json';row=json.loads(mr.read_text())['units'][0];flags=row['command'][1:row['command'].index('-MD')];cmd=['clang',*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 inputs={str((vendor/'provenance.json').relative_to(ROOT)):sha(vendor/'provenance.json'),str((vendor/'COPYRIGHT').relative_to(ROOT)):sha(vendor/'COPYRIGHT')}
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 u,d=undefined_symbols(obj);assert not u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,upstream=pin,runtime_report_sha256=sha(mr),scope='Attributable bounded string comparison provider; original Arm runtime identity remains unproven',instruction_identity_proven=False),indent=2)+'\n');print('Pinned musl strncmp compiled')
if __name__=='__main__':main()

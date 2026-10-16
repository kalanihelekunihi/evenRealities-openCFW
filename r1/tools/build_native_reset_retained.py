#!/usr/bin/env python3
"""Compile retained getters and reuse authenticated checksum source, selecting CRC16."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-reset-retained';out.mkdir(exist_ok=True);seed=json.loads((BASE/'native-reset-decoder/report.json').read_text())['units'][0]['command'];flags=seed[1:seed.index('-MD')];flags+=['-I'+str(ROOT/'r1/source/include')];units=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};prior=BASE/'checksum-verification.json';check=json.loads(prior.read_text());inputs[str(prior.relative_to(ROOT))]=sha(prior)
 for src,name in [(ROOT/'r1/components/runtime/native_reset_retained.c','getters'),(ROOT/'r1/source/stock_checksums.c','checksums')]:
  if name=='checksums':assert sha(src)==check['source_sha256'][str(src.relative_to(ROOT))]
  obj=out/(name+'.o');dep=out/(name+'.d');cmd=['clang',*flags,'-MD','-MF',str(dep),'-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
  for item in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():p=Path(item);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
  u,d=undefined_symbols(obj);units.append(dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=u,defined=d))
 crc=out/'crc16.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_stock_crc16_modbus',str(out/'checksums.o'),'-o',str(crc)],check=True)
 linked=out/'reset-retained-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(out/'getters.o'),str(crc),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert not u
 report=dict(units=units,inputs=inputs,checksum_receipt_sha256=sha(prior),selected_crc_object_sha256=sha(crc),linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,source_context_bytes=24,retained_record_initialized_or_cleared=False,application_linked=False,instruction_identity=False,gates=['Retained RAM record at the recovered context pointer is not cold-initialized by this source.','Only getters and source checksum are selected here; writer/capture/reset retention behavior remains open.','Context cold24-byte source view, pointer/layout ownership and full raw private ABI remain separate final image gates.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Retained getters + existing source CRC16 compile/link with zero unresolved imports')
if __name__=='__main__':main()

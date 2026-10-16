#!/usr/bin/env python3
"""Link the source-owned decimal arithmetic bundle without native math imports."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'native-formatter-math';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);objects=[];providers={};inputs={str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__))}
    for directory,name in [('native-formatter-product','native_formatter_product.o'),('native-formatter-add','native_formatter_add.o'),('native-formatter-unsigned','native_formatter_unsigned.o'),('native-formatter-decimal','native_formatter_decimal.o'),('integer-runtime','integer-runtime.o')]:
        rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r['relocatable_sha256'] if directory=='integer-runtime' else r['units'][0]['object_sha256'])
        providers[str(rp.relative_to(BASE))]=sha(rp)
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path;inputs[path]=digest
        objects.append(obj)
    linked=out/'native-formatter-math.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);unresolved,defined=undefined_symbols(linked);assert not unresolved,unresolved
    report=dict(status='source-compiled-arithmetic-bundle',provider_reports=providers,objects={str(p.relative_to(BASE)):sha(p) for p in objects},inputs=inputs,linked_sha256=sha(linked),undefined_symbols=unresolved,defined_symbols=defined,original_instruction_identity=False,application_linked=False,gates=['Only the decimal arithmetic/conversion dependency bundle is linked; parser, callback framing, snprintf wrapper and full firmware remain separate requirements.','Bounded native behavior checks, complete native ABI and original instruction/whole-image identity remain distinct.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Decimal arithmetic source bundle: no unresolved symbols')
if __name__=='__main__':main()

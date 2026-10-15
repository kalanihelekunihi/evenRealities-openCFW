#!/usr/bin/env python3
"""Compile TWI callbacks directly from authenticated Nordic inline HAL."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=ROOT/'r1/research/source-build/software-twi';output.mkdir(exist_ok=True)
    receipt=output/'gpio-report.json';receipt.unlink(missing_ok=True)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    # Reuse target/SDK include setup, not the example's runtime objects.
    app=json.loads((ROOT/'r1/research/source-build/application-sdk/report.json').read_text())
    cmd=app['units'][0]['command'];flags=cmd[1:cmd.index('-c')]
    source=ROOT/'r1/components/software-twi/sdk_gpio.c';obj=output/'sdk_gpio.o';dep=output/'sdk_gpio.d'
    command=['clang',*flags,'-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)]
    subprocess.run(command,check=True)
    paths=dep.read_text().replace('\\\n',' ').split(':',1)[1].split()
    inputs={(str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p):sha(Path(p)) for p in paths}
    # Check that local vendor headers equal the authenticated archive members.
    import zipfile
    with zipfile.ZipFile(archive) as z:
        for path,digest in inputs.items():
            prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
            if path.startswith(prefix):
                member='nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):]
                assert hashlib.sha256(z.read(member)).hexdigest()==digest,path
    undefined,defined=undefined_symbols(obj);assert not undefined,undefined
    row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
    receipt.write_text(json.dumps(dict(units=[row],inputs=inputs,sdk_archive_sha256=sha(archive),application_linked=False,instruction_identity=False),indent=2)+'\n');print('Six Nordic GPIO wrappers and two recovered delay bodies compiled; no undefined symbols')
if __name__=='__main__':main()

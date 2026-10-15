#!/usr/bin/env python3
"""Compile native ADC adapters using authenticated Nordic SAADC types."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=ROOT/'r1/research/source-build/adc';output.mkdir(exist_ok=True)
    receipt=output/'report.json';receipt.unlink(missing_ok=True)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    # Reuse target/SDK include setup, not the example's runtime objects.
    app=json.loads((ROOT/'r1/research/source-build/application-sdk/report.json').read_text())
    cmd=app['units'][0]['command'];flags=cmd[1:cmd.index('-c')]+['-I'+str(ROOT/'r1/reconstructed')]
    source=ROOT/'r1/components/adc/stock_named_adc.c';obj=output/'stock_named_adc.o';dep=output/'stock_named_adc.d'
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
    undefined,defined=undefined_symbols(obj);# Provider references remain explicit until linked with the actual SDK.
    row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
    sdk_report_path=ROOT/'r1/research/source-build/application-sdk/report.json'
    sdk_report=json.loads(sdk_report_path.read_text());saadc=next(row for row in sdk_report['units'] if row['source'].endswith('/nrfx_saadc.c'))
    sdk_object=Path(saadc['command'][-1]);assert sha(sdk_object)==saadc['object_sha256'] and sha(ROOT/saadc['source'])==saadc['source_sha256']
    transport=ROOT/'r1/research/source-build/i2c5/st25-i2c5-registry.o';transport_report=transport.parent/'report.json'
    assert sha(transport)==json.loads(transport_report.read_text())['relocatable_sha256']
    linked=output/'adc-native-integration.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(obj),str(transport),str(sdk_object),'-o',str(linked)],check=True)
    remaining,_=undefined_symbols(linked)
    (output/'integration-report.json').write_text(json.dumps(dict(relocatable_sha256=sha(linked),adc_object_sha256=sha(obj),sdk_object_sha256=sha(sdk_object),sdk_report_sha256=sha(sdk_report_path),transport_report_sha256=sha(transport_report),remaining_symbols=remaining,application_linked=False),indent=2)+'\n')
    receipt.write_text(json.dumps(dict(units=[row],inputs=inputs,sdk_archive_sha256=sha(archive),application_linked=False,instruction_identity=False),indent=2)+'\n');print('Native ADC records and four adapter bodies compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()

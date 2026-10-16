#!/usr/bin/env python3
"""Link source application entry with source scatter startup; keep remaining providers unresolved."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'native-application-startup-runtime';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);objects=[];providers={};inputs={str(Path(__file__).resolve().relative_to(ROOT)):sha(Path(__file__))}
    for directory,name in [('native-application-entry','native_application_entry.o'),('native-scatter-runtime','native-scatter-runtime.o')]:
        rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r.get('relocatable_sha256') or r['units'][0]['object_sha256'])
        providers[str(rp.relative_to(BASE))]=sha(rp)
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path;inputs[path]=digest
        objects.append(obj)
    linked=out/'native-application-startup-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);unresolved,defined=undefined_symbols(linked);expected=sorted(['ble_dfu_buttonless_async_svci_init','cm_backtrace_init','nrf_drv_clock_init','nrf_log_default_backends_init','nrf_log_frontend_std_0','nrf_log_init','r1_adc_error','r1_boot_ctor_run','r1_device_module_init','r1_peripheral_module_init','r1_reset_reason_nordic_adapter','r1_structured_log_format','r1_structured_log_mode_get']);assert unresolved==expected,unresolved
    report=dict(status='candidate-native-application-providers-unresolved',provider_reports=providers,objects={str(p.relative_to(BASE)):sha(p) for p in objects},inputs=inputs,linked_sha256=sha(linked),undefined_symbols=unresolved,defined_symbols=defined,original_instruction_identity=False,application_linked=False,gates=['Application entry, scatter dispatch, runtime handoff, source handler configuration and initialization providers compile and link. Thirteen explicit imports and initialized callback source ownership remain unresolved. Typed provider fixtures are not source integration or executable fallbacks; raw ABI and whole-image integration remain unproven.','Bounded native behavior checks, complete native ABI and original instruction/whole-image identity remain distinct.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Native application startup candidate: thirteen provider imports unresolved')
if __name__=='__main__':main()

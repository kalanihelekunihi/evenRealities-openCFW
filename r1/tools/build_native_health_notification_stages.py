#!/usr/bin/env python3
"""Compile bounded native event-table configuration with explicit callback imports."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-health-notification-stages';out.mkdir(exist_ok=True);parent=BASE/'native-health-notification-throttle';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_health_notification_stages.c';obj=out/'native_health_notification_stages.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-munaligned-access','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True);inputs[str(src.relative_to(ROOT))]=sha(src);inputs[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
 po=parent/'native-health-notification-throttle-runtime.o';assert sha(po)==p['linked_sha256'];linked=out/'native-health-notification-stages-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));assert len(closed)==5
 roots=[x['symbol'] for x in json.loads((out/'contracts.json').read_text())['bodies']];graph=out/'stages-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 comparison={}
 for name in ['r1/reconstructed/qma6100/qma6100.c','r1/reconstructed/qma6100/qma6100.h','r1/docs/correlation/QMA6100-REDUCTION-CORRELATION.md']:comparison[name]=sha(ROOT/name)
 r=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,comparison_only_inputs=comparison,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=closed,newly_exposed_imports=sorted(set(u)-set(p['undefined_symbols'])),contracts_sha256=sha(out/'contracts.json'),native_body_bytes=3400,source_descriptor_bytes=12,source_pending_bytes=4,text_spans_sha256=sha(out/'text-spans.json'),full_table_extents_proven=False,complete_service_bodies_proven=False,owner_authorized_native_reconstruction=True,unlicensed_qst_source_is_build_input=False,existing_hardened_reconstruction_substituted=False,full_sensor_state_extent_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Health notification stage controllers compiled;five imports close;remaining provider frontier explicit')
if __name__=='__main__':main()

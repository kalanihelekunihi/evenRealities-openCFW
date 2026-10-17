#!/usr/bin/env python3
"""Compile native QMA transport/identity/IRQ/FIFO without vendor-source substitution."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-qma-transport';out.mkdir(exist_ok=True);parent=BASE/'native-bma-initialize';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_qma_transport.c';obj=out/'native_qma_transport.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-munaligned-access','-mfloat-abi=hard','-mfpu=fpv4-sp-d16','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True);inputs[str(src.relative_to(ROOT))]=sha(src);inputs[str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
 po=parent/'native-bma-initialize-runtime.o';assert sha(po)==p['linked_sha256'];linked=out/'native-qma-transport-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));assert closed==['r1_qma6100_bounded_fifo_read','r1_qma6100_chip_id','r1_qma6100_irq_boundary'] and not set(u)-set(p['undefined_symbols']) and len(u)==20
 roots=['r1_qma_read_retry','r1_qma_write_retry','r1_qma_delay_units','r1_qma6100_chip_id','r1_qma6100_irq_boundary','r1_qma6100_bounded_fifo_read','r1_qma6100_fifo_normalized'];graph=out/'qma-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for x in roots for v in ['-u',x]],str(linked),'-o',str(graph)],check=True)
 comparison={}
 for name in ['r1/reconstructed/qma6100/qma6100.c','r1/reconstructed/qma6100/qma6100.h','r1/docs/correlation/QMA6100-REDUCTION-CORRELATION.md']:comparison[name]=sha(ROOT/name)
 r=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,comparison_only_inputs=comparison,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=closed,newly_exposed_imports=[],fifo_text_spans_sha256=sha(out/'fifo-text-spans.json'),runtime_prefix_bytes=12,owner_authorized_native_reconstruction=True,unlicensed_qst_source_is_build_input=False,existing_hardened_reconstruction_substituted=False,full_sensor_state_extent_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native QMA transports/ID/IRQ/FIFO compiled:20 main imports;no new provider imports')
if __name__=='__main__':main()

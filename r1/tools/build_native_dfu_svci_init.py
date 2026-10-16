#!/usr/bin/env python3
"""Reuse compiled Nordic DFU entry/SVC bridge and add recovered R1 restore logging."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-dfu-svci-init';out.mkdir(exist_ok=True);rp=BASE/'application-sdk/report.json';sdk=json.loads(rp.read_text());u=next(x for x in sdk['units'] if 'ble_dfu_buttonless_async_svci_init' in x.get('defined',[]));obj=Path(u['command'][-1]);assert sha(obj)==u['object_sha256'] and sha(ROOT/u['source'])==u['source_sha256'];selected=out/'nordic-dfu-init.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=ble_dfu_buttonless_async_svci_init',str(obj),'-o',str(selected)],check=True)
 source=ROOT/'r1/components/runtime/native_dfu_vector_restore.c';port=out/'native_dfu_vector_restore.o';dep=out/'native_dfu_vector_restore.d';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(source),'-o',str(port)];subprocess.run(cmd,check=True)
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(rp.relative_to(ROOT)):sha(rp),u['source']:sha(ROOT/u['source'])}
 for p,h in sdk['configuration'].items():assert sha(ROOT/p)==h;inputs[p]=h
 h=BASE/'application-sdk/nrf_svci_clang.h';assert sha(h)==sdk['compiler_adaptations']['svci_compiled_header_sha256'];inputs[str(h.relative_to(ROOT))]=sha(h)
 for item in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():p=Path(item);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
 linked=out/'native-dfu-svci-init.o';subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(port),'-o',str(linked)],check=True);unresolved,defined=undefined_symbols(linked);assert unresolved==['nrf_dfu_svci_vector_table_set','nrf_log_frontend_std_0','nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get']
 unit=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(port),undefined=undefined_symbols(port)[0],defined=undefined_symbols(port)[1]);upstream=dict(u);upstream['admitted_scope']='Selected DFU initialization entry, SVC0/R12=3 bridge and12-byte async state only'
 report=dict(units=[unit,upstream],inputs=inputs,provider_report_sha256=sha(rp),provider_object_sha256=sha(obj),selected_object_sha256=sha(selected),linked_sha256=sha(linked),undefined_symbols=unresolved,defined_symbols=defined,sdk_archive_sha256=sdk['sdk_archive_sha256'],compiler_adaptations=sdk['compiler_adaptations'],native_scope='32-byte entry plus130-byte shared vector-restore tail;162-byte locked row',upstream_entry_source_unmodified=True,svc_bridge_instruction_bytes='4ff0030c00df7047',image_linked=False,instruction_identity=False,gates=['Vector-to-bootloader setter and physical supervisor provider remain external.','R1 restore dual logging is recovered product adaptation, not unchanged Nordic unset body.','Async state source layout, all raw ABI, final placement and byte-identical image remain gated.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Nordic DFU entry/SVC bridge source selected; R1 vector restore compiled; five source imports remain')
if __name__=='__main__':main()

from pathlib import Path
import json
N=Path('g2/analysis/bootloader-completion-2026-10-06/inventory-worker/logger-call-metadata');C=Path('g2/components/bootloader/log_call_adapters');C.mkdir(exist_ok=True);s=json.loads((N/'captured-calls.json').read_text());rows={}
for r in s['calls']:rows.setdefault((r['family'],r['line']),r)
q=lambda x:json.dumps(x,ensure_ascii=True)
out='''/* Reconstructed call-site adapters, not stock function-body replacements.
 * Only the documented fixed caller lines are supported. Stock strings are
 * readonly metadata. See logger-call-metadata/ for instruction provenance. */
#include <stdint.h>
extern void opencfw_boot_elog_output(uint32_t,const char *,const char *,const char *,long,const char *,...);
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define H(n) W(0x20026ef8u+4u*(n))
static const char path[]="/firmware.bin";
'''
# Exact path read from official data pointer supplied for %s calls.
b=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();ptr=rows[('dfu_task',526)]['argument_words'][0];offset=ptr-0x410000;path=b[offset:b.index(b'\0',offset)].decode();out=out.replace('"/firmware.bin"',q(path))
args={523:'',526:',path',532:',path,detail',538:',H(0)&0x00ffffffu,H(0)&0x00ffffffu',539:',(H(0)>>26)&1u',540:',H(1)',541:',H(4)&255u,H(4)&255u',542:',H(5)',553:',H(5),0x438000u',558:',W(H(5))',559:',H(5),W(H(5)+4u)',567:',W(H(5))',568:',H(5),W(H(5)+4u)',356:'',361:'',409:''}
# Constants shared by known callsites, dynamically recovered values retained.
out+='void opencfw_dfu_log_detail_native(uint32_t level,uint32_t line,uint32_t detail){\n switch(line){\n'
for (family,line),r in sorted(rows.items()):
 if family not in ['dfu_task','dfu_context']:continue
 out+=f' case {line}u:opencfw_boot_elog_output(level,{q(r["tag"])},{q(r["file"])},{q(r["function"])},{line},{q(r["format"])}{args[line]});return;\n'
out+=' default:return; /* No corresponding fixed source callsite. */\n }\n}\nvoid opencfw_dfu_log_native(uint32_t level,uint32_t line){opencfw_dfu_log_detail_native(level,line,0);}\n'
for family,func,params,level in [('allocator','opencfw_allocator_log_native','uint32_t line','4'),('control','opencfw_control_log_native','uint32_t level,uint32_t line','level')]:
 row=next(r for k,r in rows.items() if k[0]==family);out+=f'void {func}({params}){{if(line=={row["line"]}u)opencfw_boot_elog_output({level},{q(row["tag"])},{q(row["file"])},{q(row["function"])},{row["line"]},{q(row["format"])});}}\n'
(C/'log_adapters.c').write_text(out)
t=Path('g2/components/bootloader/dfu_task/task.c').read_text().replace('#include "task.h"','#include "../dfu_task/task.h"\nextern void opencfw_dfu_log_detail_native(uint32_t,uint32_t,uint32_t);').replace('opencfw_boot_dfu_log(1,0x214u);','opencfw_dfu_log_detail_native(1,0x214u,got);');(C/'task_with_log_detail.c').write_text(t)
(C/'log_adapters.h').write_text('#ifndef OPENCFW_LOG_CALL_ADAPTERS_H\n#define OPENCFW_LOG_CALL_ADAPTERS_H\n#include <stdint.h>\nvoid opencfw_allocator_log_native(uint32_t);\nvoid opencfw_control_log_native(uint32_t,uint32_t);\nvoid opencfw_dfu_log_native(uint32_t,uint32_t);\nvoid opencfw_dfu_log_detail_native(uint32_t,uint32_t,uint32_t);\n#endif\n')
(N/'reconstruct.py').write_bytes(Path('/tmp/opencfw-logger-source.py').read_bytes());print('created adapters',len(rows),'known lines','path',repr(path))

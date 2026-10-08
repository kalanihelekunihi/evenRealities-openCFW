"""Extract a verbatim pinned public callback and build an offline comparator."""
from pathlib import Path
import argparse,subprocess,re,hashlib,json
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--pdl-source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True)
s=a.pdl_source.read_text();m=re.search(r'cy_en_syspm_status_t Cy_SysClk_DeepSleepCallback\([^;{]*\)\s*\{',s);i=m.end();depth=1
while depth:
 if s[i]=='{':depth+=1
 if s[i]=='}':depth-=1
 i+=1
prefix="""#include <stdint.h>
#include <stdbool.h>
typedef uint32_t cy_en_syspm_status_t;
typedef uint32_t cy_en_syspm_callback_mode_t;
typedef struct {void *base;void *context;} cy_stc_syspm_callback_params_t;
#define CY_SYSPM_SUCCESS 0u
#define CY_SYSPM_FAIL 0x4200ffu
#define CY_SYSPM_CHECK_READY 1u
#define CY_SYSPM_CHECK_FAIL 2u
#define CY_SYSPM_BEFORE_TRANSITION 4u
#define CY_SYSPM_AFTER_TRANSITION 8u
#define CY_UNUSED_PARAMETER(p) ((void)(p))
extern bool iloMeasurment,preventIloMeasurment;
/* CY_IP_M0S8EXCO and CY_IP_M0S8WCO absent in selected device header. */
"""
public=a.output/'public-pm.c';public.write_text(prefix+s[m.start():i]+'\n');link=a.output/'link.ld';link.write_text('preventIloMeasurment = 0x20000f1d; iloMeasurment = 0x20000f1e; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'pm.elf';src=root/'g2/components/touch/ilo_pm_offline/pm.c';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-T',str(link),str(src),str(public),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'reproduction-receipt.json').write_text(json.dumps({'gcc':str(a.gcc),'gcc_sha256':h(a.gcc),'version':subprocess.check_output([str(a.gcc),'--version'],text=True).splitlines()[0],'pdl_pin':'35f1714623cfea682d5e285af80d50416b4c7bbc','pdl_source':str(a.pdl_source),'pdl_sha256':h(a.pdl_source),'public_environment':prefix,'public_translation_unit_sha256':h(public),'source_sha256':h(src),'elf':str(elf),'elf_sha256':h(elf),'flags':flags},indent=2)+'\n');print(elf)

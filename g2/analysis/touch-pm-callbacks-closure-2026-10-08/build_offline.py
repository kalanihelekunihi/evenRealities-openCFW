"""Pinned public registration/dispatcher plus independent reconstruction comparator."""
from pathlib import Path
import argparse,subprocess,re,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--pdl-source',type=Path,required=True);p.add_argument('--public-clock-source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True)
prefix="""#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
typedef uint32_t cy_en_syspm_status_t,cy_en_syspm_callback_mode_t;
typedef uint8_t cy_en_syspm_callback_type_t;
typedef struct {void *base,*context;} cy_stc_syspm_callback_params_t;
typedef struct cy_stc_syspm_callback cy_stc_syspm_callback_t;
struct cy_stc_syspm_callback {uint32_t (*callback)(cy_stc_syspm_callback_params_t *,uint32_t);uint8_t type;uint32_t skipMode;cy_stc_syspm_callback_params_t *callbackParams;cy_stc_syspm_callback_t *prevItm,*nextItm;uint8_t order;};
_Static_assert(offsetof(cy_stc_syspm_callback_t,order)==24,"order");
_Static_assert(offsetof(cy_stc_syspm_callback_t,callbackParams)==12,"params");
#define CY_SYSPM_DEEPSLEEP 1u
#define SRSS_PWR_KEY_DELAY (*(volatile uint32_t *)0x40030004u)
#define SFLASH_DPSLP_KEY_DELAY (*(volatile const uint16_t *)0x0ffff152u)
#define SCB_SCR (*(volatile uint32_t *)0xe000ed10u)
#define SCB_SCR_SLEEPDEEP_Msk 4u
#define __WFI() __asm volatile("wfi")
uint32_t Cy_SysLib_EnterCriticalSection(void);
void Cy_SysLib_ExitCriticalSection(uint32_t);
void Cy_SysPm_CpuEnterDeepSleepNoCallbacks(void);
uint32_t Cy_SysPm_ExecuteCallback(uint8_t,uint32_t);
#define CY_SYSPM_SUCCESS 0u
#define CY_SYSPM_FAIL 0x4200ffu
#define CY_SYSPM_CHECK_READY 1u
#define CY_SYSPM_CHECK_FAIL 2u
#define CY_SYSPM_BEFORE_TRANSITION 4u
#define CY_SYSPM_AFTER_TRANSITION 8u
/* Valid supported input contract; target BKPT assertion paths are excluded. */
#define CY_ASSERT_L3(c) ((void)0)
extern cy_stc_syspm_callback_t *pmCallbackRoot[],*failedCallback[];
"""
s=a.pdl_source.read_text();bodies=[]
for name in ['Cy_SysPm_RegisterCallback','Cy_SysPm_ExecuteCallback','Cy_SysPm_CpuEnterDeepSleep','Cy_SysPm_CpuEnterDeepSleepNoCallbacks']:
 m=re.search(r'(?:bool|void|cy_en_syspm_status_t)\s+'+name+r'\([^;{]*\)\s*\{',s);i=m.end();depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 bodies.append(s[m.start():i])
public=a.output/'public-callbacks.c';public.write_text(prefix+'\n'.join(bodies)+'\n');link=a.output/'link.ld';link.write_text('preventIloMeasurment = 0x20000f1d; iloMeasurment = 0x20000f1e; Cy_SysLib_EnterCriticalSection = 0x4493; Cy_SysLib_ExitCriticalSection = 0x449b; pmCallbackRoot = 0x20000f34; failedCallback = 0x20000f28; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } .bss 0x20000f24 : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'callbacks.elf';src=root/'g2/components/touch/pm_callbacks_offline/callbacks.c';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-T',str(link),str(src),str(public),str(a.public_clock_source),str(root/'g2/components/touch/ilo_pm_offline/pm.c'),str(D/'probe.c'),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'reproduction-receipt.json').write_text(json.dumps({'gcc':str(a.gcc),'gcc_sha256':h(a.gcc),'version':subprocess.check_output([str(a.gcc),'--version'],text=True).splitlines()[0],'pdl_pin':'35f1714623cfea682d5e285af80d50416b4c7bbc','pdl_source':str(a.pdl_source),'pdl_sha256':h(a.pdl_source),'public_environment':prefix,'public_translation_unit_sha256':h(public),'source_sha256':h(src),'probe_sha256':h(D/'probe.c'),'public_clock_source_sha256':h(a.public_clock_source),'independent_clock_source_sha256':h(root/'g2/components/touch/ilo_pm_offline/pm.c'),'elf':str(elf),'elf_sha256':h(elf),'flags':flags},indent=2)+'\n');print(elf)

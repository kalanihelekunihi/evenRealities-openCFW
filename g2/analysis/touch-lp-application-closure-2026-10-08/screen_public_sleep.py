"""Selected pinned PM bodies; resolve peers/globals to observed firmware addresses."""
from pathlib import Path
import argparse,re,subprocess,json,hashlib
from elftools.elf.elffile import ELFFile
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;a.output.mkdir(parents=True,exist_ok=True);s=a.source.read_text();raw=(D.parents[2]/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()[32:];rows=[];bodies=[]
prefix='''#include <stdint.h>
#include <stddef.h>
typedef uint32_t cy_en_syspm_status_t;
#define CY_SYSPM_DEEPSLEEP 1u
#define CY_SYSPM_SUCCESS 0u
#define CY_SYSPM_CHECK_READY 1u
#define CY_SYSPM_CHECK_FAIL 2u
#define CY_SYSPM_BEFORE_TRANSITION 4u
#define CY_SYSPM_AFTER_TRANSITION 8u
extern void *pmCallbackRoot[];
uint32_t Cy_SysPm_ExecuteCallback(uint32_t,uint32_t);
uint32_t Cy_SysLib_EnterCriticalSection(void);
void Cy_SysLib_ExitCriticalSection(uint32_t);
void Cy_SysPm_CpuEnterDeepSleepNoCallbacks(void);
#define SRSS_PWR_KEY_DELAY (*(volatile uint32_t *)0x40030004u)
#define SFLASH_DPSLP_KEY_DELAY (*(volatile const uint16_t *)0x0ffff152u)
#define SCB_SCR (*(volatile uint32_t *)0xe000ed10u)
#define SCB_SCR_SLEEPDEEP_Msk 4u
#define __WFI() __asm volatile("wfi")
'''
for name,start,end in [('Cy_SysPm_CpuEnterDeepSleep',0xa58c,0xa5f4),('Cy_SysPm_CpuEnterDeepSleepNoCallbacks',0xa388,0xa3b0)]:
 m=re.search(r'(?:cy_en_syspm_status_t|void)\s+'+name+r'\s*\([^;{]*\)\s*\{',s);i=m.end();depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 bodies.append(s[m.start():i]);c=a.output/(name+'.c');c.write_text(prefix+s[m.start():i]+'\n');link=a.output/(name+'.ld');link.write_text('pmCallbackRoot = 0x20000f34; Cy_SysPm_ExecuteCallback = 0xa445; Cy_SysLib_EnterCriticalSection = 0x4493; Cy_SysLib_ExitCriticalSection = 0x449b; '+('Cy_SysPm_CpuEnterDeepSleepNoCallbacks = 0xa389; ' if name.endswith('DeepSleep') else '')+'SECTIONS { .text '+hex(start)+' : { *(.text*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');stock=raw[start-0x3300:end-0x3300]
 for opt in ['Og','O1','O2','Os']:
  elf=a.output/(name+'-'+opt+'.elf');subprocess.run([str(a.gcc),'-mcpu=cortex-m0plus','-mthumb','-'+opt,'-ffreestanding','-fno-builtin','-nostdlib','-T',str(link),str(c),'-o',str(elf)],check=True)
  with elf.open('rb') as f:data=ELFFile(f).get_section_by_name('.text').data()
  rows.append({'function':name,'stock_start':hex(start),'optimization':opt,'stock_extent':len(stock),'public_extent':len(data),'exact':stock==data,'stock_sha256':hashlib.sha256(stock).hexdigest(),'public_sha256':hashlib.sha256(data).hexdigest(),'matching_addresses':[hex(0x3300+k) for k in range(len(raw)-len(data)+1) if raw[k:k+len(data)]==data]})
(D/'public-sleep-screen.json').write_text(json.dumps({'pdl_pin':'35f1714623cfea682d5e285af80d50416b4c7bbc','source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'environment':prefix,'comparisons':rows,'limits':['Verbatim selected public bodies with explicit macros and fixed resolved firmware peers/global addresses; not complete SDK rebuild.','No callback-body, physical sleep/wakeup/IRQ or uniquely identified compiler/release claim.']},indent=2)+'\n');print([(r['function'],r['optimization'],r['exact'],r['public_extent']) for r in rows])

(a.output/'public-sleep.c').write_text(prefix+'\n'.join(bodies)+'\n')

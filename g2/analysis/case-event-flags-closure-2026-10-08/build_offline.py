from pathlib import Path
import argparse,re,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);c=root/'g2/components/case/event_flags_offline'
prefix='''#include <stdint.h>
#include <stddef.h>
typedef void *osEventFlagsId_t,*EventGroupHandle_t;
typedef int32_t BaseType_t;
typedef uint32_t EventBits_t;
#define EVENT_FLAGS_INVALID_BITS 0xff000000u
#define configUSE_OS2_EVENTFLAGS_FROM_ISR 1
#define osErrorParameter (-4)
#define osErrorResource (-3)
#define pdFALSE 0
#define pdFAIL 0
static uint32_t irq(void){uint32_t x;__asm volatile("mrs %0, ipsr":"=r"(x));return x;}
#define IS_IRQ() irq()
/* Explicit stock-matching callback-context environment, not full IRQ_Context implementation. */
#define IRQ_Context() irq()
#define portYIELD_FROM_ISR(y) do{if(y)*(volatile uint32_t *)0xe000ed04u=0x10000000u;}while(0)
int32_t xEventGroupSetBitsFromISR(void *,uint32_t,int32_t *);
uint32_t xEventGroupSetBits(void *,uint32_t);
uint32_t xEventGroupGetBitsFromISR(void *);
''';versions={'v1031':'677bb7fcbf38f07e106735c7c947f4efb2714b0f','v1046':'943dc0607e28d786f9b363e5da60047c1ea755d8','v1051':'d213f261b5be6bb29a7cce8b84071706b72f4d53'};paths=[];receipts=[];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for version,pin in versions.items():
 source=D/('cmsis-os2-'+pin+'.c');s=source.read_text();m=re.search(r'uint32_t osEventFlagsSet\s*\([^;{]*\)\s*\{',s);i=m.end();depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 body=s[m.start():i];out=a.output/(version+'.c');out.write_text(prefix+body.replace('osEventFlagsSet','case_public_event_set_'+version,1)+'\n');paths.append(out);receipts.append({'version':version,'pin':pin,'url':'https://raw.githubusercontent.com/ARM-software/CMSIS-FreeRTOS/'+pin+'/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c','source_sha256':h(source),'selected_body_sha256':hashlib.sha256(body.encode()).hexdigest(),'translation_unit_sha256':h(out)})
link=a.output/'link.ld';link.write_text('xEventGroupSetBitsFromISR = 0x0800c569; xEventGroupSetBits = 0x0800c4df; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'events.elf';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-T',str(link),str(c/'events.c'),str(D/'kernel_models.c'),*[str(p) for p in paths],'-o',str(elf)],check=True);(D/'reproduction-receipt.json').write_text(json.dumps({'sources':receipts,'public_environment':prefix,'gcc':str(a.gcc),'gcc_sha256':h(a.gcc),'flags':flags,'source_sha256':h(c/'events.c'),'kernel_models_sha256':h(D/'kernel_models.c'),'elf':str(elf),'elf_sha256':h(elf),'limits':['Actual kernel child entries are replaced by compiled result models in verification; explicitly not full wrapper/kernel integration proof.','Public function bodies retained except export name; IRQ_Context scaffold is IPSR-only, not uniquely attributed source configuration.']},indent=2)+'\n');print(elf)

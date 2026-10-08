from pathlib import Path
import argparse,subprocess,json,hashlib,re
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);src=root/'g2/components/audio/thread_flags_offline/flags.c';up=root/'g2/analysis/case-event-flags-closure-2026-10-08/cmsis-os2-d213f261b5be6bb29a7cce8b84071706b72f4d53.c';s=up.read_text();m=re.search(r'uint32_t osThreadFlagsSet\s*\([^;{]*\)\s*\{',s);i=m.end();depth=1
while depth:
 if s[i]=='{':depth+=1
 if s[i]=='}':depth-=1
 i+=1
body=s[m.start():i];prefix='''#include <stdint.h>
#include <stddef.h>
typedef void *osThreadId_t,*TaskHandle_t;
typedef int32_t BaseType_t;
#define THREAD_FLAGS_INVALID_BITS 0x80000000u
#define osErrorParameter (-4)
#define osError (-1)
#define pdFALSE 0
#define eSetBits 1
#define eNoAction 0
int32_t audio_irq_context(void);
int32_t audio_notify_task(void *,uint32_t,uint32_t,uint32_t,uint32_t *);
int32_t audio_notify_isr(void *,uint32_t,uint32_t,uint32_t,uint32_t *,int32_t *);
#define IRQ_Context() audio_irq_context()
#define xTaskNotifyFromISR(t,v,a,y) audio_notify_isr(t,0,v,a,0,y)
#define xTaskNotifyAndQueryFromISR(t,v,a,p,y) audio_notify_isr(t,0,v,a,p,y)
#define xTaskNotify(t,v,a) audio_notify_task(t,0,v,a,0)
#define xTaskNotifyAndQuery(t,v,a,p) audio_notify_task(t,0,v,a,p)
#define portYIELD_FROM_ISR(y) do{if(y)*(volatile uint32_t *)0xe000ed04u=0x10000000u;}while(0)
''';public=a.output/'public.c';public.write_text(prefix+body.replace('osThreadFlagsSet','audio_public_flags_set',1));link=a.output/'link.ld';link.write_text('audio_irq_context = 0x0044900f; audio_notify_task = 0x00455c49; audio_notify_isr = 0x00455dc1; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'flags.elf';flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-T',str(link),str(src),str(public),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(gcc=str(a.gcc),gcc_sha256=h(a.gcc),flags=flags,source_sha256=h(src),elf=str(elf),elf_sha256=h(elf),public_pin='d213f261b5be6bb29a7cce8b84071706b72f4d53',public_source=str(up.relative_to(root)),public_sha256=h(up),selected_body_sha256=hashlib.sha256(body.encode()).hexdigest(),scaffold=prefix,limits=['Cortex-M4 compatible instruction profile; target Apollo510 Cortex-M55.','Real original context and notify providers on all sides; public body macro maps disclosed. No full kernel configuration/version attribution.']),indent=2)+'\n');print(elf)

from pathlib import Path
import argparse,subprocess,re,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);src=root/'g2/components/audio/notification_wait_offline/wait.c';old=root/'g2/analysis/audio-thread-flags-closure-2026-10-08';receipt=json.loads((old/'reproduction-receipt.json').read_text());up=(root/receipt['public_source']).read_text();m=re.search(r'uint32_t osThreadFlagsWait\s*\([^;{]*\)\s*\{',up);i=m.end();depth=1
while depth:
 if up[i]=='{':depth+=1
 if up[i]=='}':depth-=1
 i+=1
prefix='''#include <stdint.h>
typedef int32_t BaseType_t;
typedef uint32_t TickType_t;
#define pdPASS 1
#define pdFAIL 0
#define THREAD_FLAGS_INVALID_BITS 0x80000000u
#define osErrorISR (-6)
#define osErrorParameter (-4)
#define osErrorResource (-3)
#define osErrorTimeout (-2)
#define osFlagsNoClear 2
#define osFlagsWaitAll 1
#define pdTRUE 1
#define pdFALSE 0
int32_t audio_irq_context(void);
uint32_t audio_tick(void);
int32_t audio_original_notify_wait(uint32_t,uint32_t,uint32_t,uint32_t *,uint32_t);
#define IRQ_Context() audio_irq_context()
#define xTaskGetTickCount() audio_tick()
#define xTaskNotifyWait(a,b,c,d) audio_original_notify_wait(0,a,b,c,d)
''';public=a.output/'public.c';public.write_text(prefix+up[m.start():i].replace('osThreadFlagsWait','audio_public_flags_wait',1));link=a.output/'link.ld';link.write_text('audio_irq_context = 0x0044900f; audio_tick = 0x00454eff; audio_original_notify_wait = 0x00455b85; audio_enter_critical = 0x004420d1; audio_exit_critical = 0x004420e9; audio_block_ticks = 0x00455fa9; audio_yield = 0x004420bd; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'wait.elf';flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-T',str(link),str(src),str(public),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps(dict(gcc=str(a.gcc),gcc_sha256=h(a.gcc),source_sha256=h(src),flags=flags,elf=str(elf),elf_sha256=h(elf),public_source=receipt['public_source'],public_source_sha256=receipt['public_sha256'],public_body_sha256=hashlib.sha256(up[m.start():i].encode()).hexdigest(),scaffold=prefix,limits=['Independent index0 notify-wait subset and wrapper; original/public uses actual original kernel.','Blocking stops before actual455fa8; no yield/delay/task-return model.']),indent=2)+'\n');print(elf)

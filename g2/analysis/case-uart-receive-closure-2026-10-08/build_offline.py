"""Pinned official receive bodies with explicit ABI/constants and callback boundaries."""
from pathlib import Path
import argparse,re,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);c=root/'g2/components/case/uart_receive_offline'
prefix='''#include "receive.h"
#include <stddef.h>
typedef case_uart_rx UART_HandleTypeDef;
#define READ_REG(r) (r)
#define READ_BIT(r,b) ((r)&(b))
#define CLEAR_BIT(r,b) ((r)&=~(b))
#define HAL_UART_STATE_BUSY_RX 0x22u
#define HAL_UART_STATE_READY 0x20u
#define HAL_UART_RECEPTION_TOIDLE 1u
#define HAL_UART_RECEPTION_STANDARD 0u
#define HAL_UART_RXEVENT_TC 0u
#define USART_CR1_RXNEIE_RXFNEIE 0x20u
#define USART_CR1_PEIE 0x100u
#define USART_CR1_IDLEIE 0x10u
#define USART_CR1_RTOIE (1u<<26)
#define USART_CR2_RTOEN (1u<<23)
#define USART_CR3_EIE 1u
#define UART_FLAG_IDLE 0x10u
#define UART_CLEAR_IDLEF 0x10u
#define UART_RXDATA_FLUSH_REQUEST 8u
#define SET 1u
#define USE_HAL_UART_REGISTER_CALLBACKS 0
#define IS_LPUART_INSTANCE(p) ((uint32_t)(p)==0x40008000u)
#define __HAL_UART_GET_FLAG(h,f) ((((h)->Instance->ISR&(f))==(f))?SET:0u)
#define __HAL_UART_CLEAR_FLAG(h,f) ((h)->Instance->ICR=(f))
#define __HAL_UART_SEND_REQ(h,f) ((h)->Instance->RQR|=(f))
static void clear(volatile uint32_t *p,uint32_t bits) {
 uint32_t saved,one=1;__asm volatile("mrs %0, primask\\nmsr primask, %1":"=&r"(saved):"r"(one):"memory");*p&=~bits;__asm volatile("msr primask, %0"::"r"(saved):"memory");
}
#define ATOMIC_CLEAR_BIT(r,b) clear(&(r),(b))
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *);
void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *,uint16_t);
'''
versions={'v145':'ba4210f57d3c863d31ace271219a12f43ab59847','v140':'e84a576c18bf5806d43bf45fe0f8d7007ff8e6c2','v143':'38df07685b03ab758d2374ff56edbbf20ba829c8','v144':'3e7e57636112b59a7c88babb18de3070262a51ae','v146':'e194e5abc3a125ef08434f1ee122a2bc7b3d9af4','v147':'a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9'};sources=[];receipts=[];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for version,pin in versions.items():
 source=D/('public-uart-'+pin+'.c');s=source.read_text();bodies=[];bodyhash={}
 for bits in [8,16]:
  name=f'UART_RxISR_{bits}BIT';m=re.search(r'static void '+name+r'\([^;{]*\)\s*\{',s);i=m.end();depth=1
  while depth:
   if s[i]=='{':depth+=1
   if s[i]=='}':depth-=1
   i+=1
  body=s[m.start():i];bodyhash[name]=hashlib.sha256(body.encode()).hexdigest();bodies.append(body.replace('static void '+name,'void case_public_rx'+str(bits)+'_'+version,1))
 out=a.output/(version+'.c');out.write_text(prefix+'\n'.join(bodies)+'\n');sources.append(out);receipts.append({'version':version,'pin':pin,'official_source_url':'https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/'+pin+'/Src/stm32g0xx_hal_uart.c','source_sha256':h(source),'body_sha256':bodyhash,'translation_unit_sha256':h(out)})
link=a.output/'link.ld';link.write_text('SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'receive.elf';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-I'+str(c),'-T',str(link),str(c/'receive.c'),str(D/'callback_boundary.c'),*[str(p) for p in sources],'-o',str(elf)],check=True)
(D/'reproduction-receipt.json').write_text(json.dumps({'sources':receipts,'gcc':str(a.gcc),'gcc_sha256':h(a.gcc),'version':subprocess.check_output([str(a.gcc),'--version'],text=True).splitlines()[0],'public_environment':prefix,'device_header_sha256':h(D/'stm32g0b1xx.h'),'device_header_pin':'f576c24e123edf3332988ecd49512c0f35f85186','independent_source_sha256':h(c/'receive.c'),'elf':str(elf),'elf_sha256':h(elf),'flags':flags,'limits':['Bodies retained verbatim except static declaration exported/renamed; minimal ABI/macros explicitly supplied.','Callbacks are compiled boundary markers; actual application completion bodies are not exercised.','Candidate release commits were resolved by peeling official annotated tags; initial tag-object raw URLs returned404 and were not accepted as source.']},indent=2)+'\n');print(elf)

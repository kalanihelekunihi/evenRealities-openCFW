from pathlib import Path
import argparse,re,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);c=root/'g2/components/case/uart_start_offline';s=(D/'stm32g0xx_hal_uart.c').read_text();header=(D/'stm32g0xx_hal_uart_ex.h').read_text();start=header.index('#define UART_MASK_COMPUTATION(');stop=header.index('  } while(0U)',start)+len('  } while(0U)');mask=header[start:stop]
prefix='''#include "start.h"
#include <stddef.h>
typedef case_start_handle UART_HandleTypeDef;
typedef uint32_t HAL_StatusTypeDef;
#define HAL_OK 0u
#define HAL_ERROR 1u
#define HAL_BUSY 2u
#define HAL_UART_STATE_READY 0x20u
#define HAL_UART_STATE_BUSY_RX 0x22u
#define HAL_UART_ERROR_NONE 0u
#define HAL_UART_RECEPTION_STANDARD 0u
#define UART_WORDLENGTH_9B 0x1000u
#define UART_WORDLENGTH_8B 0u
#define UART_WORDLENGTH_7B 0x10000000u
#define UART_PARITY_NONE 0u
#define UART_FIFOMODE_ENABLE 0x20000000u
#define USART_CR1_PEIE 0x100u
#define USART_CR1_RXNEIE_RXFNEIE 0x20u
#define USART_CR1_RTOIE 0x4000000u
#define USART_CR2_RTOEN 0x800000u
#define USART_CR3_RXFTIE 0x10000000u
#define USART_CR3_EIE 1u
#define READ_BIT(r,b) ((r)&(b))
#define IS_LPUART_INSTANCE(p) ((uint32_t)(p)==0x40008000u)
static void set(volatile uint32_t *r,uint32_t bits){uint32_t old,one=1;__asm volatile("mrs %0, primask\\nmsr primask, %1":"=&r"(old):"r"(one):"memory");*r|=bits;__asm volatile("msr primask, %0"::"r"(old):"memory");}
#define ATOMIC_SET_BIT(r,b) set(&(r),(b))
uint32_t UART_Start_Receive_IT(UART_HandleTypeDef *,uint8_t *,uint16_t);
void UART_RxISR_8BIT(UART_HandleTypeDef *);
void UART_RxISR_16BIT(UART_HandleTypeDef *);
void UART_RxISR_8BIT_FIFOEN(UART_HandleTypeDef *);
void UART_RxISR_16BIT_FIFOEN(UART_HandleTypeDef *);
''';bodies=[]
for name in ['HAL_UART_Receive_IT','UART_Start_Receive_IT']:
 m=re.search(r'HAL_StatusTypeDef '+name+r'\([^;{]*\)\s*\{',s);i=m.end();depth=1
 while depth:
  if s[i]=='{':depth+=1
  if s[i]=='}':depth-=1
  i+=1
 bodies.append(s[m.start():i])
public=a.output/'public-start.c';public.write_text(prefix+mask+'\n'+'\n'.join(bodies)+'\n');link=a.output/'link.ld';link.write_text('UART_RxISR_8BIT = 0x08008999; UART_RxISR_16BIT = 0x08008759; UART_RxISR_8BIT_FIFOEN = 0x08008a49; UART_RxISR_16BIT_FIFOEN = 0x08008809; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'start.elf';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-I'+str(c),'-T',str(link),str(c/'start.c'),str(public),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(D/'reproduction-receipt.json').write_text(json.dumps({'source_commit':'ba4210f57d3c863d31ace271219a12f43ab59847','source_sha256':h(D/'stm32g0xx_hal_uart.c'),'uart_header_sha256':h(D/'stm32g0xx_hal_uart.h'),'uart_ex_header_sha256':h(D/'stm32g0xx_hal_uart_ex.h'),'public_environment':prefix,'verbatim_mask_macro':mask,'translation_unit_sha256':h(public),'native_source_sha256':h(c/'start.c'),'gcc':str(a.gcc),'gcc_sha256':h(a.gcc),'elf':str(elf),'elf_sha256':h(elf),'flags':flags,'limits':['Selected full bodies and verbatim public mask macro; explicit ARM32 ABI/macros, not full SDK.','Original callback pointers are stored as ABI metadata; pointed ISR bodies are not executed by these start calls.','USART1 only in fixture; no LPUART compatibility inference.']},indent=2)+'\n');print(elf)

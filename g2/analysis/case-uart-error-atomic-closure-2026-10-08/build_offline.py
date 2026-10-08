"""Build independent UART prefix plus pinned public selected-prefix comparator."""
from pathlib import Path
import argparse,re,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--gcc',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();D=Path(__file__).resolve().parent;root=D.parents[2];a.output.mkdir(parents=True,exist_ok=True);source=D/'stm32g0xx_hal_uart.c';s=source.read_text()
m=re.search(r'void HAL_UART_IRQHandler\([^;{]*\)\s*\{',s);cut=s.index('  /* Check current reception Mode :',m.end());irq=s[m.start():cut]+'  case_uart_other_irq(huart);\n}\n'
m=re.search(r'static void UART_EndRxTransfer\([^;{]*\)\s*\{',s);i=m.end();depth=1
while depth:
 if s[i]=='{':depth+=1
 if s[i]=='}':depth-=1
 i+=1
end=s[m.start():i]
prefix='''#include <stdint.h>
#include <stddef.h>
typedef struct {volatile uint32_t CR1,CR2,CR3,BRR,GTPR,RTOR,RQR,ISR,ICR;} USART_TypeDef;
typedef struct DMA_HandleTypeDef DMA_HandleTypeDef;
struct DMA_HandleTypeDef {uint8_t pad[56];void (*XferAbortCallback)(DMA_HandleTypeDef *);};
typedef struct UART_HandleTypeDef UART_HandleTypeDef;
struct UART_HandleTypeDef {USART_TypeDef *Instance;uint8_t pad[104];uint32_t ReceptionType,RxEventType;void (*RxISR)(UART_HandleTypeDef *);uint32_t TxISR;void *hdmatx;DMA_HandleTypeDef *hdmarx;uint32_t Lock,gState,RxState,ErrorCode;};
_Static_assert(offsetof(UART_HandleTypeDef,RxISR)==0x74,"RxISR");
_Static_assert(offsetof(UART_HandleTypeDef,ErrorCode)==0x90,"ErrorCode");
#define READ_REG(x) (x)
#define HAL_IS_BIT_SET(r,b) (((r)&(b))==(b))
#define USART_ISR_PE 1u
#define USART_ISR_FE 2u
#define USART_ISR_NE 4u
#define USART_ISR_ORE 8u
#define USART_ISR_RTOF 0x800u
#define USART_ISR_RXNE_RXFNE 0x20u
#define USART_CR1_RXNEIE_RXFNEIE 0x20u
#define USART_CR1_PEIE 0x100u
#define USART_CR1_RTOIE 0x4000000u
#define USART_CR1_IDLEIE 0x10u
#define USART_CR3_RXFTIE 0x10000000u
#define USART_CR3_EIE 1u
#define USART_CR3_DMAR 0x40u
#define UART_CLEAR_PEF 1u
#define UART_CLEAR_FEF 2u
#define UART_CLEAR_NEF 4u
#define UART_CLEAR_OREF 8u
#define UART_CLEAR_RTOF 0x800u
#define HAL_UART_ERROR_PE 1u
#define HAL_UART_ERROR_FE 4u
#define HAL_UART_ERROR_NE 2u
#define HAL_UART_ERROR_ORE 8u
#define HAL_UART_ERROR_RTO 0x20u
#define HAL_UART_ERROR_NONE 0u
#define HAL_UART_RECEPTION_TOIDLE 1u
#define HAL_UART_RECEPTION_STANDARD 0u
#define HAL_UART_STATE_READY 0x20u
#define HAL_OK 0u
#define USE_HAL_UART_REGISTER_CALLBACKS 0
#define __HAL_UART_CLEAR_FLAG(h,f) ((h)->Instance->ICR=(f))
static void public_atomic_clear(volatile uint32_t *r,uint32_t mask) {
 uint32_t saved,one=1;__asm volatile("mrs %0, primask\\nmsr primask, %1":"=&r"(saved):"r"(one):"memory");*r&=~mask;__asm volatile("msr primask, %0"::"r"(saved):"memory");
}
#define ATOMIC_CLEAR_BIT(r,b) public_atomic_clear(&(r),(b))
static void UART_EndRxTransfer(UART_HandleTypeDef *);
void HAL_UART_ErrorCallback(UART_HandleTypeDef *);
void case_uart_other_irq(UART_HandleTypeDef *);
void UART_DMAAbortOnError(DMA_HandleTypeDef *);
uint32_t HAL_DMA_Abort_IT(DMA_HandleTypeDef *);
'''
public=a.output/'public-uart.c';public.write_text(prefix+irq+'\n'+end+'\n');link=a.output/'link.ld';link.write_text('HAL_UART_ErrorCallback = 0x08005f43; HAL_DMA_Abort_IT = 0x080048e7; UART_DMAAbortOnError = 0x080086e1; SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n');elf=a.output/'uart.elf';c=root/'g2/components/case/uart_error_atomic_offline';flags=['-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib'];subprocess.run([str(a.gcc),*flags,'-I'+str(c),'-T',str(link),str(c/'uart.c'),str(public),str(D/'probe.c'),'-o',str(elf)],check=True);h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(D/'reproduction-receipt.json').write_text(json.dumps({'gcc':str(a.gcc),'gcc_sha256':h(a.gcc),'version':subprocess.check_output([str(a.gcc),'--version'],text=True).splitlines()[0],'official_source_url':'https://raw.githubusercontent.com/STMicroelectronics/stm32g0xx-hal-driver/a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9/Src/stm32g0xx_hal_uart.c','pin':'a0cf8a8b96183fdcc2e3b1cf0bcf0825f27bd0c9','source_sha256':h(source),'public_environment':prefix,'public_translation_unit_sha256':h(public),'independent_source_sha256':h(c/'uart.c'),'elf':str(elf),'elf_sha256':h(elf),'flags':flags,'limits':['Selected verbatim IRQ prefix ends before IDLE handling; explicit boundary marker appended. Selected EndRxTransfer is full body.','DMA request must remain disabled in prefix comparison; linked actual DMA peers are not exercised.','Explicit ARM32 target ABI/macros, not full STM32 SDK or producing-version identification.']},indent=2)+'\n');print(elf)

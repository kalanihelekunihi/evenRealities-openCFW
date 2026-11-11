/* Out-of-line CMSIS NVIC_ClearPendingIRQ / NVIC_EnableIRQ / NVIC_SetPriority
 * as the locked f89a4c46 IAR build emits them. The UART HAL that lived here
 * is upstream AmbiqSuite 5.0.0 am_hal_uart.c. */
#include <stdint.h>
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
/* Names retained for existing row-loop ABI. Exact addresses determine action. */
NI uint32_t opencfw_bl_post_enable(uint32_t irq) {
    int32_t n=(int16_t)irq;if(n<0)return irq;
    uint32_t index=(uint32_t)n>>5;R(0xe000e280u+4*index)=1u<<(irq&31);return index;
}
NI uint32_t opencfw_bl_post_precommit(uint32_t irq) {
    int32_t n=(int16_t)irq;if(n<0)return irq;
    uint32_t index=(uint32_t)n>>5;R(0xe000e100u+4*index)=1u<<(irq&31);return index;
}
NI uint32_t opencfw_bl_register_mode(uint32_t irq,uint32_t priority) {
    int32_t n=(int16_t)irq;
    if(n>=0){B(0xe000e400u+(uint32_t)n)=(uint8_t)(priority<<4);return (uint32_t)n;}
    uint32_t address=0xe000ed18u+(irq&15);B(address-4)=(uint8_t)(priority<<4);return address;
}

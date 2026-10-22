/* SPDX-License-Identifier: MIT
 * Stock 0x0800bad8/0x0800baa4/0x0800bafc pin toggles and
 * 0x0800a7a2 busy delay. Pin writer has sourced MMIO semantics.
 */
#include <stdint.h>
extern void case_control_write(uint32_t base,uint32_t mask,uint32_t enable);
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *state); /* 0x08004d30 */
/* Stock 0x0800BAD8 (case_write_mask8_set) */
void case_bus_drive_a(void){case_control_write(0x50000000u,8u,1u);}
/* Stock 0x0800BAA4 (case_transition_word4_alt) */
void case_bus_drive_b(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x200000a0u;
    if(state[1]!=1u){state[1]=1u;case_bus_gpio_config(0x50000000u,state);}
}
/* Stock 0x0800BAFC (case_write_mask8_clear) */
void case_bus_drive_c(void){case_control_write(0x50000000u,8u,0u);}
void case_bus_delay(uint32_t cycles)
{
    for(volatile int32_t i=0;i<(int32_t)cycles;++i){}
}

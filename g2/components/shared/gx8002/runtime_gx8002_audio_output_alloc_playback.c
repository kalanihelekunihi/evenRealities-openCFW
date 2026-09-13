/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
extern void *memset(void *, int, size_t);
extern void *open_cfw_gx8002_aout_select_hw_config(unsigned int);
extern int open_cfw_gx8002_aout_handle_isr(int, void *);
extern void open_cfw_gx8002_request_irq(int, int (*)(int,void *), void *);
/* Successful stock e7e0 path. Repair the stock failure path, which otherwise
 * continues with handle zero and stores to low memory before enabling IRQ13. */
void *open_cfw_gx8002_aout_alloc_playback(unsigned int route)
{
    volatile uint8_t *state=(volatile uint8_t *)0x20026b94u;
    __asm__ volatile ("" : "+r" (state));
    if (((const uint8_t *)state)[4] || *(volatile uint32_t *)(state+8) || ((const uint8_t *)state)[12]!=route)
        return NULL;
    memset((void *)(state+16),0,36);
    state[4]=1;
    *(volatile uint32_t *)(state+20)=0;
    state[24]=(uint8_t)route;
    volatile uint32_t *settings=open_cfw_gx8002_aout_select_hw_config(0);
    *(volatile uint32_t *)(state+48)=(uintptr_t)settings;
    volatile uint32_t *hw=(volatile uint32_t *)0xa0b00000u;
    hw[3]=hw[3]|(1u<<21);
    hw[0]=hw[0]&0x7fffffffu;
    uint32_t word=hw[0];hw[0]=(word&~2u)|((settings[0]&1u)<<1);
    word=hw[0];hw[0]=(word&~1u)|(settings[1]&1u);
    hw[1]=hw[1]&~256u;
    open_cfw_gx8002_request_irq(13,open_cfw_gx8002_aout_handle_isr,(void *)state);
    return (void *)state;
}

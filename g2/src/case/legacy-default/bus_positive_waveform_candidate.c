/* SPDX-License-Identifier: MIT
 * Stock 0x0800a188/0x0800a224/0x0800a2a2 output-channel (PB2, "4005") bit
 * waveforms and response wrapper 0x0800c42c.
 * Bit timing follows stock call-for-call: the pulse leaves 0x0800a1ac/
 * 0x0800a1e8 (bus-pulse/pulse_leaves.c), the GPIO leaves 0x0800ba84/bac4/
 * bae8 and the 5-cycle-per-count delay 0x0800a794. The earlier reduction
 * inlined pins and used a volatile stack counter (about 11 cycles per count,
 * 2.2x stock); see build/case-link/timing.py.
 */
#include <stdint.h>
extern uint32_t case_bus_positive_sample(uint32_t *bit); /* 0x0800b4e0 */
extern void case_pulse4_short(void);                  /* 0x0800a1ac */
extern void case_pulse4_long(void);                   /* 0x0800a1e8 */
extern void case_boot_gpio_a4_output(void);           /* 0x0800ba84 */
extern void case_boot_gpio_a4_high(void);             /* 0x0800bac4 */
extern void case_boot_gpio_a4_low(void);              /* 0x0800bae8 */
extern void case_boot_short_delay_a794(uint32_t count); /* 0x0800a794 */
/* Stock 0x0800A188 (case_route_boolean) */
void case_bus_output_start(uint32_t bit)
{
    if(bit!=0u)case_pulse4_long();
    else case_pulse4_short();
}
/* Stock 0x0800A224 (case_pulse4_extended) */
void case_bus_output_finish(void)
{
    case_boot_gpio_a4_high();case_boot_gpio_a4_output();case_boot_gpio_a4_high();
    case_boot_short_delay_a794(0x17u);
    case_boot_gpio_a4_low();
    case_boot_short_delay_a794(0x15eu);
    case_boot_gpio_a4_high();
}
/* Stock 0x0800A2A2 (case_emit_bits) */
void case_bus_output_send(uint32_t value,uint32_t first)
{
    uint32_t bit=first==1u?6u:7u;
    do{case_bus_output_start((value>>bit)&1u);--bit;}while((int32_t)bit>=0);
}
/* Stock 0x0800C42C (case_transform_word) */
uint32_t case_bus_output_poll(uint32_t *word)
{
    uint32_t bit=0u;
    uint32_t result=case_bus_positive_sample(&bit);
    *word=bit;
    return result;
}

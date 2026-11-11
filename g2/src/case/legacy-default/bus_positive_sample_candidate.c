/* SPDX-License-Identifier: MIT
 * Stock 0x0800b4e0 output-channel (PB2) response bit and timeout. Live GPIO
 * input at 0x50000410 is the external device boundary. As stock, the line
 * changes go through the GPIO leaves, the sample point is 23 counts of
 * 0x0800a794 and the timeout counts 10000 calls of the 0x0800a39c reader,
 * so the response window matches stock (the reduction inlined the reads,
 * shortening the timeout about 4x).
 */
#include <stdint.h>
extern void case_boot_gpio_a4_alt(void);              /* 0x0800bb0c */
extern void case_boot_gpio_a4_high(void);             /* 0x0800bac4 */
extern void case_boot_gpio_a4_output(void);           /* 0x0800ba84 */
extern void case_boot_gpio_a4_low(void);              /* 0x0800bae8 */
extern void case_boot_gpio_a4_input(void);            /* 0x0800ba44 */
extern uint32_t case_boot_gpio_a4_read(void);         /* 0x0800a39c */
extern void case_boot_short_delay_a794(uint32_t count); /* 0x0800a794 */
/* Stock 0x0800B4E0 (case_probe_low_signal) */
uint32_t case_bus_positive_sample(uint32_t *sample)
{
    volatile uint32_t *diag=(volatile uint32_t *)(uintptr_t)0x20000000u;
    diag[2]=0u;diag[3]=0u;
    case_boot_gpio_a4_alt();case_boot_gpio_a4_high();case_boot_gpio_a4_output();
    case_boot_gpio_a4_high();case_boot_gpio_a4_low();case_boot_gpio_a4_input();
    case_boot_short_delay_a794(0x17u);
    *sample=(~case_boot_gpio_a4_read())&1u;
    for(int32_t i=1;;++i){
        if(i>10000){diag[3]=1u;return 0u;}
        if(case_boot_gpio_a4_read()!=0u)return 1u;
    }
}

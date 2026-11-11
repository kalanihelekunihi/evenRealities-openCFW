/* SPDX-License-Identifier: MIT
 * Stock 0x0800b53c config-channel (PA3) timed one-bit response sample.
 * GPIO at 0x50000010 is live external input. As stock, both 100000-count
 * waits poll through the 0x0800a3ac reader call and the sample point is
 * 50 counts of 0x0800a7a2 after the falling edge.
 */
#include <stdint.h>
extern void case_boot_gpio_b8_input(void);            /* 0x0800ba64 */
extern void case_boot_gpio_b8_alt(void);              /* 0x0800bb2c */
extern uint32_t case_boot_gpio_b8_read(void);         /* 0x0800a3ac */
extern void case_boot_short_delay_a7a2(uint32_t count); /* 0x0800a7a2 */
/* Stock 0x0800B53C (case_probe_high_signal) */
uint32_t case_bus_response_sample(uint32_t *sample)
{
    volatile uint32_t *diag=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    diag[3]=0u;diag[4]=0u;
    uint32_t ok=1u;
    case_boot_gpio_b8_input();case_boot_gpio_b8_alt();
    for(int32_t i=1;;++i){
        if(i>100000){diag[3]=1u;ok=0u;break;}
        if(case_boot_gpio_b8_read()!=1u)break;
    }
    case_boot_short_delay_a7a2(50u);
    uint32_t bit=(~case_boot_gpio_b8_read())&1u;
    *sample=bit;
    for(int32_t i=1;;++i){
        if(i>100000){diag[4]=1u;ok=0u;break;}
        if(case_boot_gpio_b8_read()!=0u)break;
    }
    *sample=bit;
    return ok;
}

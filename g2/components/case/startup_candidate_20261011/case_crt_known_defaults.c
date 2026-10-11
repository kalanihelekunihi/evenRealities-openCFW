/* SPDX-License-Identifier: MIT
 * CASE initial RAM 0x20000000..0x200001a3 reconstructed by typed C fields.
 * Stock CRT shows every byte outside the named fields is zero.
 */
#include <stdint.h>

extern void case_crt_init_cw221x_battery_profile(void);
extern void case_crt_init_gpio_descriptors(void);
extern void case_crt_init_clock_scheduler_defaults(void);
extern void case_crt_init_policy_flags(void);
extern void case_crt_init_transport_mode(void);

void case_crt_init_known_defaults(void)
{
    volatile uint32_t *ram=(volatile uint32_t *)(uintptr_t)0x20000000u;
    for(uint32_t i=0u;i<0x1a4u/4u;++i)ram[i]=0u;
    case_crt_init_cw221x_battery_profile();
    case_crt_init_gpio_descriptors();
    case_crt_init_clock_scheduler_defaults();
    case_crt_init_policy_flags();
    case_crt_init_transport_mode();
}

/* SPDX-License-Identifier: MIT
 * CASE 0x08008438 and 0x0800b600. Both entry points use the same native
 * transfer plan and peripheral selection, with the stock fatal path.
 */
#include <stdint.h>

extern uint32_t case_boot_clock_gate_enable(uint32_t mask); /* 0x08005048 */
extern uint32_t case_transfer_control_5528(const uint8_t *config);
extern uint32_t case_boot_clock_device_apply(const uint32_t *config,uint32_t count); /* 0x080052e4 */
extern void case_boot_init_failure(void) __attribute__((noreturn)); /* 0x08003e90 */

static void configure_input_system(void)
{
    volatile uint32_t plan[14];
    for (uint32_t i=0;i<14u;++i) plan[i]=0u;
    uint32_t select[4] = {7u,2u,0u,0u};
    (void)case_boot_clock_gate_enable(0x200u);
    plan[0]=10u;
    plan[3]=256u;
    plan[5]=64u;
    plan[6]=1u;
    plan[7]=2u;
    plan[8]=2u;
    plan[10]=8u;
    plan[11]=0x20000u;
    plan[12]=0x2000000u;
    plan[13]=0x20000000u;
    if(case_transfer_control_5528((const uint8_t *)(uintptr_t)plan)!=0u)
        case_boot_init_failure();
    if(case_boot_clock_device_apply(select,2u)!=0u)
        case_boot_init_failure();
}

/* Stock 0x08008438 (case_initialize_application_profile) */
void case_boot_input_initialize(void) { configure_input_system(); }
/* Stock 0x0800B600 (board_peripheral_init) */
void case_policy_system_reset(void) { configure_input_system(); }

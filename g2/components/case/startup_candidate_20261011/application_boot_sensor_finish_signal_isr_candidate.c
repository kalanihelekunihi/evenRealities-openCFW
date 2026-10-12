/* SPDX-License-Identifier: MIT
 * CASE 0x0800c568 notification ISR wrapper, native register shuffle and
 * bound semaphore handle 0x0800c578. The scheduler operation at ce0c is a
 * separate real body contract.
 */
#include <stdint.h>
extern void vEventGroupSetBitsCallback(void *event_group,uint32_t bits);
extern uint32_t case_policy_irq_event_dispatch(uint32_t descriptor,uint32_t event,
                                                uint32_t bits,uint32_t option); /* 0xce0c */
int32_t case_boot_sensor_finish_signal_isr(uint32_t task,uint32_t bits,uint32_t *woken)
{
    return (int32_t)case_policy_irq_event_dispatch((uint32_t)(uintptr_t)vEventGroupSetBitsCallback,task,bits,
                                                    (uint32_t)(uintptr_t)woken);
}

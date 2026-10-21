/* SPDX-License-Identifier: MIT. Stock41b4f6 startup through SVC handoff. */
#include <stdint.h>
extern void opencfw_bl_port_timer_configure(void);
extern void opencfw_boot_first_task_transfer(void);
extern void opencfw_boot_thread_select(void);
extern void opencfw_bl_task_return(void);
uint32_t opencfw_bl_port_start(void) {
    volatile uint32_t *priority=(volatile uint32_t *)(uintptr_t)0xe000ed20;
    *priority|=0x00ff0000;*priority|=0xff000000;
    opencfw_bl_port_timer_configure();
    *(volatile uint32_t *)(uintptr_t)0x200004c4=0;
    opencfw_boot_first_task_transfer();
    /* Stock continuation if SVC returns unexpectedly. */
    opencfw_boot_thread_select();opencfw_bl_task_return();return 0;
}

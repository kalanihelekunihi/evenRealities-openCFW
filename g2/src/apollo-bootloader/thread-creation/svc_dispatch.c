/* SPDX-License-Identifier: MIT
 * FreeRTOS ARMv8-M port C halves of the SVC path, stock 0x41b448 (SVC
 * dispatch, vPortSVCHandler_C) and 0x41b3ba (FPU setup, prvSetupFPU). The
 * naked entries they serve stay in exception_entry.S.
 */
#include <stdint.h>

#define WORD(a) (*(volatile uint32_t *)(uintptr_t)(a))

#define PORT_SVC_START_SCHEDULER 2u

extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_boot_first_task_restore(void);

/* CP10/CP11 full access, then automatic + lazy FP state preservation. */
void opencfw_boot_port_fpu_enable(void)
{
    WORD(0xe000ed88u) |= 0x00f00000u; /* SCB->CPACR */
    WORD(0xe000ef34u) |= 0xc0000000u; /* FPU->FPCCR ASPEN | LSPEN */
}

/* caller_stack is the exception frame of the SVC caller; the SVC number is the
 * immediate byte of the SVC instruction just before the stacked PC. */
void opencfw_boot_svc_dispatch(const uint32_t *caller_stack)
{
    const uint8_t svc_number = ((const uint8_t *)(uintptr_t)caller_stack[6])[-2];

    if (svc_number == PORT_SVC_START_SCHEDULER) {
        opencfw_boot_port_fpu_enable();
        opencfw_boot_first_task_restore();
        return;
    }
    (void)opencfw_bl_mask_interrupts();
    WORD(UINT32_MAX) = 0u; /* configASSERT: unknown SVC number */
    for (;;) {
    }
}

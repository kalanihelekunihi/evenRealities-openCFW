/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern unsigned int open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_STATE
extern unsigned int open_cfw_bootloader_runtime_state_query(void);
#define OPEN_CFW_BOOTLOADER_RUNTIME_STATE() \
    open_cfw_bootloader_runtime_state_query()
#endif

#ifndef OPEN_CFW_BOOTLOADER_GATE_WORD
#define OPEN_CFW_BOOTLOADER_GATE_WORD \
    (*(volatile unsigned int *)(void *)0x200270D4U)
#endif

#ifndef OPEN_CFW_BOOTLOADER_GATE_TRANSITION_HOOK
extern void open_cfw_bootloader_gate_transition_hook(void);
#define OPEN_CFW_BOOTLOADER_GATE_TRANSITION_HOOK() \
    open_cfw_bootloader_gate_transition_hook()
#endif

#ifndef OPEN_CFW_BOOTLOADER_GATE_COMPLETE
extern void open_cfw_bootloader_gate_complete(void);
#define OPEN_CFW_BOOTLOADER_GATE_COMPLETE() \
    open_cfw_bootloader_gate_complete()
#endif

__attribute__((used, noinline))
int open_cfw_bootloader_gate_release(void)
{
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return -6;
    }
    if (OPEN_CFW_BOOTLOADER_RUNTIME_STATE() != 1U) {
        return -1;
    }
    if (OPEN_CFW_BOOTLOADER_GATE_WORD != 1U) {
        return -1;
    }
    OPEN_CFW_BOOTLOADER_GATE_TRANSITION_HOOK();
    OPEN_CFW_BOOTLOADER_GATE_WORD = 2U;
    OPEN_CFW_BOOTLOADER_GATE_COMPLETE();
    return 0;
}

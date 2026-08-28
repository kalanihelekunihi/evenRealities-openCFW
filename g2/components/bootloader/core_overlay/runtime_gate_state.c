/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_STATE
extern unsigned int open_cfw_bootloader_runtime_state_query(void);
#define OPEN_CFW_BOOTLOADER_RUNTIME_STATE() \
    open_cfw_bootloader_runtime_state_query()
#endif

#ifndef OPEN_CFW_BOOTLOADER_GATE_WORD
#define OPEN_CFW_BOOTLOADER_GATE_WORD \
    (*(volatile unsigned int *)(void *)0x200270D4U)
#endif

__attribute__((used, noinline))
unsigned int open_cfw_bootloader_gate_state(void)
{
    unsigned int state = OPEN_CFW_BOOTLOADER_RUNTIME_STATE();

    if (state == 0U) {
        return 3U;
    }
    if (state == 2U) {
        return 2U;
    }
    if (OPEN_CFW_BOOTLOADER_GATE_WORD == 1U) {
        return 1U;
    }
    return 0U;
}

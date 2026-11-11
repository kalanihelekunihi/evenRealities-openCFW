/* SPDX-License-Identifier: MIT. Stock416058/416088/4160b0 wrappers. */
#include <stdint.h>
extern uint32_t opencfw_bl_context_guard(void);
extern uint32_t opencfw_bl_queue_runtime_mode(void);
extern uint32_t opencfw_bl_kernel_start(void);
extern void opencfw_boot_empty_leaf_416028(void);
#define STATE (*(volatile uint32_t *)(uintptr_t)0x200270d4u)
int32_t opencfw_boot_kernel_initialize(void) {
    if (opencfw_bl_context_guard())return -6;
    if (opencfw_bl_queue_runtime_mode()!=1 || STATE!=0)return -1;
    STATE=1;return 0;
}
uint32_t opencfw_boot_kernel_state(void) {
    uint32_t raw=opencfw_bl_queue_runtime_mode();
    if (!raw)return 3;
    if (raw==2)return 2;
    return STATE==1?1:0;
}
int32_t opencfw_boot_kernel_start(void) {
    if (opencfw_bl_context_guard())return -6;
    if (opencfw_bl_queue_runtime_mode()!=1 || STATE!=1)return -1;
    opencfw_boot_empty_leaf_416028();
    STATE=2;(void)opencfw_bl_kernel_start();return 0;
}

/* Stock entry names that branch straight to the provider above. */
__typeof__(opencfw_boot_kernel_start) opencfw_provider_4160b0 __attribute__((alias("opencfw_boot_kernel_start")));

/* Stock entry names that reach the provider above directly. */
__typeof__(opencfw_boot_kernel_initialize) opencfw_provider_416058 __attribute__((alias("opencfw_boot_kernel_initialize")));
__typeof__(opencfw_boot_kernel_state) opencfw_bl_kernel_state __attribute__((alias("opencfw_boot_kernel_state")));

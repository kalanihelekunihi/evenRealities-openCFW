/* Source-owned DFU and manager thread teardown leaves from locked stock. */
#include <stdint.h>

extern void opencfw_boot_dfu_thread_terminate(uint32_t handle);
extern void opencfw_provider_416200(uintptr_t handle);

uint32_t opencfw_boot_dfu_thread_deinit_native(void)
{
    volatile uint32_t *const handle = (volatile uint32_t *)(uintptr_t)0x200004d4u;
    if (*handle != 0u) {
        opencfw_boot_dfu_thread_terminate(*handle);
        *handle = 0u;
    }
    return 0u;
}

/* Stock 0x42e3ca (guarded_context_teardown_42e3ca) */
uint32_t opencfw_boot_manager_thread_deinit(void)
{
    volatile uint32_t *const handle = (volatile uint32_t *)(uintptr_t)0x200004fcu;
    if (*handle != 0u) {
        opencfw_provider_416200(*handle);
        *handle = 0u;
    }
    return 0u;
}

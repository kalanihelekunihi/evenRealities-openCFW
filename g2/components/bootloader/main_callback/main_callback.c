/* SPDX-License-Identifier: MIT
 * Bounded reconstruction of the initialized callback at 0x42E39C.
 * Runtime/thread services remain explicit provider cuts.
 */
#include <stdint.h>

#if defined(OPENCFW_MAIN_CALLBACK_AT_STOCK_ADDRESS)
#define CALLBACK_ENTRY_SECTION __attribute__((section(".callback_text")))
#else
#define CALLBACK_ENTRY_SECTION
#endif

extern void opencfw_provider_416058(void);
extern int32_t opencfw_provider_4160fe(void (*entry)(void),
                                       uint32_t argument,
                                       const void *attributes);
extern void opencfw_provider_4160b0(void);
extern void opencfw_provider_41b2f8(void);

/* This is the exact first 36-byte attribute record consumed by the callback. */
__attribute__((section(".rodata.manager_attributes"), used))
const uint32_t opencfw_boot_manager_attributes[9] = {
    0x434134u, 0u, 0x20026ac0u, 0x70u, 0x20018aa0u,
    0x4000u, 0x30u, 1u, 0u,
};

__attribute__((section(".rodata.manager_name"), used))
const char opencfw_boot_manager_name[] = "manager";

static volatile uint32_t *const manager_handle =
    (volatile uint32_t *)(uintptr_t)0x200004fcu;

__attribute__((noreturn, noinline))
static void allocation_failure(void)
{
    opencfw_provider_41b2f8();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0;
    for (;;) {
        __asm__ volatile("b ." ::: "memory");
    }
}

CALLBACK_ENTRY_SECTION void opencfw_boot_main_callback(void)
{
    opencfw_provider_416058();
    *manager_handle = (uint32_t)opencfw_provider_4160fe(
        (void (*)(void))(uintptr_t)0x42e2f9u, 0u,
        opencfw_boot_manager_attributes);
    if (*manager_handle == 0u)
        allocation_failure();
    opencfw_provider_4160b0();
}

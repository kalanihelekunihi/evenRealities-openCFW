/* Stock bootloader f89a4c46 queue reset body 0x419be8..0x419c9b.
 * The caller owns a nonzero q[15] message count; stock UDIV uses it directly.
 */
#include <stdint.h>

extern uint32_t opencfw_bl_mask_interrupts(void);
extern void opencfw_bl_kernel_enter(void);
extern void opencfw_bl_kernel_exit(void);
extern uint32_t opencfw_bl_remove_event_waiter(uint32_t *list);
extern void opencfw_bl_kernel_reschedule(void);
extern void opencfw_boot_list_initialize(uint32_t *list);

static void queue_reset_fatal(void)
{
    (void)opencfw_bl_mask_interrupts();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) __asm__ volatile("b ." ::: "memory");
}

uint32_t opencfw_boot_queue_reset(uint32_t *q, uint32_t clear_waiters)
{
    if (q == 0) queue_reset_fatal();
    const uint32_t count = q[15];
    const uint32_t item_size = q[16];
    /* `count != 0` is the stock caller precondition, not a default value. */
    if (UINT32_MAX / count < item_size) queue_reset_fatal();

    opencfw_bl_kernel_enter();
    q[2] = q[0] + count * item_size;
    q[14] = 0u;
    q[1] = q[0];
    q[3] = q[0] + (count - 1u) * item_size;
    ((uint8_t *)q)[0x44] = 0xffu;
    ((uint8_t *)q)[0x45] = 0xffu;

    if (clear_waiters == 0u) {
        if (q[4] != 0u && opencfw_bl_remove_event_waiter(q + 4) != 0u)
            opencfw_bl_kernel_reschedule();
    } else {
        opencfw_boot_list_initialize(q + 4);
        opencfw_boot_list_initialize(q + 9);
    }
    opencfw_bl_kernel_exit();
    return 1u;
}

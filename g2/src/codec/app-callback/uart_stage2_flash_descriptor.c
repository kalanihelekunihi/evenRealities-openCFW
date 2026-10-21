/* SPDX-License-Identifier: MIT
 * Retained seeded bodies 0x100033ac (flash-probe wait/dispatch) and
 * 0x10004da4 (64-bit tick read). Product probe pointer and status live
 * at fixed RAM addresses; they are real runtime contracts.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_launch_61a4(const char *, ...);

uint64_t gx8002_uart_stage2_tick_4da4(void)
{
    volatile const uint32_t *clock =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20009964);
    uint32_t low = clock[0];
    uint32_t high = clock[1];
    return ((uint64_t)high << 32) | low;
}

void *gx8002_uart_stage2_flash_descriptor_33ac(
    uint32_t device, uint32_t mode, uint32_t clock, uint32_t block_size)
{
    volatile uint8_t *status =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2000994c);
    volatile const uint32_t *probe_slot =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20009244);
    uint64_t started = gx8002_uart_stage2_tick_4da4();
    for (;;) {
        if (*status < 2u) {
            uint32_t address = *probe_slot;
            void *(*probe)(uint32_t, uint32_t, uint32_t, uint32_t) =
                (void *(*)(uint32_t, uint32_t, uint32_t, uint32_t))
                (uintptr_t)address;
            void *descriptor = probe(device, mode, clock, block_size);
            if (descriptor != 0) {
                *status = 1u;
                return descriptor;
            }
        }
        if (gx8002_uart_stage2_tick_4da4() - started > UINT64_C(4999999)) {
            gx8002_uart_stage2_launch_61a4("flash probe waitting timeout.\n");
            return 0;
        }
    }
}

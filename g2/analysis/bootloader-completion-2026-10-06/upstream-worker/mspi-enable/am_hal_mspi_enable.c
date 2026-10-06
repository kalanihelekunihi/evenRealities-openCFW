/* Recovered from authenticated Apollo bootloader instructions at 0x425066.
 * Only mspi_cq_init remains a platform provider seam. */
#include <stdint.h>
#include "ambiq_mspi_compat.h"

enum {
    HANDLE_CONFIGURED = 0x08,
    HANDLE_QUEUE_ARGUMENT = 0x14,
    HANDLE_QUEUE_CONTEXT = 0x18,
    HANDLE_QUEUE_COUNT_A = 0x1c,
    HANDLE_QUEUE_COUNT_B = 0x20,
    HANDLE_QUEUE_RESET_0 = 0x82c,
    HANDLE_QUEUE_RESET_1 = 0x82d,
    HANDLE_QUEUE_RESET_2 = 0x830,
    HANDLE_QUEUE_RESET_3 = 0x838,
    HANDLE_QUEUE_RESET_4 = 0x83c,
    HANDLE_QUEUE_RESET_5 = 0x840,
    HANDLE_QUEUE_RESET_6 = 0x844,
    HANDLE_QUEUE_RESET_7 = 0x854,
    HANDLE_QUEUE_RESET_8 = 0x85c,
    CQCFG_OFFSET = 0x2b4,
    MSPI0_BASE = 0x40060000,
    MSPI_STRIDE = 0x1000,
    CQCFG_RESET_VALUE = 0x00400080,
    PREFIX_VALID_MASK = 0x01ffffff,
    PREFIX_VALID_VALUE = 0x01bebebe,
    PREFIX_ENABLE_BIT = 0x02000000,
    STATUS_INVALID_HANDLE = 2,
    STATUS_INVALID_OPERATION = 7
};

extern void mspi_cq_init(uint32_t module, uint32_t queue_argument,
                         uint32_t queue_context);

_Static_assert(sizeof(am_hal_mspi_state_t) == 0x8d0,
               "stock sparse state extent changed");
_Static_assert(offsetof(am_hal_mspi_state_t, pTCB) == HANDLE_QUEUE_CONTEXT,
               "stock queue-context slot changed");
_Static_assert(offsetof(am_hal_mspi_state_t, ui32NumCQEntries) ==
                   HANDLE_QUEUE_COUNT_B,
               "stock CQ counter slot changed");

uint32_t opencfw_bl_mspi_enable(void *handle)
{
    volatile uint8_t *const bytes = (volatile uint8_t *)handle;
    uint32_t prefix;

    if (handle == 0)
        return STATUS_INVALID_HANDLE;

    prefix = *(volatile uint32_t *)(void *)bytes;
    if ((prefix & PREFIX_VALID_MASK) != PREFIX_VALID_VALUE)
        return STATUS_INVALID_HANDLE;
    if (bytes[HANDLE_CONFIGURED] == 0u)
        return STATUS_INVALID_OPERATION;

    if (*(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_CONTEXT) != 0u) {
        const uint32_t module = *(volatile uint32_t *)(void *)(bytes + 4u);

        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_COUNT_A) = 0u;
        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_COUNT_B) = 0u;
        mspi_cq_init(module,
                     *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_ARGUMENT),
                     *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_CONTEXT));

        *(volatile uint32_t *)(uintptr_t)(MSPI0_BASE + module * MSPI_STRIDE +
                                           CQCFG_OFFSET) = CQCFG_RESET_VALUE;
        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_RESET_7) = 0u;
        bytes[HANDLE_QUEUE_RESET_4] = 0u;
        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_RESET_6) = 0u;
        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_RESET_3) = 0u;
        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_RESET_5) = 0u;
        bytes[HANDLE_QUEUE_RESET_0] = 0u;
        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_RESET_2) = 0u;
        bytes[HANDLE_QUEUE_RESET_1] = 1u;
        *(volatile uint32_t *)(void *)(bytes + HANDLE_QUEUE_RESET_8) = 0u;
    }

    prefix = *(volatile uint32_t *)(void *)bytes;
    *(volatile uint32_t *)(void *)bytes = prefix | PREFIX_ENABLE_BIT;
    return 0u;
}

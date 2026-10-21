/* SPDX-License-Identifier: MIT
 * Readable source candidate for stock helper 0x004205F4. This wrapper
 * constructs one PIO command; transfer and error-reporting bodies are
 * explicit linked providers.
 */
#include "nor_read_status.h"
#include <stddef.h>

typedef enum {
    OPENCFW_MSPI_RX = 0,
    OPENCFW_MSPI_TX = 1
} opencfw_mspi_direction_t;

typedef struct {
    uint32_t byte_count;                /* +0 */
    uint8_t scrambling;                 /* +4 */
    uint8_t dcx;                        /* +5 */
    opencfw_mspi_direction_t direction; /* +6 */
    uint8_t send_address;               /* +7 */
    uint32_t device_address;            /* +8 */
    uint8_t send_instruction;           /* +12 */
    uint16_t device_instruction;        /* +14 */
    uint8_t turnaround;                 /* +16 */
    uint8_t write_latency;              /* +17 */
    uint8_t continuation;               /* +18 */
    uint8_t reserved;                   /* +19 */
    uint32_t *buffer;                   /* +20 */
} opencfw_mspi_pio_transfer_t;

_Static_assert(sizeof(void *) == 4, "stock wrapper uses 32-bit pointers");
_Static_assert(sizeof(opencfw_mspi_pio_transfer_t) == 24,
               "stock PIO command is 24 bytes");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, direction) == 6,
               "PIO direction offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, device_address) == 8,
               "PIO address offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t,
                         device_instruction) == 14,
               "PIO instruction offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, buffer) == 20,
               "PIO buffer offset");

enum {
    OPENCFW_AM_HAL_STATUS_INVALID_HANDLE = 2,
    OPENCFW_AM_HAL_STATUS_OUT_OF_RANGE = 5,
    OPENCFW_AM_HAL_STATUS_INVALID_ARG = 6
};

#define OPENCFW_ACTIVE_MSPI_SLOT UINT32_C(0x200270dc)
#define OPENCFW_NOR_ADDRESS_LIMIT UINT32_C(0x02000000)
#define OPENCFW_TRANSFER_TIMEOUT_USEC UINT32_C(1000000)
#define OPENCFW_ERROR_LOG_MODULE UINT32_C(0x00431420)

extern uint32_t opencfw_bl_mspi_blocking_transfer(uint32_t handle,
    const opencfw_mspi_pio_transfer_t *transfer,
    uint32_t timeout_usec);                                  /* 0x004262E0 */
extern void opencfw_bl_status_transfer_error(uint32_t module,
    uint16_t instruction, uint32_t address, uint32_t length,
    uint32_t status);                                        /* 0x00415FAE */

uint32_t opencfw_bl_mspi_status_transfer(uint32_t instruction,
    uint32_t address, uint32_t send_address, void *destination,
    uint32_t length)
{
    const uint32_t stock_instruction = (uint16_t)instruction;
    const uint32_t handle = *(volatile const uint32_t *)(uintptr_t)
        OPENCFW_ACTIVE_MSPI_SLOT;
    if (handle == 0u)
        return OPENCFW_AM_HAL_STATUS_INVALID_HANDLE;
    if (destination == NULL || length == 0u)
        return OPENCFW_AM_HAL_STATUS_INVALID_ARG;
    if (address >= OPENCFW_NOR_ADDRESS_LIMIT)
        return OPENCFW_AM_HAL_STATUS_OUT_OF_RANGE;

    const uint8_t transmit_address = (uint8_t)send_address;
    const opencfw_mspi_pio_transfer_t transfer = {
        .byte_count = length,
        .scrambling = 0,
        .dcx = 0,
        .direction = OPENCFW_MSPI_RX,
        .send_address = transmit_address != 0u ? 1u : 0u,
        .device_address = transmit_address != 0u ? address : 0u,
        .send_instruction = 1,
        .device_instruction = (uint16_t)stock_instruction,
        .turnaround = 1,
        .write_latency = 0,
        .continuation = 0,
        .reserved = 0,
        .buffer = (uint32_t *)destination
    };

    const uint32_t status = opencfw_bl_mspi_blocking_transfer(
        handle, &transfer, OPENCFW_TRANSFER_TIMEOUT_USEC);
    if (status != 0u)
        opencfw_bl_status_transfer_error(OPENCFW_ERROR_LOG_MODULE,
            (uint16_t)stock_instruction, address, length, status);
    return status;
}

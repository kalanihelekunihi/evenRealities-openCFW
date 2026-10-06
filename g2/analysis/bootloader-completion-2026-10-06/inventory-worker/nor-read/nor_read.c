/* SPDX-License-Identifier: MIT
 * Readable candidate for stock Apollo bootloader function 0x00420F70.
 * The four local setup/teardown and HAL calls remain explicit linked
 * providers. No transfer behavior is attributed to their implementations.
 */
#include "nor_read.h"
#include <stddef.h>

typedef enum {
    OPENCFW_MSPI_RX = 0,
    OPENCFW_MSPI_TX = 1
} opencfw_mspi_direction_t;

/* Layout recovered from the instructions at 0x00420F70 and corroborated by
 * the public AmbiqSuite Apollo510 PIO transfer declaration. Target compiles
 * with -fshort-enums; pointers and uint32_t are both four bytes.
 */
typedef struct {
    uint32_t byte_count;              /* +0 */
    uint8_t scrambling;               /* +4 */
    uint8_t dcx;                      /* +5 */
    opencfw_mspi_direction_t direction; /* +6 */
    uint8_t send_address;             /* +7 */
    uint32_t device_address;          /* +8 */
    uint8_t send_instruction;         /* +12 */
    uint16_t device_instruction;      /* +14 */
    uint8_t turnaround;               /* +16 */
    uint8_t write_latency;            /* +17 */
    uint8_t continuation;             /* +18 */
    uint8_t reserved;                 /* +19, zeroed by stock */
    uint32_t *buffer;                 /* +20 */
} opencfw_mspi_pio_transfer_t;

_Static_assert(sizeof(void *) == 4, "stock ABI uses 32-bit pointers");
_Static_assert(sizeof(opencfw_mspi_pio_transfer_t) == 24,
               "stock PIO command occupies 24 bytes");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, direction) == 6,
               "stock direction offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, device_address) == 8,
               "stock address offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, device_instruction) == 14,
               "stock instruction offset");
_Static_assert(offsetof(opencfw_mspi_pio_transfer_t, buffer) == 20,
               "stock buffer offset");

enum {
    /* AmbiqSuite 5.1 status enumeration order, matched to returned immediates. */
    OPENCFW_AM_HAL_STATUS_OUT_OF_RANGE = 5,
    OPENCFW_AM_HAL_STATUS_INVALID_ARG = 6,
    OPENCFW_MX25_READ_4BYTE = 0x006c
};

#define OPENCFW_MX25_ADDRESS_LIMIT UINT32_C(0x02000000)
#define OPENCFW_MSPI_TIMEOUT_USEC  UINT32_C(1000000)
#define OPENCFW_ACTIVE_MSPI_SLOT   UINT32_C(0x200270dc)

/* These aliases map to the exact local call destinations visible in the
 * locked image. In the bounded comparison they are intercepted stubs.
 */
extern void opencfw_bl_nor_read_before(void);       /* 0x0041FF08 */
extern void opencfw_bl_nor_read_configure(void);    /* 0x00420E8C */
extern void opencfw_bl_nor_read_delay(void);        /* 0x004207F4 */
extern void opencfw_bl_nor_read_after(void);         /* 0x0041FF1E */
extern uint32_t opencfw_bl_mspi_blocking_transfer(
    uint32_t handle, const opencfw_mspi_pio_transfer_t *transfer,
    uint32_t timeout_usec);                         /* 0x004262E0 */

uint32_t opencfw_boot_nor_read(uint32_t address, void *destination,
                               uint32_t length, uint32_t reserved)
{
    (void)reserved;
    const uint32_t handle = *(volatile const uint32_t *)(uintptr_t)
        OPENCFW_ACTIVE_MSPI_SLOT;
    if (handle == 0u || destination == NULL || length == 0u)
        return OPENCFW_AM_HAL_STATUS_INVALID_ARG;
    if (address >= OPENCFW_MX25_ADDRESS_LIMIT)
        return OPENCFW_AM_HAL_STATUS_OUT_OF_RANGE;

    opencfw_bl_nor_read_before();
    opencfw_bl_nor_read_configure();
    opencfw_bl_nor_read_delay();

    const opencfw_mspi_pio_transfer_t transfer = {
        .byte_count = length,
        .scrambling = 0,
        .dcx = 0,
        .direction = OPENCFW_MSPI_RX,
        .send_address = 1,
        .device_address = address,
        .send_instruction = 1,
        .device_instruction = OPENCFW_MX25_READ_4BYTE,
        .turnaround = 1,
        .write_latency = 0,
        .continuation = 0,
        .reserved = 0,
        .buffer = (uint32_t *)destination
    };
    const uint32_t status = opencfw_bl_mspi_blocking_transfer(
        handle, &transfer, OPENCFW_MSPI_TIMEOUT_USEC);
    opencfw_bl_nor_read_after();
    return status;
}

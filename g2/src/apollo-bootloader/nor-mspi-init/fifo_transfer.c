/* SPDX-License-Identifier: MIT. Stock423e40/423e8a FIFO byte movement.
 * Polling is a separate provider. TX intentionally reads complete words even
 * for a partial final word and returns the last poll status; no early abort.
 */
#include <stdint.h>
extern uint32_t opencfw_hal_status_poll(uint32_t, uintptr_t, uint32_t, uint32_t, uint32_t);
uint32_t opencfw_hal_mspi_fifo_write(uint32_t module, uint32_t address,
                                    uint32_t length, uint32_t timeout) {
    if (module >= 4u) return 5;
    uintptr_t base = 0x40060000u + (module << 12);
    const uint32_t *buffer = (const uint32_t *)(uintptr_t)address;
    uint32_t status = 0;
    for (uint32_t i = 0; (i << 2) < length; ++i) {
        *(volatile uint32_t *)(base + 0x10u) = buffer[i];
        status = opencfw_hal_status_poll(timeout, base + 0x18u, 0x3fu, 0x10u, 0u);
    }
    return status;
}
uint32_t opencfw_hal_mspi_fifo_read(uint32_t module, uint32_t address,
                                   uint32_t length, uint32_t timeout) {
    if (module >= 4u) return 5;
    uintptr_t base = 0x40060000u + (module << 12);
    uint32_t *buffer = (uint32_t *)(uintptr_t)address;
    uint32_t words = length >> 2;
    for (uint32_t i = 0; i < words; ++i) {
        uint32_t status = opencfw_hal_status_poll(timeout, base + 0x1cu, 0x3fu, 0u, 0u);
        if (status != 0u) return status;
        buffer[i] = *(volatile uint32_t *)(base + 0x14u);
    }
    uint32_t tail = length & 3u;
    if (tail != 0u) {
        uint32_t status = opencfw_hal_status_poll(timeout, base + 0x1cu, 0x3fu, 0u, 0u);
        if (status != 0u) return status;
        uint32_t word = *(volatile uint32_t *)(base + 0x14u);
        uint8_t *out = (uint8_t *)(uintptr_t)(address + words * 4u);
        for (uint32_t i = 0; i < tail; ++i) out[i] = (uint8_t)(word >> (i * 8u));
    }
    return 0;
}

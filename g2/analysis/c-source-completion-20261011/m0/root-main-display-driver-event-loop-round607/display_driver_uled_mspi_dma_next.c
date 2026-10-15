/* Apollo DMA next-descriptor provider 0x4bfdf4. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_mspi_dma_pin_prepare_4c44bc(uint32_t, uint32_t);

uint32_t display_driver_uled_mspi_dma_next_4bfdf4(uint32_t *h) {
    uint32_t instance = h[1];
    uint32_t ring_index = (h[0x850u / 4u] + 1u) % h[0x848u / 4u];
    const uint32_t *entry = (const uint32_t *)(uintptr_t)
        (h[0x854u / 4u] + ring_index * 0x18u);
    uint32_t status = display_driver_uled_mspi_dma_pin_prepare_4c44bc(
        4u, (instance + 0x10u) & 0xffu);
    if (status != 0u) return status;
    volatile uint32_t *r = (volatile uint32_t *)(uintptr_t)
        (0x40060000u + (instance << 12));
    r[0x100u / 4u] = 0u;
    r[0x108u / 4u] = entry[0];
    r[0x10cu / 4u] = entry[1];
    r[0x110u / 4u] = entry[2];
    r[0x100u / 4u] = entry[3];
    return 0u;
}

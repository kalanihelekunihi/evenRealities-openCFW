/* Apollo MSPI DMA wrappers 0x4bfd44 and 0x4bfd62. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_mspi_dma_pin_prepare_4c44bc(uint32_t, uint32_t);
extern uint32_t display_driver_uled_mspi_dma_queue_start_538e3c(uint32_t);
extern uint32_t display_driver_uled_mspi_dma_queue_stop_538e8c(uint32_t);

uint32_t display_driver_uled_mspi_dma_start_4bfd44(uint32_t *h) {
    uint32_t status = display_driver_uled_mspi_dma_pin_prepare_4c44bc(
        4u, (h[1] + 0x10u) & 0xffu);
    if (status == 0u) return display_driver_uled_mspi_dma_queue_start_538e3c(h[0x828u/4u]);
    return status;
}
uint32_t display_driver_uled_mspi_dma_stop_4bfd62(uint32_t *h) {
    return display_driver_uled_mspi_dma_queue_stop_538e8c(h[0x828u/4u]);
}

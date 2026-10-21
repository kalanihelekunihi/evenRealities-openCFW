/* SPDX-License-Identifier: MIT
 * Image-B UART DMA submit 0x10004740..0x1000479d.
 * Stock binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Fifth context parameter is the native stack argument. Port records have
 * 0x80-byte stride at the literal shared-RAM base 0x20016b84.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_irq_save_1000486c(void);
extern void gx8002_image_b_irq_restore_10004878(uint32_t previous);
extern int32_t gx8002_image_b_uart_dma_apply_100040e8(
    volatile uint32_t *record, uint32_t source, uint32_t length);

int32_t gx8002_image_b_uart_dma_send_10004740(
    uint32_t port, const uint8_t *source, uint32_t length,
    uint32_t callback, uint32_t context)
{
    volatile uint32_t *record = (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x20016b84) + port * 128u);
    if (source == 0 || callback == 0u) return -1;
    record[0x6cu / 4u] = callback;
    uint32_t installed = record[0x2cu / 4u];
    record[0x44u / 4u] = 2u;
    record[0x74u / 4u] = (uint32_t)(uintptr_t)source;
    record[0x78u / 4u] = length;
    record[0x70u / 4u] = context;
    record[0x7cu / 4u] = UINT32_MAX;
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)record[1];
    if (installed == 0u) {
        uint32_t previous = gx8002_image_b_irq_save_1000486c();
        registers[1] |= 2u;
        gx8002_image_b_irq_restore_10004878(previous);
        return 0;
    }
    registers[0xa8u / 4u] = 1u;
    return gx8002_image_b_uart_dma_apply_100040e8(
        record, (uint32_t)(uintptr_t)source, length);
}

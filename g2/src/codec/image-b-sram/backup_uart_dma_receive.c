/* SPDX-License-Identifier: MIT
 * Image-B UART DMA receive submit 0x100047a4..0x10004801.
 * Stock binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Fifth context argument is native r18 from caller stack.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_irq_save_1000486c(void);
extern void gx8002_image_b_irq_restore_10004878(uint32_t previous);
extern int32_t gx8002_image_b_uart_dma_receive_apply_10004188(
    volatile uint32_t *record, uint32_t destination, uint32_t length);

int32_t gx8002_image_b_uart_dma_receive_100047a4(
    uint32_t port, uint8_t *destination, uint32_t length,
    uint32_t callback, uint32_t context)
{
    volatile uint32_t *record = (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x20016b84) + port * 128u);
    if (destination == 0 || callback == 0u) return -1;
    record[0x58u / 4u] = callback;
    uint32_t installed = record[0x2cu / 4u];
    record[0x40u / 4u] = 2u;
    record[0x60u / 4u] = (uint32_t)(uintptr_t)destination;
    record[0x64u / 4u] = length;
    record[0x5cu / 4u] = context;
    record[0x68u / 4u] = UINT32_MAX;
    if (installed == 0u) {
        uint32_t previous = gx8002_image_b_irq_save_1000486c();
        volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)record[1];
        registers[1] |= 1u;
        gx8002_image_b_irq_restore_10004878(previous);
        return 0;
    }
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)record[1];
    registers[0xa8u / 4u] = 1u;
    return gx8002_image_b_uart_dma_receive_apply_10004188(
        record, (uint32_t)(uintptr_t)destination, length);
}

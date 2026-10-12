/* SPDX-License-Identifier: MIT
 * Image-B UART DMA preparation 0x100040e8..0x10004183.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * For an out-of-domain port selector the native 12-word stack descriptor's
 * direction word is unwritten. Preserve that ambient input as an explicit
 * contract; the two hardware port values have exact native values 7 and 5.
 */
#include <stdint.h>

extern void gx8002_image_b_dcache_clean_range_10004e74(uint32_t, int32_t);
extern int32_t gx8002_image_b_dma_select_10004b6c(void);
extern uint32_t gx8002_image_b_uart_width_code_10004078(
    uint32_t mask, const uint32_t *fallback, uint32_t use_mask);
extern void gx8002_image_b_dma_callback_10004cb8(
    uint32_t channel, uintptr_t callback, uintptr_t context);
extern int32_t gx8002_image_b_dma_transfer_10004ccc(
    uint32_t source, uint32_t destination, int32_t bytes,
    uint32_t channel, const uint32_t *settings);
extern void gx8002_image_b_uart_transmit_complete_10004034(
    volatile uint32_t *record);
int32_t gx8002_image_b_uart_dma_apply_body_100040e8(
    volatile uint32_t *record, uint32_t source, uint32_t length,
    uint32_t ambient_direction)
{
    uint32_t registers = record[1];
    gx8002_image_b_dcache_clean_range_10004e74(source, (int32_t)length);
    int32_t channel = gx8002_image_b_dma_select_10004b6c();
    if (channel < 0) return -1;
    uint32_t format = record[0x34u / 4u];
    record[0x7cu / 4u] = (uint32_t)channel;
    uint32_t settings[12];
    settings[0] = 0u;
    settings[2] = 0u;
    settings[5] = 0u;
    settings[4] = 0u;
    settings[1] = gx8002_image_b_uart_width_code_10004078(
        format, (const uint32_t *)(const void *)(record + 0x38u / 4u), 1u);
    settings[3] = 0u;
    settings[7] = 1u;
    settings[10] = 0u;
    settings[9] = 1u;
    settings[6] = gx8002_image_b_uart_width_code_10004078(
        format, (const uint32_t *)(const void *)(record + 0x38u / 4u), 1u);
    uint32_t port = record[0];
    settings[8] = port == 0u ? 7u : port == 1u ? 5u :
        ambient_direction;
    settings[11] = 1u;
    gx8002_image_b_dma_callback_10004cb8(
        (uint32_t)channel,
        (uintptr_t)gx8002_image_b_uart_transmit_complete_10004034,
        (uintptr_t)record);
    (void)gx8002_image_b_dma_transfer_10004ccc(
        registers, source, (int32_t)length, (uint32_t)channel, settings);
    return 0;
}

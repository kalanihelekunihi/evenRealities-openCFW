/* SPDX-License-Identifier: MIT
 * Image-B UART receive DMA preparation 0x10004188..0x10004219.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Both width-code calls use the fallback word at record+0x38 (native r2=0).
 */
#include <stdint.h>

extern void gx8002_image_b_dcache_invalidate_range_10004dd8(
    uint32_t address, int32_t length);
extern int32_t gx8002_image_b_dma_select_10004b6c(void);
extern uint32_t gx8002_image_b_uart_width_code_10004078(
    uint32_t mask, const uint32_t *fallback, uint32_t use_mask);
extern void gx8002_image_b_dma_callback_10004cb8(
    uint32_t channel, uintptr_t callback, uintptr_t context);
extern int32_t gx8002_image_b_dma_transfer_10004ccc(
    uint32_t source, uint32_t destination, int32_t bytes,
    uint32_t channel, const uint32_t *settings);
extern void gx8002_image_b_uart_receive_complete_10004054(
    volatile uint32_t *record);

int32_t gx8002_image_b_uart_dma_receive_apply_10004188(
    volatile uint32_t *record, uint32_t destination, uint32_t length)
{
    uint32_t registers = record[1];
    uint32_t invalidate_length = record[0x64u / 4u];
    uint32_t invalidate_address = record[0x60u / 4u];
    gx8002_image_b_dcache_invalidate_range_10004dd8(
        invalidate_address, (int32_t)invalidate_length);
    int32_t channel = gx8002_image_b_dma_select_10004b6c();
    if (channel < 0) return -1;
    uint32_t format = record[0x34u / 4u];
    record[0x68u / 4u] = (uint32_t)channel;
    uint32_t settings[12];
    settings[2] = 1u;
    settings[4] = 1u;
    settings[0] = 0u;
    settings[5] = 0u;
    settings[1] = gx8002_image_b_uart_width_code_10004078(
        format, (const uint32_t *)(const void *)(record + 0x38u / 4u), 0u);
    uint32_t port = record[0];
    if (port == 0u) settings[3] = 6u;
    else if (port == 1u) settings[3] = 4u;
    else return -1;
    settings[7] = 0u;
    settings[10] = 0u;
    settings[9] = 0u;
    settings[6] = gx8002_image_b_uart_width_code_10004078(
        format, (const uint32_t *)(const void *)(record + 0x38u / 4u), 0u);
    settings[11] = 2u;
    settings[8] = 0u;
    gx8002_image_b_dma_callback_10004cb8(
        (uint32_t)channel,
        (uintptr_t)gx8002_image_b_uart_receive_complete_10004054,
        (uintptr_t)record);
    (void)gx8002_image_b_dma_transfer_10004ccc(
        destination, registers, (int32_t)length, (uint32_t)channel, settings);
    return 0;
}

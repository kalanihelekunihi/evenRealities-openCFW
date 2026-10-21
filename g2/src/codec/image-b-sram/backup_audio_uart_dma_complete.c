/* SPDX-License-Identifier: MIT
 * Image-B DMA segment completion callback 0x1000acbc..0x1000acdf.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Native masks callback channel to eight bits, then re-enters the segment
 * sender with an unbounded availability pointer (null third argument).
 */
#include <stdint.h>

extern int32_t gx8002_image_b_audio_uart_segment_send_1000ab7c(
    uint32_t channel, const uint8_t *packet, uint32_t *available);

int32_t gx8002_image_b_audio_uart_dma_complete_1000acbc(
    uint32_t channel, uint32_t context)
{
    (void)context;
    uint32_t selected = channel & 0xffu;
    uintptr_t state;
    if (selected == 0u) state = UINT32_C(0x2002cc20);
    else if (selected == 1u) state = UINT32_C(0x2002cd9c);
    else return -1;
    (void)gx8002_image_b_audio_uart_segment_send_1000ab7c(
        channel, (const uint8_t *)(state + 0x3cu), 0);
    return 0;
}

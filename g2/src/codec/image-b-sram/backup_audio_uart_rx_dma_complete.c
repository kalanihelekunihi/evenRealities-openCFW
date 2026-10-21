/* SPDX-License-Identifier: MIT
 * Image-B UART RX DMA completion callback 0x1000af94..0x1000afb9.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Native supplies null r2/r3 to the receive-packet body; its word-at-zero
 * read is an explicit imported memory contract in that body.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_audio_uart_receive_packet_1000ad60(
    uint32_t channel, volatile uint8_t *packet,
    uint8_t **input, uint32_t *available);

int32_t gx8002_image_b_audio_uart_rx_dma_complete_1000af94(
    uint32_t channel, uint32_t context)
{
    (void)context;
    uint32_t selected = channel & 0xffu;
    uintptr_t state;
    if (selected == 0u) state = UINT32_C(0x2002cc20);
    else if (selected == 1u) state = UINT32_C(0x2002cd9c);
    else return -1;
    (void)gx8002_image_b_audio_uart_receive_packet_1000ad60(
        channel, (volatile uint8_t *)(state + 0x1cu), 0, 0);
    return 0;
}

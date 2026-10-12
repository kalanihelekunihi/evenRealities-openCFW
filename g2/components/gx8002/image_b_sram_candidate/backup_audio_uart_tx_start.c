/* SPDX-License-Identifier: MIT
 * Image-B 0x1000ab10: start one queued UART audio record and register the
 * native TX-complete callback at 0x1000afc4. Both channel-state bases are
 * literal native addresses; final SRAM scatter remains separate.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_ring_empty_1000a00c(
    const volatile int32_t *ring);
extern uint32_t gx8002_image_b_audio_ring_read_10009fbc(
    volatile int32_t *ring, uint8_t *destination);
extern uint32_t gx8002_image_b_audio_resource_mark_1000a898(int32_t resource);
extern int32_t gx8002_image_b_uart_tx_irq_enable_10004650(
    uint32_t port, uint32_t callback, uint32_t context);
extern int32_t gx8002_image_b_uart_tx_irq_disable_10004684(uint32_t port);
extern int32_t gx8002_image_b_audio_uart_tx_complete_1000afc4(
    uint32_t channel, uint32_t available);

int32_t gx8002_image_b_audio_uart_tx_start_1000ab10(uint32_t channel)
{
    uintptr_t base;
    if (channel == 0u) base = UINT32_C(0x2002cc20);
    else if (channel == 1u) base = UINT32_C(0x2002cd9c);
    else return -1;

    volatile uint8_t *state = (volatile uint8_t *)base;
    volatile int32_t *ring = (volatile int32_t *)(base + 0x15cu);
    if (gx8002_image_b_audio_ring_empty_1000a00c(ring) == 0u) {
        *(volatile uint32_t *)(volatile void *)(state + 0x18u) = 1u;
        (void)gx8002_image_b_audio_ring_read_10009fbc(
            ring, (uint8_t *)(uintptr_t)(base + 0x3cu));
        *(volatile uint32_t *)(volatile void *)(state + 0x174u) = 0u;
        uint32_t resource =
            *(volatile uint32_t *)(volatile void *)(state + 0x178u);
        (void)gx8002_image_b_audio_resource_mark_1000a898((int32_t)resource);
        uint32_t port = *(volatile uint32_t *)(volatile void *)(state + 8u);
        (void)gx8002_image_b_uart_tx_irq_enable_10004650(
            port, (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_tx_complete_1000afc4,
            0u);
        return 0;
    }
    *(volatile uint32_t *)(volatile void *)(state + 0x18u) = 0u;
    (void)gx8002_image_b_uart_tx_irq_disable_10004684(channel);
    return -1;
}

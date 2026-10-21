/* SPDX-License-Identifier: MIT
 * Image-B dual-channel UART audio open 0x1000b5f8..0x1000b6c5.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * The callback record labels are exact native NUL-terminated strings at
 * 0x10013634 and 0x1001364c, reconstructed as typed C strings.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_tx_abort_route_10004708(uint32_t port);
extern int32_t gx8002_image_b_uart_rx_abort_route_10004724(uint32_t port);
extern int32_t gx8002_image_b_uart_configure_1000451c(
    uint32_t port, uint32_t configuration);
extern void gx8002_image_b_audio_frame_set_10009fa8(
    uint32_t *frame, uint32_t value, int32_t count, int32_t unit);
extern int32_t gx8002_image_b_uart_rx_irq_enable_100046ac(
    uint32_t port, uint32_t callback, uint32_t context);
extern int32_t gx8002_image_b_audio_uart_rx_irq_1000b198(
    uint32_t port, uint32_t available);
extern int32_t gx8002_image_b_audio_uart_suspend_1000ace8(void);
extern int32_t gx8002_image_b_audio_uart_resume_1000ad10(void);
extern uint32_t gx8002_image_b_audio_record_one_1000a784(const uint32_t *record);
extern uint32_t gx8002_image_b_audio_record_two_1000a7f0(const uint32_t *record);
extern uint32_t gx8002_image_b_audio_resource_take_1000a85c(uint32_t *resource);

static const char suspend_label[] = "UartMessageAsyncSuspend";
static const char resume_label[] = "UartMessageAsyncResume";

int32_t gx8002_image_b_audio_uart_open_1000b5f8(const uint32_t *configuration)
{
    if (configuration == 0) return -1;
    uint32_t port = configuration[0];
    uint32_t selected = port & 0xffu;
    volatile uint32_t *state;
    if (selected == 0u) state = (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cc20);
    else if (selected == 1u) state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cd9c);
    else return -1;
    uint32_t active = state[0xcu / 4u];
    state[8u / 4u] = port;
    if (active != 0u && configuration[3] == 0u) return -1;
    state[0] = configuration[2] == 0u ? UINT32_C(0x42555858) : configuration[2];
    state[0x10u / 4u] = configuration[1];
    (void)gx8002_image_b_uart_tx_abort_route_10004708(port);
    (void)gx8002_image_b_uart_rx_abort_route_10004724(state[8u / 4u]);
    int32_t result = gx8002_image_b_uart_configure_1000451c(
        state[8u / 4u], state[0x10u / 4u]);
    if (result != 0) return -1;
    volatile uint32_t *primary =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cc20);
    if (primary[0xcu / 4u] == 0u || primary[0x188u / 4u] == 0u) {
        gx8002_image_b_audio_frame_set_10009fa8(
            (uint32_t *)(uintptr_t)UINT32_C(0x2002d770),
            UINT32_C(0x2002d1b4), 256, 32);
    }
    if (state[0xcu / 4u] == 0u) {
        gx8002_image_b_audio_frame_set_10009fa8(
            (uint32_t *)(uintptr_t)((uintptr_t)state + 0x15cu),
            (uint32_t)(uintptr_t)((uintptr_t)state + 0x5cu), 256, 32);
    }
    (void)gx8002_image_b_uart_rx_irq_enable_100046ac(
        state[8u / 4u],
        (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_rx_irq_1000b198,
        0u);
    uint32_t first[2] = {
        (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_suspend_1000ace8,
        (uint32_t)(uintptr_t)suspend_label
    };
    uint32_t second[2] = {
        (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_resume_1000ad10,
        (uint32_t)(uintptr_t)resume_label
    };
    (void)gx8002_image_b_audio_record_one_1000a784(first);
    (void)gx8002_image_b_audio_record_two_1000a7f0(second);
    (void)gx8002_image_b_audio_resource_take_1000a85c(
        (uint32_t *)(uintptr_t)((uintptr_t)state + 0x178u));
    state[0xcu / 4u] = 1u;
    return 0;
}

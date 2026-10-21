/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10208458..0x10208529. The channel, queue and
 * registration call order follows direct C-SKY disassembly. The fixed
 * 0x42555858 word and SRAM addresses are stock literals, not invented
 * product defaults. Callback descendants remain typed source contracts.
 */
#include <stdint.h>

extern volatile uint32_t *gx8002_xip_uart_channel_lookup_10207ac0(uint32_t port);
extern uint32_t gx8002_xip_uart_transmit_abort_102036e8(uint32_t port);
extern uint32_t gx8002_xip_uart_receive_abort_10203704(uint32_t port);
extern uint32_t gx8002_xip_uart_initialize_10203530(uint32_t port,
                                                    uint32_t baud);
extern void gx8002_xip_queue_initialize_10206f9c(
    volatile uint32_t *, uint32_t, int32_t, int32_t);
extern uint32_t gx8002_xip_uart_receive_start_1020368c(
    uint32_t port, uint32_t (*callback)(uint32_t, uint32_t), uint32_t context);
extern uint32_t gx8002_xip_uart_receive_callback_10208098(
    uint32_t port, uint32_t level);
extern uint32_t gx8002_xip_uart_message_suspend_10207c74(void);
extern uint32_t gx8002_xip_uart_message_resume_10207c9c(void);
extern uint32_t gx8002_xip_register_suspend_102076c0(const void *);
extern uint32_t gx8002_xip_register_resume_10207718(const void *);
extern uint32_t gx8002_xip_power_lock_create_10207770(void *);

struct gx8002_uart_named_callback {
    uint32_t callback;
    const char *name;
};
_Static_assert(sizeof(struct gx8002_uart_named_callback) == 8,
               "native callback descriptor");

int32_t gx8002_xip_uart_async_initialize_10208458(const uint32_t *settings)
{
    if (settings == (void *)0) return -1;
    const uint32_t port_word = settings[0];
    volatile uint32_t *const channel =
        gx8002_xip_uart_channel_lookup_10207ac0(port_word & 0xffu);
    if (channel == (void *)0) return -1;
    channel[2] = port_word;
    if (channel[3] != 0u && settings[3] == 0u) return -1;
    channel[0] = settings[2] == 0u ? UINT32_C(0x42555858) : settings[2];
    channel[4] = settings[1];
    gx8002_xip_uart_transmit_abort_102036e8(port_word);
    gx8002_xip_uart_receive_abort_10203704(channel[2]);
    if (gx8002_xip_uart_initialize_10203530(channel[2], channel[4]) != 0u)
        return -1;

    volatile uint32_t *first = gx8002_xip_uart_channel_lookup_10207ac0(0u);
    if ((first != (void *)0 && first[3] == 0u) ||
        ((first = gx8002_xip_uart_channel_lookup_10207ac0(1u)) !=
         (void *)0 && first[3] == 0u)) {
        gx8002_xip_queue_initialize_10206f9c(
            (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002ecc4),
            UINT32_C(0x2002e5e4), 0x100, 0x20);
    }
    if (channel[3] == 0u)
        gx8002_xip_queue_initialize_10206f9c(
            channel + 0x57u, (uint32_t)(uintptr_t)(channel + 0x17u),
            0x100, 0x20);
    (void)gx8002_xip_uart_receive_start_1020368c(
        channel[2], gx8002_xip_uart_receive_callback_10208098, 0u);
    const struct gx8002_uart_named_callback suspend = {
        (uint32_t)(uintptr_t)gx8002_xip_uart_message_suspend_10207c74,
        "UartMessageAsyncSuspend"
    };
    const struct gx8002_uart_named_callback resume = {
        (uint32_t)(uintptr_t)gx8002_xip_uart_message_resume_10207c9c,
        "UartMessageAsyncResume"
    };
    (void)gx8002_xip_register_suspend_102076c0(&suspend);
    (void)gx8002_xip_register_resume_10207718(&resume);
    (void)gx8002_xip_power_lock_create_10207770(
        (void *)(uintptr_t)(channel + 0x5eu));
    channel[3] = 1u;
    return 0;
}

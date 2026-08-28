/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of platform/audio/service_codec_porting.c. */
#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SELECTOR
#define OPEN_CFW_SELECTOR 0
#endif

#ifndef OPEN_CFW_CODEC_INIT_FLAG
#define OPEN_CFW_CODEC_INIT_FLAG \
    (*(volatile uint8_t *)(uintptr_t)0x20075014u)
#endif
#ifndef OPEN_CFW_CODEC_ACTIVE_FLAG
#define OPEN_CFW_CODEC_ACTIVE_FLAG \
    (*(volatile uint8_t *)(uintptr_t)0x20075015u)
#endif
#ifndef OPEN_CFW_CODEC_RING
#define OPEN_CFW_CODEC_RING ((void *)(uintptr_t)0x20073ed4u)
#endif
#ifndef OPEN_CFW_CODEC_RX_BUFFER
#define OPEN_CFW_CODEC_RX_BUFFER ((uint8_t *)(uintptr_t)0x200731b0u)
#endif
#ifndef OPEN_CFW_CODEC_RX_CALLBACK
#define OPEN_CFW_CODEC_RX_CALLBACK ((void (*)(void))(uintptr_t)0x0058fb1du)
#endif

#ifndef OPEN_CFW_CODEC_RING_INIT
void open_cfw_codec_ring_init(void *ring, uint8_t *buffer, size_t size);
#define OPEN_CFW_CODEC_RING_INIT(ring, buffer, size) \
    open_cfw_codec_ring_init((ring), (buffer), (size))
#endif
#ifndef OPEN_CFW_CODEC_UART_SET_RX_CALLBACK
void open_cfw_codec_uart_set_rx_callback(uint32_t port, void (*callback)(void));
#define OPEN_CFW_CODEC_UART_SET_RX_CALLBACK(port, callback) \
    open_cfw_codec_uart_set_rx_callback((port), (callback))
#endif
#ifndef OPEN_CFW_CODEC_UART_RESUME
int32_t open_cfw_codec_uart_resume(uint32_t port);
#define OPEN_CFW_CODEC_UART_RESUME(port) open_cfw_codec_uart_resume((port))
#endif
#ifndef OPEN_CFW_CODEC_UART_SUSPEND
int32_t open_cfw_codec_uart_suspend(uint32_t port);
#define OPEN_CFW_CODEC_UART_SUSPEND(port) open_cfw_codec_uart_suspend((port))
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 1
__attribute__((used, noinline))
int32_t open_cfw_codec_uart_init(void)
{
    int32_t status;

    if (OPEN_CFW_CODEC_INIT_FLAG == 0u) {
        OPEN_CFW_CODEC_RING_INIT(OPEN_CFW_CODEC_RING,
            OPEN_CFW_CODEC_RX_BUFFER, 64u);
        OPEN_CFW_CODEC_UART_SET_RX_CALLBACK(3u,
            OPEN_CFW_CODEC_RX_CALLBACK);
        OPEN_CFW_CODEC_INIT_FLAG = 1u;
    }
    if (OPEN_CFW_CODEC_ACTIVE_FLAG != 0u) {
        return 0;
    }
    status = OPEN_CFW_CODEC_UART_RESUME(3u);
    if (status != 0) {
        return -1;
    }
    OPEN_CFW_CODEC_ACTIVE_FLAG = 1u;
    return 0;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 2
__attribute__((used, noinline))
int32_t open_cfw_codec_uart_close(void)
{
    int32_t status;

    if (OPEN_CFW_CODEC_ACTIVE_FLAG == 0u) {
        return 0;
    }
    status = OPEN_CFW_CODEC_UART_SUSPEND(3u);
    if (status != 0) {
        return -1;
    }
    OPEN_CFW_CODEC_ACTIVE_FLAG = 0u;
    return 0;
}
#endif

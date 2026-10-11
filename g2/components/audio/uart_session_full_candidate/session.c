#include <stdint.h>
#include "../codec_uart_lifecycle_offline/lifecycle.h"

/* codec.porting uart_init/uart_close, native 0x58fb52..0x58fca7.
 * Selected lifecycle children implement ring, callback and channel
 * power/config operations; product state remains typed external RAM. */
extern uart3_ring_t g2_audio_uart_ring_state;
extern uint8_t g2_audio_uart_storage[];
extern volatile uint8_t g2_audio_uart_initialized;
extern volatile uint8_t g2_audio_uart_resumed;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.porting";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_porting.c";
static const char init_function[] = "uart_init";
static const char close_function[] = "uart_close";
static const char already[] = "UART already resumed";
static const char simple_already[] = "[codec.porting]UART already resumed";
static const char resume_failed[] = "Failed to resume UART bus: %d";
static const char simple_resume_failed[] =
    "[codec.porting]Failed to resume UART bus: %d";
static const char not_resumed[] = "UART not resumed";
static const char simple_not_resumed[] = "[codec.porting]UART not resumed";
static const char suspend_failed[] = "Failed to suspend UART bus: %d";
static const char simple_suspend_failed[] =
    "[codec.porting]Failed to suspend UART bus: %d";

int32_t audio_uart_session_open(void) {
    if (g2_audio_uart_initialized == 0u) {
        codec_ring_initialize(&g2_audio_uart_ring_state,
                              g2_audio_uart_storage, 64u);
        codec_channel_callback(3u,
                               (uint32_t)(uintptr_t)codec_rx_callback);
        g2_audio_uart_initialized = 1u;
    }
    if (g2_audio_uart_resumed != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, file, init_function, 130u,
                               already);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, simple_already, simple_already);
        return 0;
    }
    const int32_t status = (int32_t)codec_channel_enable(3u);
    if (status != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, init_function, 136u,
                               resume_failed, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, simple_resume_failed,
                             simple_resume_failed, status);
        return -1;
    }
    g2_audio_uart_resumed = 1u;
    return 0;
}

int32_t audio_uart_session_close(void) {
    if (g2_audio_uart_resumed == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, file, close_function, 152u,
                               not_resumed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, simple_not_resumed,
                             simple_not_resumed);
        return 0;
    }
    const int32_t status = (int32_t)codec_channel_disable(3u);
    if (status != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, close_function, 158u,
                               suspend_failed, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, simple_suspend_failed,
                             simple_suspend_failed, status);
        return -1;
    }
    g2_audio_uart_resumed = 0u;
    return 0;
}

void audio_uart_set_baud(uint32_t baud) {
    (void)codec_uart_baud(baud);
}

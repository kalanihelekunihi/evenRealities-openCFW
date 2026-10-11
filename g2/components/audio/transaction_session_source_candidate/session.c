#include <stdint.h>

/* gx8002_host_init/release, native 0x57ba88 and 0x57baec.
 * Lower UART session operations retain their own real hardware contracts. */
extern int32_t audio_uart_session_open(void);
extern int32_t audio_uart_session_close(void);
extern void audio_uart_set_baud(uint32_t baud);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";
static const char function[] = "gx8002_host_init";
static const char failed[] = "Failed to initialize UART: %d";
static const char simple_failed[] =
    "[codec.host]Failed to initialize UART: %d";

int32_t audio_transaction_init(void) {
    const int32_t status = audio_uart_session_open();
    if (status != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 45u,
                               failed, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, simple_failed,
                             simple_failed, status);
        return status;
    }
    audio_uart_set_baud(115200u);
    return 0;
}

void audio_transaction_cleanup(void) {
    (void)audio_uart_session_close();
}

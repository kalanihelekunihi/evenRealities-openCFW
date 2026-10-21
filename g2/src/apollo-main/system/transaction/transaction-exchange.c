#include <stdint.h>

/* gx8002_read_uart_data, native 0x57c442..0x57c511.
 * Selected codec_response_read owns the blocking framing loop. */
extern int32_t codec_response_read(uint8_t *buffer, uint16_t capacity,
                                   uint32_t timeout);
extern void audio_dump_hex(const char *label, uint32_t width,
                           const void *data, uint32_t length);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";
static const char function[] = "gx8002_read_uart_data";
static const char failed[] = "UART read failed: %d";
static const char simple_failed[] =
    "[codec.host]UART read failed: %d";
static const char received[] = "UART read: %d bytes";
static const char simple_received[] =
    "[codec.host]UART read: %d bytes";
static const char dump_label[] = "8002_rx";

int32_t audio_transaction_exchange(void *buffer, uint32_t capacity,
                                    uint16_t *length, uint32_t timeout) {
    if (buffer == 0 || length == 0 || (uint16_t)capacity == 0u)
        return -1;
    const int32_t result = codec_response_read(buffer, (uint16_t)capacity,
                                                timeout);
    if (result < 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, file, function, 299u,
                               failed, result);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x10400000u, simple_failed,
                             simple_failed, result);
        return result;
    }
    *length = (uint16_t)result;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, file, function, 304u,
                           received, *length);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10400000u, simple_received,
                         simple_received, *length);
    audio_dump_hex(dump_label, 16u, buffer, *length);
    return 0;
}

/* Native conversate_data_recv_handler 0x5b08a2..0x5b09dd.
 * The stock unsupported type-1 subtype branch falls through to route 8. */
#include <stdint.h>

extern uint32_t audio_conversate_dispatch_5b4904(uint32_t, const uint8_t *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "conversate_data_recv_handler";
static const char unknown_ctrl[] = "unknown ctrl cmd=%d";
static const char unknown_ctrl_short[] = "[conversate]unknown ctrl cmd=%d";
static const char unknown_command[] = "unknown command id=%d";
static const char unknown_command_short[] = "[conversate]unknown command id=%d";

static void log_unknown(uint32_t line, const char *message,
                        const char *short_message, uint32_t value) {
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, path, function, line, message, value);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x08400000u, short_message, short_message, value);
}

uint32_t audio_conversate_data_handler_5b08a2(void *message_ptr) {
    const uint8_t *const message = (const uint8_t *)message_ptr;
    const uint8_t *const payload = message + 4u;
    if (message[0] == 1u) {
        switch (message[4]) {
        case 1u: return audio_conversate_dispatch_5b4904(1u, payload, 0x94u);
        case 2u: return audio_conversate_dispatch_5b4904(4u, payload, 0x94u);
        case 3u: return audio_conversate_dispatch_5b4904(2u, payload, 0x94u);
        case 4u: return audio_conversate_dispatch_5b4904(3u, payload, 0x94u);
        case 5u: return audio_conversate_dispatch_5b4904(5u, payload, 0x94u);
        default:
            log_unknown(343u, unknown_ctrl, unknown_ctrl_short, message[4]);
            return audio_conversate_dispatch_5b4904(8u, payload, 0xaa8u);
        }
    }
    switch (message[0]) {
    case 3u: return audio_conversate_dispatch_5b4904(8u, payload, 0xaa8u);
    case 5u: return audio_conversate_dispatch_5b4904(10u, payload, 0x48cu);
    case 6u: return audio_conversate_dispatch_5b4904(11u, payload, 0x408u);
    case 7u: return audio_conversate_dispatch_5b4904(9u, payload, 0xfa8u);
    case 255u: return audio_conversate_dispatch_5b4904(12u, payload, 1u);
    default:
        log_unknown(357u, unknown_command, unknown_command_short, message[0]);
        return 1u;
    }
}

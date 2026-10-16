/* Stock Terminal overlay-focus publication 0x5e5498 -> 0x5cf134. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence; /* stock RAM 0x20074fff */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t command,
                                                     uint32_t tag,
                                                     const void *payload,
                                                     uint32_t sequence,
                                                     uint32_t notify);

static const char module[] = "pb.terminal";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[] = "APP_PbTerminalTxEncodeOverlayFocus";
static const char message[] =
    "terminal overlay focus: magic=%d overlay=%d focused_index=%lu";
static const char short_message[] =
    "[pb.terminal]terminal overlay focus: magic=%d overlay=%d focused_index=%lu";

void audio_terminal_pb_overlay_focus_5cf134(uint32_t overlay,
                                              uint32_t focused_index) {
    uint8_t payload[8] = {0u};
    payload[0] = (uint8_t)overlay;
    payload[4] = (uint8_t)focused_index;
    payload[5] = (uint8_t)(focused_index >> 8);
    payload[6] = (uint8_t)(focused_index >> 16);
    payload[7] = (uint8_t)(focused_index >> 24);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x125u,
                           message, (uint32_t)audio_terminal_message_sequence + 1u,
                           (uint8_t)overlay, focused_index);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(
            0x0cc00000u, short_message, short_message,
            (uint32_t)audio_terminal_message_sequence + 1u,
            (uint8_t)overlay, focused_index);
    (void)audio_terminal_send_message_5ce7c4(
        0xaau, 0x19u, payload,
        (uint8_t)(audio_terminal_message_sequence + 1u), 1u);
}

void audio_terminal_status_publish_5e5498(uint32_t overlay,
                                            uint32_t focused_index) {
    audio_terminal_pb_overlay_focus_5cf134((uint8_t)overlay, focused_index);
}

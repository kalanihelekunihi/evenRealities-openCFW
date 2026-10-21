/* Native APP_PbTerminalTxEncodeDisplayStateNotify and its 0x5e5484 wrapper. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence; /* stock RAM 0x20074fff */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t, uint32_t,
                                                    const void *, uint32_t,
                                                    uint32_t);

static const char module[] = "pb.terminal";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[] = "APP_PbTerminalTxEncodeDisplayStateNotify";
static const char message[] =
    "terminal display state notify: magic=%d state=%d session=%lu overlay=%d";
static const char short_message[] =
    "[pb.terminal]terminal display state notify: magic=%d state=%d session=%lu overlay=%d";

void audio_terminal_pb_encode_display_state_5ceffa(uint32_t state,
                                                     uint32_t session,
                                                     uint32_t overlay) {
    uint8_t payload[12];
    audio_uart_buffer_zero(payload, sizeof payload, 0u);
    state = (uint8_t)state;
    if (state != 4u) {
        session = 0u;
        overlay = 0u;
    }
    payload[0] = (uint8_t)state;
    payload[4] = (uint8_t)session;
    payload[5] = (uint8_t)(session >> 8);
    payload[6] = (uint8_t)(session >> 16);
    payload[7] = (uint8_t)(session >> 24);
    payload[8] = (uint8_t)overlay;
    uint32_t sequence = (uint32_t)audio_terminal_message_sequence + 1u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x108u,
                           message, sequence, state, session, (uint8_t)overlay);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0xd000000u, short_message, short_message,
                                    sequence, state, session, (uint8_t)overlay);
    (void)audio_terminal_send_message_5ce7c4(0xa7u, 0x14u, payload,
                                               sequence & 0xffu, 1u);
}

void audio_terminal_ui_event_5e5484(uint32_t state, uint32_t session,
                                     uint32_t overlay) {
    audio_terminal_pb_encode_display_state_5ceffa((uint8_t)state, session,
                                                   (uint8_t)overlay);
}

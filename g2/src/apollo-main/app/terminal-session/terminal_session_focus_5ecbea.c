/* Stock Terminal session focus 0x5ecbea, UI wrapper 0x5e5490 and
 * protobuf ListFocus encoder 0x5cf0ba. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence; /* stock 0x20074fff */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t, uint32_t,
                                                    const void *, uint32_t,
                                                    uint32_t);

static const char module[] = "pb.terminal";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[] = "APP_PbTerminalTxEncodeListFocus";
static const char message[] =
    "terminal list focus: magic=%d focused_index=%lu";
static const char short_message[] =
    "[pb.terminal]terminal list focus: magic=%d focused_index=%lu";

__attribute__((noinline)) void audio_terminal_pb_list_focus_5cf0ba(uint32_t focused) {
    uint32_t payload;
    audio_uart_buffer_zero(&payload, 4u, 0u);
    payload = focused;
    const uint32_t sequence = (uint32_t)audio_terminal_message_sequence + 1u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x116u,
                           message, sequence, focused);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, short_message,
                                    short_message, sequence, focused);
    (void)audio_terminal_send_message_5ce7c4(0xa9u, 0x18u, &payload,
                                               sequence & 0xffu, 1u);
}

__attribute__((noinline)) void audio_terminal_list_focus_5e5490(uint32_t focused) {
    audio_terminal_pb_list_focus_5cf0ba(focused);
}

void audio_terminal_session_focus_5ecbea(int32_t index) {
    const int32_t selected = (int16_t)index;
    if (selected >= -1)
        audio_terminal_list_focus_5e5490(
            selected == -1 ? 0u : (uint32_t)(selected + 1));
}

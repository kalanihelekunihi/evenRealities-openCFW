/* Native APP_PbTerminalTxEncodeStatusReply at 0x5ceba2. */
#include <stdint.h>

uint8_t audio_terminal_message_sequence
    __attribute__((section(".g2.ram.terminal_message_sequence"),used)); /* native RAM 0x20074fff */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t, uint32_t,
                                                    const void *, uint32_t,
                                                    uint32_t);

static const char module[] = "pb.terminal";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[] = "APP_PbTerminalTxEncodeStatusReply";
static const char null_message[] = "terminal status reply is null";
static const char null_short[] = "[pb.terminal]terminal status reply is null";
static const char status_message[] = "terminal status reply: magic=%d current_mode=%d err_code=%d";
static const char status_short[] = "[pb.terminal]terminal status reply: magic=%d current_mode=%d err_code=%d";

uint32_t audio_terminal_send_status_reply(const void *reply) {
    if (reply == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x99u,
                               null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x4000000u, null_short, null_short);
        return 6u;
    }
    const uint8_t *bytes = (const uint8_t *)reply;
    uint32_t sequence = (uint32_t)audio_terminal_message_sequence + 1u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x9du,
                           status_message, sequence, bytes[0], bytes[1]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0xcc00000u, status_short, status_short,
                                    sequence, bytes[0], bytes[1]);
    return audio_terminal_send_message_5ce7c4(0xa1u, 9u, reply,
                                               sequence & 0xffu, 1u);
}

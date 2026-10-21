/* Native APP_PbTerminalTxEncodeVoiceInput at 0x5cec72. */
#include <stdint.h>

extern uint8_t audio_terminal_message_sequence; /* stock RAM 0x20074fff */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_terminal_send_message_5ce7c4(uint32_t, uint32_t,
                                                    const void *, uint32_t,
                                                    uint32_t);

static const char module[] = "pb.terminal";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_terminal\\pb_service_terminal.c";
static const char function[] = "APP_PbTerminalTxEncodeVoiceInput";
static const char null_message[] = "terminal voice input is null";
static const char null_short[] = "[pb.terminal]terminal voice input is null";
static const char voice_message[] = "terminal voice input: magic=%d cmd=%d";
static const char voice_short[] = "[pb.terminal]terminal voice input: magic=%d cmd=%d";

uint32_t audio_terminal_encode_voice_input_5cec72(const uint8_t *voice) {
    if (voice == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0xa9u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 6u;
    }
    uint32_t sequence = (uint32_t)audio_terminal_message_sequence + 1u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0xadu,
                           voice_message, sequence, voice[0]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c800000u, voice_short, voice_short,
                                    sequence, voice[0]);
    return audio_terminal_send_message_5ce7c4(0xa2u, 10u, voice,
                                               sequence & 0xffu, 1u);
}

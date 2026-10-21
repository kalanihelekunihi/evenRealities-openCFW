/* Native tracepoint_handle_delete_all 0x5ee7b4 and result constructor
 * 0x5ee10a. Reply buffer is live RAM 0x2037bbc8. */
#include <stdint.h>

extern uint8_t audio_tracepoint_reply_buffer[]; /* 0x2037bbc8, >=0x206 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_tracepoint_role_char_5edadc(void);
extern int32_t audio_tracepoint_delete_all_files_5ee650(void);
extern void audio_tracepoint_reply_result_5ee134(uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "tp.setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[] = "tracepoint_handle_delete_all";
static const char request[] = "tracepoint delete all request magic=%u role=%c";
static const char request_short[] = "[tp.setting]tracepoint delete all request magic=%u role=%c";
static const char result_message[] = "tracepoint delete all result=%d";
static const char result_short[] = "[tp.setting]tracepoint delete all result=%d";

void audio_tracepoint_make_result_message_5ee10a(uint8_t command,
                                                   uint8_t magic,
                                                   uint8_t failed)
{
    audio_uart_buffer_zero(audio_tracepoint_reply_buffer, 0x206u, 0u);
    audio_tracepoint_reply_buffer[0] = command;
    audio_tracepoint_reply_buffer[1] = magic;
    audio_tracepoint_reply_buffer[2] = 5u;
    audio_tracepoint_reply_buffer[3] = 0u;
    audio_tracepoint_reply_buffer[4] = failed;
}

void audio_tracepoint_delete_all_5ee7b4(uint8_t magic)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x19cu,
                           request, magic, audio_tracepoint_role_char_5edadc());
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, request_short,
                                    request_short, magic,
                                    audio_tracepoint_role_char_5edadc());
    int32_t result = audio_tracepoint_delete_all_files_5ee650();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x1a0u,
                           result_message, result);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c400000u, result_short,
                                    result_short, result);
    audio_tracepoint_make_result_message_5ee10a(3u, magic,
                                                  (uint8_t)(result < 0));
    audio_tracepoint_reply_result_5ee134(audio_tracepoint_reply_buffer);
}

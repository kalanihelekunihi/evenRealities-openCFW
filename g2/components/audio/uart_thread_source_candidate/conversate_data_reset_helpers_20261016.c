/* Native Conversate data clear/accessor leaves at 0x5b430e, 0x5b4364,
   0x5b43d4, 0x5b43e8, 0x5b473a and 0x5b4766. */
#include <stdint.h>

extern uint8_t audio_conversate_prep_note_ram_200d7630[];
extern uint8_t audio_conversate_reply_status_200d6b84[];
extern uint8_t audio_conversate_transcribe_output_200e2ae4[];
extern uint32_t audio_conversate_transcribe_length_2007439c;
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate.data";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_comm_data.c";
static const char function[] = "conversate_transcribe_data_deinit";
static const char message[] = "Transcribe data deinitialized successfully";
static const char short_message[] =
    "[conversate.data]Transcribe data deinitialized successfully";

void audio_conversate_transcribe_reset_5b430e(void) {
    audio_uart_buffer_zero(audio_conversate_prep_note_ram_200d7630 + 0x88u,
                           0x100au, 0u);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 219u, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, short_message, short_message);
}

void *audio_conversate_transcribe_get_5b4364(void) {
    return audio_conversate_transcribe_length_2007439c
        ? audio_conversate_transcribe_output_200e2ae4 : (void *)0;
}

void audio_conversate_reply_list_clear_5b43d4(void) {
    audio_uart_buffer_zero(audio_conversate_reply_status_200d6b84 + 4u,
                           0xaa8u, 0u);
}

void *audio_conversate_reply_list_get_5b43e8(void) {
    return audio_conversate_reply_status_200d6b84 + 4u;
}

void audio_conversate_prep_note_reset_5b473a(void) {
    uint8_t *const ram = audio_conversate_prep_note_ram_200d7630;
    audio_uart_buffer_zero(ram, 0x88u, 0u);
    audio_uart_buffer_zero(ram + 0x7e00u, 0x36b1u, 0u);
    audio_uart_buffer_zero(ram + 0x1094u, 0x6d6cu, 0u);
}

void *audio_conversate_prep_note_get_5b4766(void) {
    return audio_conversate_prep_note_ram_200d7630;
}

/* Native conversate_prep_note_line_layout_rebuild 0x5b4000..0x5b4163. */
#include <stdint.h>

extern uint8_t audio_conversate_prep_note_ram_200d7630[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern uint32_t audio_conversate_prep_note_measure_line_5b3f94(
    const void *, uint32_t, uint32_t);

static const char module[] = "conversate.data";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_comm_data.c";
static const char function[] = "conversate_prep_note_line_layout_rebuild";
static const char empty_message[] = "prep note line layout skipped, empty input";
static const char empty_short[] =
    "[conversate.data]prep note line layout skipped, empty input";
static const char layout_message[] =
    "prep note layout: raw_size=%u, consumed=%u, line_count=%u, measure_w=%d, truncated=%d";
static const char layout_short[] =
    "[conversate.data]prep note layout: raw_size=%u, consumed=%u, line_count=%u, measure_w=%d, truncated=%d";

static void set_half(uint8_t *p, uint16_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8);
}

void audio_conversate_prep_note_layout_parse_5b4000(const void *input,
                                                      uint32_t length) {
    uint8_t *const state = audio_conversate_prep_note_ram_200d7630 + 0x1094u;
    uint8_t *const offsets = state + 10u;
    audio_uart_buffer_zero(offsets, 28002u, 0u);
    set_half(state + 6u, 0u);
    uint16_t raw_size = (uint16_t)length;
    if (!input || raw_size == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 112u, empty_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, empty_short, empty_short);
        return;
    }
    uint32_t consumed = 0u;
    uint32_t count = 0u;
    const uint32_t width = 544u;
    const uint8_t *const text = input;
    while ((uint16_t)consumed < raw_size && (uint16_t)count < 14000u) {
        uint16_t remaining = (uint16_t)(length - consumed);
        uint32_t step = audio_conversate_prep_note_measure_line_5b3f94(
            text + (uint16_t)consumed, remaining, width);
        if ((uint16_t)step == 0u)
            break;
        set_half(offsets + 2u * (uint16_t)count, (uint16_t)consumed);
        count++;
        consumed += step;
    }
    uint32_t truncated = (uint16_t)consumed < raw_size ? 1u : 0u;
    set_half(offsets + 2u * (uint16_t)count, (uint16_t)consumed);
    set_half(state + 6u, (uint16_t)count);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 141u, layout_message,
                           raw_size, (uint16_t)consumed, (uint16_t)count,
                           width, truncated);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0d400000u, layout_short, layout_short,
                         raw_size, (uint16_t)consumed, (uint16_t)count,
                         width, truncated);
}

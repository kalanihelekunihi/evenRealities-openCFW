/* Native conversate_prep_note_packet_update 0x5b44d8..0x5b4739. */
#include <stdint.h>

extern uint8_t audio_conversate_prep_note_ram_200d7630[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void audio_conversate_prep_note_text_commit_5b4164(const void *, uint32_t);

static const char module[] = "conversate.data";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_comm_data.c";
static const char function[] = "conversate_prep_note_packet_update";
static const char null_message[] = "prep_note_packet is NULL";
static const char null_short[] = "[conversate.data]prep_note_packet is NULL";
static const char not_ready_message[] = "prep note packet ignored, metadata not ready";
static const char not_ready_short[] =
    "[conversate.data]prep note packet ignored, metadata not ready";
static const char order_message[] =
    "prep note packet order unexpected: recv=%u, expect=%u";
static const char order_short[] =
    "[conversate.data]prep note packet order unexpected: recv=%u, expect=%u";
static const char invalid_message[] = "prep note packet index invalid: %u/%u";
static const char invalid_short[] =
    "[conversate.data]prep note packet index invalid: %u/%u";
static const char update_message[] =
    "prep note packet update: packet=%u, text_size=%u, raw_len=%u, loaded=%u, total=%u, complete=%d";
static const char update_short[] =
    "[conversate.data]prep note packet update: packet=%u, text_size=%u, raw_len=%u, loaded=%u, total=%u, complete=%d";

static uint16_t half(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8));
}

static void set_half(uint8_t *p, uint16_t value) {
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8);
}

uint32_t audio_conversate_prep_note_packet_update_5b44d8(const void *input) {
    if (!input) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 288u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    uint8_t *const state = audio_conversate_prep_note_ram_200d7630 + 0x1094u;
    uint8_t *const text = audio_conversate_prep_note_ram_200d7630 + 0x7e00u;
    const uint8_t *const packet = input;
    uint16_t total = half(state);
    if (!total) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 293u, not_ready_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, not_ready_short, not_ready_short);
        return UINT32_MAX;
    }
    uint16_t index = half(packet);
    uint16_t loaded = half(state + 2u);
    if (index != loaded) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 301u,
                               order_message, index, loaded);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08800000u, order_short, order_short,
                             index, loaded);
        return UINT32_MAX;
    }
    if (index >= total) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 308u,
                               invalid_message, index, total);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08800000u, invalid_short, invalid_short,
                             index, total);
        return UINT32_MAX;
    }
    uint16_t copied = half(packet + 4u);
    if (copied > 14000u)
        copied = 14000u;
    uint16_t raw = half(state + 4u);
    uint16_t capacity = (uint16_t)(14000u - raw);
    if (copied > capacity)
        copied = capacity;
    if (copied) {
        (void)audio_queue_copy_bytes(text + raw, packet + 6u, copied);
        raw = (uint16_t)(raw + copied);
        set_half(state + 4u, raw);
        text[raw] = 0;
    }
    loaded = (uint16_t)(loaded + 1u);
    set_half(state + 2u, loaded);
    state[8] = (uint8_t)(loaded >= total);
    if (state[8])
        audio_conversate_prep_note_text_commit_5b4164(text, raw);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 340u, update_message,
                           index, copied, raw, loaded, total, (uint32_t)state[8]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0d800000u, update_short, update_short,
                         index, copied, raw, loaded, total, (uint32_t)state[8]);
    return 0;
}

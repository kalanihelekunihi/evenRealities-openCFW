/* Native conversate_action_tag_data 0x5b4f72..0x5b514f. */
#include <stdint.h>

extern uint32_t audio_conversate_store_tag_596360(const void *);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_tag_data";
static const char null_message[] = "conversate tag data is NULL";
static const char null_short[] = "[conversate]conversate tag data is NULL";
static const char received[] =
    "tag data received(type: %d, len: %d, extend_len: %d):[text:%s|extend:%s]";
static const char received_short[] =
    "[conversate]tag data received(type: %d, len: %d, extend_len: %d):[text:%s|extend:%s]";
static const char bad_type[] = "Invalid tag type: %d";
static const char bad_type_short[] = "[conversate]Invalid tag type: %d";
static const char bad_text[] = "Invalid tag text: %s, %s";
static const char bad_text_short[] = "[conversate]Invalid tag text: %s, %s";
static const char store_failed[] = "Failed to store tag data";
static const char store_failed_short[] = "[conversate]Failed to store tag data";

uint32_t audio_conversate_action_5b4f72(void *context, const void *arg1,
                                           void *arg2) {
    (void)context;
    (void)arg2;
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 261u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    const uint8_t *const packet = (const uint8_t *)arg1;
    const uint32_t type = packet[0];
    const uint16_t length = (uint16_t)((uint16_t)packet[2] | ((uint16_t)packet[3] << 8));
    const uint16_t extended_length =
        (uint16_t)((uint16_t)packet[0x84] | ((uint16_t)packet[0x85] << 8));
    const char *const text = (const char *)(packet + 4);
    const char *const extended = (const char *)(packet + 0x86);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 266u, received,
                           type, length, extended_length, text, extended);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0d400000u, received_short, received_short,
                         type, length, extended_length, text, extended);
    if (type == 0u || type >= 5u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 269u, bad_type, type);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, bad_type_short, bad_type_short, type);
        return UINT32_MAX;
    }
    if (length == 0u || extended_length == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 274u,
                               bad_text, text, extended);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04800000u, bad_text_short, bad_text_short,
                             text, extended);
        return UINT32_MAX;
    }
    if (audio_conversate_store_tag_596360(packet) == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 280u, store_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, store_failed_short, store_failed_short);
        return UINT32_MAX;
    }
    audio_conversate_report_5b02e4(5u, 0u);
    return 0u;
}

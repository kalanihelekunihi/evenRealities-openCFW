/* Native conversate_prep_note_list_data_update 0x5b4378..0x5b43d3. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

/* Four reply-status bytes precede the stock 2,728-byte list record. */
__attribute__((used, section(".g2_conversate_reply_list_200d6b84")))
uint8_t audio_conversate_reply_status_200d6b84[0xaac];

static const char module[] = "conversate.data";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_comm_data.c";
static const char function[] = "conversate_prep_note_list_data_update";
static const char null_message[] = "prep_note_list is NULL";
static const char null_short[] = "[conversate.data]prep_note_list is NULL";

void audio_conversate_prep_note_list_update_5b4378(const void *input) {
    if (!input) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 244u,
                               null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return;
    }
    (void)audio_queue_copy_bytes(audio_conversate_reply_status_200d6b84 + 4u,
                                 input, 2728u);
}

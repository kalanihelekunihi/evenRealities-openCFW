/* Apollo QuickList completed-UID batch sender, 0x4f6328..0x4f657d: the
 * completed list goes to the phone in batches of 20 as a quicklist pb items
 * message (kind 3, records marked completed), then the list is cleared.
 * Verified against stock on Renode 1.17 M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"


_Static_assert(sizeof(g2_quicklist_pb_items_t) == 0x1230u, "pb items frame");

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern uint32_t audio_quicklist_send_completed_5591b0(uint32_t, const g2_quicklist_pb_items_t *);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "quicklist_send_completed_uids";
static const char empty_message[] = "No completed UIDs to send";
static const char empty_compact[] = "[quicklist.page]No completed UIDs to send";
static const char start_message[] = "Sending %d completed UIDs in %d batches";
static const char start_compact[] = "[quicklist.page]Sending %d completed UIDs in %d batches";
static const char fail_message[] = "Failed to send completed UIDs batch %d, result: %d";
static const char fail_compact[] = "[quicklist.page]Failed to send completed UIDs batch %d, result: %d";
static const char done_message[] = "Successfully sent completed UIDs batch %d (%d items)";
static const char done_compact[] = "[quicklist.page]Successfully sent completed UIDs batch %d (%d items)";

uint32_t audio_quicklist_aux_update_4f6328(void) {
    g2_quicklist_uid_cache_t *const done = &g2_quicklist_completed_201303cc;
    if (done->count == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 1218u, empty_message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u, empty_compact, empty_compact);
        return 0u;
    }
    const int32_t batches = ((int32_t)done->count + (int32_t)QL_CACHE_RECORDS - 1) / (int32_t)QL_CACHE_RECORDS;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 1234u, start_message,
                           (uint32_t)done->count, batches);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10800000u, start_compact, start_compact,
                                    (uint32_t)done->count, batches);
    int32_t sent = 0;
    for (int32_t batch = 0; batch < batches; ++batch) {
        const int32_t remaining = (int32_t)done->count - sent;
        const int32_t items = remaining > (int32_t)QL_CACHE_RECORDS ? (int32_t)QL_CACHE_RECORDS : remaining;
        g2_quicklist_pb_items_t message;
        audio_uart_buffer_zero(&message, sizeof message, 0u);
        message.data_type = 3u;
        message.total_count = (uint8_t)done->count;
        message.items_count = (uint16_t)items;
        message.at_1228 = 0u;
        for (int32_t index = 0; index < items; ++index) {
            const g2_quicklist_uid_entry_t *const entry = &done->entries[sent + index];
            g2_quicklist_pb_item_t *const item = &message.item[index];
            item->uid = entry->uid;
            item->index = 0u;
            item->is_completed = 1u;
            item->timestamp[0] = entry->timestamp[0];
            item->timestamp[1] = entry->timestamp[1];
            item->title_size = 0u;
            item->at_e4 = 0u;
        }
        const uint32_t result = audio_quicklist_send_completed_5591b0(0u, &message);
        if (result != 0u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(1u, module, path, function, 1265u, fail_message,
                                   batch, result);
            if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x04800000u, fail_compact, fail_compact,
                                            batch, result);
            return UINT32_MAX;
        }
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 1269u, done_message,
                               batch, items);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10800000u, done_compact, done_compact,
                                        batch, items);
        sent += items;
    }
    audio_uart_buffer_zero(done, sizeof *done, 0u);
    return 0u;
}

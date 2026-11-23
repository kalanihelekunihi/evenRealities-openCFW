/* quicklist_data_add_mult_items, stock 0x58d668..0x58d9bf
 * (quicklist_data_manager.c, module "quicklist.data_mgr").
 *
 * Stock quirk kept: a converted item lands at record[received + i], but the
 * valid flag is set on record[i] (stock 0x58d8c4 indexes the flag with i
 * alone). Every item counts toward `received`, including skipped ones.
 * Verified against stock on Renode 1.17 M55 (spec ql-d). */
#include <stdint.h>

#include "../quicklist-common/quicklist_types.h"

extern uint32_t audio_quicklist_convert_pb(const g2_quicklist_pb_item_t *pb_item,
                                           g2_quicklist_record_t *record); /* 0x58da28 */
extern uint32_t audio_quicklist_tick_now(void);                          /* 0x44a1c6 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);          /* 0x43c0e4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.data_mgr";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\quicklist_data_manager.c";
static const char function[] = "quicklist_data_add_mult_items";

#define LOG_BOTH(level, line, flags, text)                                                    \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), module, path, function, (line), text);                \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compressed_log_output((flags), "[quicklist.data_mgr]" text,                 \
                                        "[quicklist.data_mgr]" text);                         \
    } while (0)

uint32_t audio_quicklist_store_many(const g2_quicklist_pb_items_t *pb_items) {
    if (pb_items == 0) {
        LOG_BOTH(1u, 73u, 0x04000000u, "pb_mult_items is NULL");
        return 2u;
    }
    g2_quicklist_cache_t *const cache = &audio_quicklist_item_cache;
    const uint32_t count = pb_items->items_count > QL_CACHE_RECORDS ? QL_CACHE_RECORDS
                                                                    : pb_items->items_count;
    if (pb_items->total_count == 0u) {
        LOG_BOTH(3u, 80u, 0x0c000000u, "No total count to add");
        audio_uart_buffer_zero(cache, sizeof *cache, 0u);
    } else if (pb_items->items_count == 0u) {
        LOG_BOTH(2u, 86u, 0x08000000u, "No items to add");
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 91u, "rcv items[0].index = %d",
                               pb_items->item[0].index);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10400000u,
                                        "[quicklist.data_mgr]rcv items[0].index = %d",
                                        "[quicklist.data_mgr]rcv items[0].index = %d",
                                        pb_items->item[0].index);
        if (pb_items->item[0].index == 0u)
            audio_uart_buffer_zero(cache, sizeof *cache, 0u);
        if (cache->received + (uint8_t)count > QL_CACHE_RECORDS) {
            LOG_BOTH(1u, 97u, 0x04000000u, "Valid count + items count > max items");
            return 4u;
        }
        for (uint32_t i = 0u; i < (uint8_t)count; ++i) {
            const g2_quicklist_pb_item_t *const item = &pb_items->item[i];
            if (item->index < QL_CACHE_RECORDS) {
                if ((uint8_t)audio_quicklist_convert_pb(item, &cache->record[i + cache->received]) == 0u) {
                    cache->record[i].valid = 1u;
                } else {
                    if ((audio_log_flags() & 2u) != 0u)
                        audio_log_extended(1u, module, path, function, 114u,
                                           "Failed to convert pb item to internal format for UID %d",
                                           item->uid);
                    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                        (void)compressed_log_output(0x04400000u,
                            "[quicklist.data_mgr]Failed to convert pb item to internal format for UID %d",
                            "[quicklist.data_mgr]Failed to convert pb item to internal format for UID %d",
                            item->uid);
                }
            } else {
                if ((audio_log_flags() & 2u) != 0u)
                    audio_log_extended(2u, module, path, function, 107u,
                                       "Invalid index %d, skipping item UID %d",
                                       item->index, item->uid);
                if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                    (void)compressed_log_output(0x08800000u,
                        "[quicklist.data_mgr]Invalid index %d, skipping item UID %d",
                        "[quicklist.data_mgr]Invalid index %d, skipping item UID %d",
                        item->index, item->uid);
            }
        }
    }
    cache->total = pb_items->total_count;
    cache->received = (uint8_t)(cache->received + count);
    cache->update_kind = pb_items->data_type;
    cache->update_tick[0] = audio_quicklist_tick_now();
    cache->update_tick[1] = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 128u,
                           "Processed %d items, total_count=%d, valid_count=%d",
                           pb_items->items_count, cache->total, cache->received);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0cc00000u,
            "[quicklist.data_mgr]Processed %d items, total_count=%d, valid_count=%d",
            "[quicklist.data_mgr]Processed %d items, total_count=%d, valid_count=%d",
            pb_items->items_count, cache->total, cache->received);
    return cache->received < cache->total ? 1u : 0u;
}

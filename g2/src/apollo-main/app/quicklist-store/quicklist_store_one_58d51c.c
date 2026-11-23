/* quicklist_data_add_item, stock 0x58d51c..0x58d667
 * (quicklist_data_manager.c, module "quicklist.data_mgr").
 *
 * The cache is the stock object at 0x20101a1c; its storage is
 * g2_stock_ram_20101a18+4 (system/stock-ram/stock_ram_cells.c).
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
static const char function[] = "quicklist_data_add_item";

uint32_t audio_quicklist_store_one(const g2_quicklist_pb_item_t *pb_item) {
    if (pb_item == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 41u, "pb_item is NULL");
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, "[quicklist.data_mgr]pb_item is NULL",
                                        "[quicklist.data_mgr]pb_item is NULL");
        return 2u;
    }
    g2_quicklist_cache_t *const cache = &audio_quicklist_item_cache;
    audio_uart_buffer_zero(cache, offsetof(g2_quicklist_cache_t, total), 0u);
    const uint8_t result = (uint8_t)audio_quicklist_convert_pb(pb_item, &cache->record[0]);
    if (result != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 51u,
                               "Failed to convert pb item to internal format");
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u,
                "[quicklist.data_mgr]Failed to convert pb item to internal format",
                "[quicklist.data_mgr]Failed to convert pb item to internal format");
        return result;
    }
    cache->record[0].valid = 1u;
    cache->total = 1u;
    cache->received = 1u;
    cache->update_kind = QL_UPDATE_MODIFY;
    cache->update_tick[0] = audio_quicklist_tick_now();
    cache->update_tick[1] = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 62u,
                           "Added single quicklist item: UID=%d, index=%d, title='%.20s'",
                           pb_item->uid, pb_item->index, (const char *)pb_item->title_bytes);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0cc00000u,
            "[quicklist.data_mgr]Added single quicklist item: UID=%d, index=%d, title='%.20s'",
            "[quicklist.data_mgr]Added single quicklist item: UID=%d, index=%d, title='%.20s'",
            pb_item->uid, pb_item->index, (const char *)pb_item->title_bytes);
    return 0u;
}

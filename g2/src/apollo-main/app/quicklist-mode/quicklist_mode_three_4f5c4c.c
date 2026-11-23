/* Apollo QuickList modify 0x4f5c4c..0x4f5e11. Known UIDs are updated in place;
 * unknown UIDs are inserted at the head (the shown count is not changed here;
 * 0x4f5596 applies it later). Stock counts every handled record in `inserted`
 * while fewer than 40 items were shown. Verified against stock on Renode 1.17
 * M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

extern void audio_quicklist_copy_record_4f55e0(const g2_quicklist_record_t *, g2_quicklist_item_t *);
extern int32_t audio_quicklist_find_record_4f5636(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "handle_modify";
static const char message[] = "Modify: total: %d";
static const char compact[] = "[quicklist.page]Modify: total: %d";

uint32_t audio_quicklist_mode_three_4f5c4c(uint32_t direction) {
    (void)direction;
    g2_quicklist_storage_t *const storage = &g2_quicklist_ui_data_2012a72c;
    const g2_quicklist_cache_t *const cache = &audio_quicklist_item_cache;
    g2_quicklist_flag_20075041 = QL_CHANGE_MODIFY;
    g2_quicklist_word_20074e28 = 0;
    if (cache->total == 0u)
        return 5u;
    const uint16_t shown = storage->count;
    uint16_t inserted = 0u, matched = 0u;
    int32_t missing = 0;
    if (shown == 0u) {
        for (uint16_t index = 0u; index < QL_CACHE_RECORDS && inserted < QL_UI_ITEMS; ++index)
            if (cache->record[index].valid != 0u)
                audio_quicklist_copy_record_4f55e0(&cache->record[index], &storage->item[inserted++]);
        g2_quicklist_flag_20075041 = QL_CHANGE_FULL;
        matched = inserted;
    } else {
        for (int32_t index = 0; index < (int32_t)QL_CACHE_RECORDS; ++index) {
            const g2_quicklist_record_t *const record = &cache->record[index];
            if (record->valid == 0u)
                continue;
            const int32_t slot = audio_quicklist_find_record_4f5636(record->uid);
            if (slot >= 0) {
                audio_quicklist_copy_record_4f55e0(record, &storage->item[slot]);
                ++matched;
            } else {
                g2_quicklist_flag_20075041 = QL_CHANGE_ADD_UP;
                ++missing;
                for (int32_t move = shown; move >= 1; --move)
                    if (shown < QL_UI_ITEMS)
                        storage->item[move] = storage->item[move - 1];
                audio_quicklist_copy_record_4f55e0(record, &storage->item[0]);
            }
            if (shown < QL_UI_ITEMS)
                ++inserted;
        }
    }
    if (g2_quicklist_flag_20075041 == QL_CHANGE_MODIFY || g2_quicklist_flag_20075041 == QL_CHANGE_FULL)
        g2_quicklist_word_20074e28 = matched;
    else if (g2_quicklist_flag_20075041 == QL_CHANGE_ADD_UP)
        g2_quicklist_word_20074e28 = missing;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 983u, message, (uint32_t)inserted);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, compact, compact, (uint32_t)inserted);
    return 0u;
}

/* Apollo QuickList cache selection 0x4f5662..0x4f570d: copy the valid cache
 * records whose update kind matches `kind` and whose UID is not already shown.
 * Stock scans the shown items from index 0 and compares *selected < capacity
 * signed. Verified against stock on Renode 1.17 M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

extern void audio_uart_checksum_copy(void *, const void *, uint32_t); /* word memcpy, 0x439c04 */

static int quicklist_uid_shown(uint32_t uid) {
    const g2_quicklist_storage_t *const storage = &g2_quicklist_ui_data_2012a72c;
    for (int32_t index = 0; index < (int32_t)storage->count; ++index)
        if (storage->item[index].uid == uid)
            return 1;
    return 0;
}

uint32_t audio_quicklist_select_records_4f5662(g2_quicklist_record_t *output, int32_t capacity,
                                               int32_t *selected, uint32_t kind) {
    if (selected == 0)
        return 2u;
    g2_quicklist_cache_t *const cache = &audio_quicklist_item_cache;
    g2_quicklist_record_t *const destination = output != 0 ? output : g2_stock_ram_20367bd8;
    *selected = 0;
    for (int32_t index = 0; index < (int32_t)QL_CACHE_RECORDS && *selected < capacity; ++index) {
        const g2_quicklist_record_t *const record = &cache->record[index];
        if (record->valid == 0u || cache->update_kind != (uint8_t)kind)
            continue;
        if (!quicklist_uid_shown(record->uid)) {
            audio_uart_checksum_copy(&destination[*selected], record, sizeof *record);
            ++*selected;
        }
    }
    return 0u;
}

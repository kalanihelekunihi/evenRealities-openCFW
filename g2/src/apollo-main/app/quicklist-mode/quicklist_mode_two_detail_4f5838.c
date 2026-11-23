/* Apollo QuickList add-down 0x4f5838..0x4f5a1b: new cache records are appended
 * after the shown items; items pushed past 40 at the head are retired. The log
 * reports the unchanged storage count. Verified against stock on Renode 1.17
 * M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* memset, 0x43c0e4 */
extern uint32_t audio_quicklist_select_records_4f5662(g2_quicklist_record_t *, int32_t, int32_t *, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* memcpy, 0x439be4 */
extern void audio_quicklist_copy_record_4f55e0(const g2_quicklist_record_t *, g2_quicklist_item_t *);
extern uint32_t audio_quicklist_aux_update_4f6328(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "handle_add_down";
static const char message[] = "Add down: %d items, total: %d";
static const char compact[] = "[quicklist.page]Add down: %d items, total: %d";

uint32_t audio_quicklist_mode_two_detail_4f5838(uint32_t direction) {
    (void)direction;
    g2_quicklist_storage_t *const storage = &g2_quicklist_ui_data_2012a72c;
    g2_quicklist_record_t *const incoming = g2_stock_ram_20367bd8;
    uint8_t *const scratch = g2_quicklist_shift_scratch_2012d57c + 8u;
    audio_uart_buffer_zero(incoming, sizeof g2_stock_ram_20367bd8, 0u);
    int32_t selected = 0;
    uint16_t kept = storage->count;
    const uint32_t status = audio_quicklist_select_records_4f5662(incoming, (int32_t)QL_CACHE_RECORDS, &selected, QL_UPDATE_ADD);
    if ((uint8_t)status != 0u)
        return (uint8_t)status;
    if (selected >= 1) {
        if (selected + kept > (int32_t)QL_UI_ITEMS) {
            const int32_t dropped = selected + kept - (int32_t)QL_UI_ITEMS;
            for (int32_t index = 0; index < dropped; ++index)
                quicklist_retire_uid(storage->item[index].uid);
            if (g2_quicklist_completed_201303cc.count != 0u)
                (void)audio_quicklist_aux_update_4f6328();
            kept = (uint16_t)(kept - dropped);
            (void)audio_queue_copy_bytes(scratch, &storage->item[dropped], kept * sizeof storage->item[0]);
            (void)audio_queue_copy_bytes(storage->item, scratch, kept * sizeof storage->item[0]);
        }
        for (int32_t index = 0; index < selected; ++index)
            audio_quicklist_copy_record_4f55e0(&incoming[index], &storage->item[kept + index]);
    }
    g2_quicklist_flag_20075041 = QL_CHANGE_ADD_DOWN;
    g2_quicklist_word_20074e28 = selected;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 773u, message, selected, (uint32_t)storage->count);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10800000u, compact, compact, selected, (uint32_t)storage->count);
    return 0u;
}

/* Apollo QuickList full update 0x4f5718..0x4f5833: rebuild the UI items from
 * the valid cache records. Verified against stock on Renode 1.17 M55
 * (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

extern int32_t g2_quicklist_page_active_20074e1c;     /* RAM 0x20074e1c */
extern void *g2_quicklist_event_fifo_20074e14;        /* RAM 0x20074e14 */
extern void *g2_dashboard_ext_container_20074b9c;     /* RAM 0x20074b9c */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* memset, 0x43c0e4 */
extern void audio_quicklist_copy_record_4f55e0(const g2_quicklist_record_t *, g2_quicklist_item_t *);
extern uint32_t audio_quicklist_aux_update_4f6328(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "handle_full_update";
static const char message[] = "Full update: %d items";
static const char compact[] = "[quicklist.page]Full update: %d items";

uint32_t audio_quicklist_mode_one_4f5718(uint32_t direction) {
    (void)direction;
    g2_quicklist_storage_t *const storage = &g2_quicklist_ui_data_2012a72c;
    const g2_quicklist_cache_t *const cache = &audio_quicklist_item_cache;
    audio_uart_buffer_zero(storage->item, sizeof storage->item, 0u);
    uint16_t count = 0u;
    if (cache->total != 0u)
        for (uint16_t index = 0u; index < QL_CACHE_RECORDS && count < QL_UI_ITEMS; ++index)
            if (cache->record[index].valid != 0u)
                audio_quicklist_copy_record_4f55e0(&cache->record[index], &storage->item[count++]);
    g2_quicklist_flag_20075041 = QL_CHANGE_FULL;
    g2_quicklist_word_20074e28 = count;
    if (g2_quicklist_temp_cache_20130654.count != 0u && g2_quicklist_page_active_20074e1c == 1 &&
        g2_quicklist_event_fifo_20074e14 != 0 && g2_dashboard_ext_container_20074b9c != 0)
        audio_uart_buffer_zero(&g2_quicklist_temp_cache_20130654, sizeof g2_quicklist_temp_cache_20130654, 0u);
    if (g2_quicklist_completed_201303cc.count != 0u)
        (void)audio_quicklist_aux_update_4f6328();
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 681u, message, (uint32_t)count);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, compact, compact, (uint32_t)count);
    return 0u;
}

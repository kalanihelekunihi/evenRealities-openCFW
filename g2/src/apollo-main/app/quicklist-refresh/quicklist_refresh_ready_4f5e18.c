/* Apollo QuickList storage-to-UI dispatch 0x4f5e18..0x4f5e7b (quicklist cache
 * update kind: 1 full, 2 add up/down by add_direction, 3 modify).
 * Verified against stock on Renode 1.17 M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

extern uint32_t audio_quicklist_mode_one_4f5718(uint32_t);
extern uint32_t audio_quicklist_mode_two_4f5a1c(uint32_t);
extern uint32_t audio_quicklist_mode_two_detail_4f5838(uint32_t);
extern uint32_t audio_quicklist_mode_three_4f5c4c(uint32_t);

uint8_t audio_quicklist_refresh_ready_4f5e18(void) {
    g2_quicklist_storage_t *const storage = &g2_quicklist_ui_data_2012a72c;
    const uint8_t kind = audio_quicklist_item_cache.update_kind;
    const uint8_t direction = storage->add_direction;
    uint32_t result;
    switch (kind) {
    case QL_UPDATE_FULL:
        result = audio_quicklist_mode_one_4f5718(direction);
        break;
    case QL_UPDATE_ADD:
        result = direction == 2u ? audio_quicklist_mode_two_detail_4f5838(direction)
                                 : audio_quicklist_mode_two_4f5a1c(direction);
        break;
    case QL_UPDATE_MODIFY:
        result = audio_quicklist_mode_three_4f5c4c(kind);
        break;
    default:
        result = 3u;
        break;
    }
    storage->last_update_kind = kind;
    return (uint8_t)result;
}

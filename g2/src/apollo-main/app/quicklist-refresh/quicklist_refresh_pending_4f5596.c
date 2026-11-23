/* Apollo QuickList pending-count update at 0x4f5596..0x4f55df.
 * Verified against stock on Renode 1.17 M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

void audio_quicklist_refresh_pending_4f5596(void) {
    g2_quicklist_storage_t *const storage = &g2_quicklist_ui_data_2012a72c;
    switch (storage->reflash_kind) {
    case 1u:
        storage->count = storage->reflash_value;
        break;
    case 2u:
    case 3u: {
        const uint32_t sum = (uint32_t)storage->count + storage->reflash_value;
        storage->count = (uint16_t)(sum > QL_UI_ITEMS ? QL_UI_ITEMS : sum);
        break;
    }
    default:
        break;
    }
}

/* Apollo QuickList UI item lookup by UID at 0x4f5636..0x4f5661.
 * Verified against stock on Renode 1.17 M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

int32_t audio_quicklist_find_record_4f5636(uint32_t uid) {
    const g2_quicklist_storage_t *const storage = &g2_quicklist_ui_data_2012a72c;
    for (int32_t index = 0; index < (int32_t)storage->count; ++index)
        if (storage->item[index].uid == uid)
            return index;
    return -1;
}

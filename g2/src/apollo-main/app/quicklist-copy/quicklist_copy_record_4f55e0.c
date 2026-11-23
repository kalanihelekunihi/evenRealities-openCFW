/* Apollo QuickList record conversion 0x4f55e0..0x4f5635: cache record -> UI item.
 * Verified against stock on Renode 1.17 M55 (build/ws-app-20261122/specs). */
#include "../quicklist-common/quicklist_types.h"

extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* memcpy, 0x439be4 */

void audio_quicklist_copy_record_4f55e0(const g2_quicklist_record_t *source,
                                        g2_quicklist_item_t *destination) {
    if (source == 0 || destination == 0)
        return;
    destination->uid = source->uid;
    destination->field_110 = source->field_04;
    destination->completed = source->completed;
    destination->timestamp[0] = source->timestamp[0];
    destination->timestamp[1] = source->timestamp[1];
    destination->time_kind = source->time_kind;
    const uint16_t length = source->title_len > QL_TITLE_MAX ? (uint16_t)QL_TITLE_MAX : source->title_len;
    (void)audio_queue_copy_bytes(destination->title, source->title, length);
    destination->title[length] = '\0';
}

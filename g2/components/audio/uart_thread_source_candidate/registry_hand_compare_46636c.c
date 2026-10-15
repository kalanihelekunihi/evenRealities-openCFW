/* Stock Apollo 0x46636c: compare a ring hand record with the saved context. */
#include <stdint.h>

extern const volatile uint8_t *const audio_uart_hand_context; /* 0x4667ec */
extern int32_t g2_lfs_memcmp(const void *, const void *, uint32_t); /* 0x4751c8 */

static uint32_t same_le16(const uint8_t *record, uint32_t record_at,
                          const volatile uint8_t *saved, uint32_t saved_at) {
    return record[record_at] == saved[saved_at] &&
           record[record_at + 1u] == saved[saved_at + 1u];
}

static uint32_t same_le32(const uint8_t *record, uint32_t record_at,
                          const volatile uint8_t *saved, uint32_t saved_at) {
    for(uint32_t i = 0; i < 4u; ++i)
        if(record[record_at + i] != saved[saved_at + i]) return 0u;
    return 1u;
}

uint32_t audio_uart_registry_hand_compare_46636c(const uint8_t *record) {
    const volatile uint8_t *saved = audio_uart_hand_context;
    if(!same_le16(record, 20u, saved, 18u) ||
       record[3] != saved[1] || record[4] != saved[2] ||
       record[5] != saved[3] || record[6] != saved[4] ||
       record[13] != saved[11]) return 0u;
    if(g2_lfs_memcmp(record + 7u, (const void *)(saved + 5u), 3u) != 0 ||
       g2_lfs_memcmp(record + 10u, (const void *)(saved + 8u), 3u) != 0 ||
       g2_lfs_memcmp(record + 14u, (const void *)(saved + 12u), 6u) != 0)
        return 0u;
    return same_le16(record, 32u, saved, 28u) &&
           same_le32(record, 28u, saved, 24u) &&
           same_le16(record, 44u, saved, 40u) &&
           same_le32(record, 40u, saved, 36u);
}

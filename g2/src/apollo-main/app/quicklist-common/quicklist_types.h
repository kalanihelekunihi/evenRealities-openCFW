/* QuickList storage layouts shared by the app/quicklist-* units.
 *
 * Evidence (stock 2.2.6.10):
 *  - cache record, 0xe8 B: copy 0x4f55e0 (uid +0, +4, completed +8, timestamp
 *    ldrd +0x10, time_kind +0x18, title +0x19, title length +0xe2 clamped to
 *    200), valid flag +0xe4 (0x4f5662/0x4f5718 tests, 0x58d51c store).
 *  - cache, stock 0x20101a1c: 20 records (0x4f5662 i < 0x14, memcpy 0xe8),
 *    +0x1220 total (0x58d668 store of pb byte 1; 0x4f5718/0x4f5c4c test != 0),
 *    +0x1221 received (0x58d668 accumulates the item count), +0x1222 update
 *    kind (0x58d668 pb byte 0, 0x58d51c stores 3, 0x4f5e18 dispatch 1/2/3),
 *    +0x1228 64-bit update tick (0x58d51c/0x58d668 store {0x44a1c6(), 0}).
 *  - pb item 0xe8 B / pb items frame: field names from the 0x558cb0 and
 *    0x58d51c log text (uid, index, isCompleted, title.size, title bytes +0x1a,
 *    timestamp, ts_type +0xe5); frame data_type +0, total_count +1,
 *    items_count +2, items +8 (0x558f34 log, 0x58d668 reads).
 *  - UI item 0x128 B / UI storage: ui/a-36-quicklist-page names (uid +0x10c,
 *    timestamp +0x118 consumed by quicklist_format_timestamp_4f5366, time_kind
 *    +0x120, completed +0x121); +0x2e48/+0x2e4e reflash pair (0x4f5596);
 *    +0x2e4c/+0x2e4d last update kind / add direction (0x4f5e18).
 *  - UID list 16 B entries, count at +0x280: 0x4f6328 reads uid +0 and the
 *    timestamp words +8/+12; 0x4f5a1c moves them between the two lists.
 * The objects keep their stock-address names; only their layout is typed here. */
#ifndef APP_QUICKLIST_TYPES_H
#define APP_QUICKLIST_TYPES_H
#include <stddef.h>
#include <stdint.h>

#define QL_CACHE_RECORDS 20u
#define QL_UI_ITEMS 40u
#define QL_TITLE_MAX 200u
#define QL_UPDATE_FULL 1u
#define QL_UPDATE_ADD 2u
#define QL_UPDATE_MODIFY 3u
/* g2_quicklist_flag_20075041: last UI change, sent to the peer by 0x4f5e84. */
#define QL_CHANGE_FULL 1u
#define QL_CHANGE_ADD_UP 2u
#define QL_CHANGE_ADD_DOWN 3u
#define QL_CHANGE_MODIFY 4u

typedef struct {
    uint32_t uid;            /* +0x00 */
    uint32_t field_04;       /* +0x04 -> item.field_110 */
    uint8_t completed;       /* +0x08 */
    uint8_t reserved_09[7];
    uint32_t timestamp[2];   /* +0x10 int64 seconds, lo/hi */
    uint8_t time_kind;       /* +0x18 */
    char title[0xc9];        /* +0x19 */
    uint16_t title_len;      /* +0xe2 */
    uint8_t valid;           /* +0xe4 */
    uint8_t reserved_e5[3];
} g2_quicklist_record_t;
_Static_assert(offsetof(g2_quicklist_record_t, timestamp) == 0x10u, "record timestamp");
_Static_assert(offsetof(g2_quicklist_record_t, title) == 0x19u, "record title");
_Static_assert(offsetof(g2_quicklist_record_t, title_len) == 0xe2u, "record title length");
_Static_assert(offsetof(g2_quicklist_record_t, valid) == 0xe4u, "record valid");
_Static_assert(sizeof(g2_quicklist_record_t) == 0xe8u, "record size");

typedef struct {
    g2_quicklist_record_t record[QL_CACHE_RECORDS]; /* +0x0000 */
    uint8_t total;                                  /* +0x1220 */
    uint8_t received;                               /* +0x1221 */
    uint8_t update_kind;                            /* +0x1222 */
    uint8_t reserved_1223[5];
    uint32_t update_tick[2];                        /* +0x1228 int64: {tick 0x44a1c6, 0} */
    uint8_t reserved_1230[8];
} g2_quicklist_cache_t;
_Static_assert(offsetof(g2_quicklist_cache_t, update_kind) == 0x1222u, "cache update kind");
_Static_assert(offsetof(g2_quicklist_cache_t, update_tick) == 0x1228u, "cache update tick");
_Static_assert(sizeof(g2_quicklist_cache_t) == 0x1238u, "cache extent (0x58d668 clears 0x1238)");

typedef struct {
    char title[0xc9];          /* +0x000 */
    char time_text[0x40];      /* +0x0c9 */
    uint8_t reserved_109[3];
    uint32_t uid;              /* +0x10c */
    uint32_t field_110;        /* +0x110 */
    uint32_t reserved_114;
    uint32_t timestamp[2];     /* +0x118 int64 seconds, lo/hi */
    uint8_t time_kind;         /* +0x120 */
    uint8_t completed;         /* +0x121 */
    uint8_t reserved_122[6];
} g2_quicklist_item_t;
_Static_assert(offsetof(g2_quicklist_item_t, uid) == 0x10cu, "item uid");
_Static_assert(offsetof(g2_quicklist_item_t, timestamp) == 0x118u, "item timestamp");
_Static_assert(offsetof(g2_quicklist_item_t, completed) == 0x121u, "item completed");
_Static_assert(sizeof(g2_quicklist_item_t) == 0x128u, "item size");

typedef struct {
    uint16_t count;                       /* +0x0000 */
    uint8_t reserved_2[6];
    g2_quicklist_item_t item[QL_UI_ITEMS]; /* +0x0008 */
    uint16_t reflash_value;               /* +0x2e48 */
    uint8_t reserved_2e4a[2];
    uint8_t last_update_kind;             /* +0x2e4c */
    uint8_t add_direction;                /* +0x2e4d: 1 up (0x4f5a1c), 2 down (0x4f5838) */
    uint8_t reflash_kind;                 /* +0x2e4e */
    uint8_t reserved_2e4f;
} g2_quicklist_storage_t;
_Static_assert(offsetof(g2_quicklist_storage_t, reflash_value) == 0x2e48u, "storage reflash");
_Static_assert(offsetof(g2_quicklist_storage_t, reflash_kind) == 0x2e4eu, "storage reflash kind");
_Static_assert(sizeof(g2_quicklist_storage_t) == 0x2e50u, "storage size");

typedef struct {
    uint32_t uid;            /* +0x0 */
    uint32_t reserved_4;
    uint32_t timestamp[2];   /* +0x8 */
} g2_quicklist_uid_entry_t;

typedef struct {
    g2_quicklist_uid_entry_t entries[QL_UI_ITEMS]; /* +0x000 */
    uint16_t count;                              /* +0x280 */
    uint8_t reserved_282[6];
} g2_quicklist_uid_cache_t;
_Static_assert(offsetof(g2_quicklist_uid_cache_t, count) == 0x280u, "uid cache count");
_Static_assert(sizeof(g2_quicklist_uid_cache_t) == 0x288u, "uid cache size (0x4f6328 clear)");

/* Objects (stock addresses in the names; storage is defined elsewhere). */
/* pb QuickList item (0xe8 B). Field names from the PB_RxQuicklistItem log at
 * 0x558cb0 ("uid, index, isCompleted, title.size, timestamp, ts_type"). */
typedef struct {
    uint32_t uid;            /* +0x00 */
    uint32_t index;          /* +0x04 (0x58d668 accepts < 20) */
    uint32_t is_completed;   /* +0x08 */
    uint32_t reserved_0c;
    uint32_t timestamp[2];   /* +0x10 int64 */
    uint16_t title_size;     /* +0x18 */
    uint8_t title_bytes[0xca];
    uint8_t at_e4;           /* +0xe4 */
    uint8_t ts_type;         /* +0xe5 */
    uint8_t reserved_e6[2];
} g2_quicklist_pb_item_t;
_Static_assert(offsetof(g2_quicklist_pb_item_t, title_size) == 0x18u, "pb item title size");
_Static_assert(offsetof(g2_quicklist_pb_item_t, ts_type) == 0xe5u, "pb item ts_type");
_Static_assert(sizeof(g2_quicklist_pb_item_t) == 0xe8u, "pb item size");

/* pb items message as handed to 0x5591b0 (the frame 0x58d668 reads: data_type
 * +0, total_count +1, items_count +2, items +8). */
typedef struct {
    uint8_t data_type;
    uint8_t total_count;
    uint16_t items_count;
    uint8_t reserved_4[4];
    g2_quicklist_pb_item_t item[QL_CACHE_RECORDS]; /* +0x0008 */
    uint8_t at_1228;
    uint8_t reserved_1229[7];
} g2_quicklist_pb_items_t;

extern g2_quicklist_cache_t audio_quicklist_item_cache;                     /* stock 0x20101a1c */
extern g2_quicklist_storage_t g2_quicklist_ui_data_2012a72c;              /* stock 0x2012a72c */
extern g2_quicklist_record_t g2_stock_ram_20367bd8[QL_CACHE_RECORDS];     /* stock 0x20367bd8 incoming */
extern uint8_t g2_quicklist_shift_scratch_2012d57c[];                     /* stock 0x2012d57c, +8 used */
extern g2_quicklist_uid_cache_t g2_quicklist_temp_cache_20130654;          /* stock 0x20130654 */
extern g2_quicklist_uid_cache_t g2_quicklist_completed_201303cc;           /* stock 0x201303cc */
extern uint8_t g2_quicklist_flag_20075041;                                /* last UI update kind */
extern int32_t g2_quicklist_word_20074e28;                                /* last UI update count */
/* Move `uid` from the pending UID cache to the completed list (inlined twice in
 * stock: 0x4f5838 and 0x4f5a1c). The completed entry gets uid and timestamp
 * only; when the completed list is full the pending entry is kept. */
static inline void quicklist_retire_uid(uint32_t uid) {
    g2_quicklist_uid_cache_t *const pending = &g2_quicklist_temp_cache_20130654;
    g2_quicklist_uid_cache_t *const done = &g2_quicklist_completed_201303cc;
    for (int32_t position = 0; position < (int32_t)pending->count; ++position) {
        if (pending->entries[position].uid != uid)
            continue;
        if (done->count < QL_UI_ITEMS) {
            g2_quicklist_uid_entry_t *const out = &done->entries[done->count];
            out->uid = uid;
            out->timestamp[0] = pending->entries[position].timestamp[0];
            out->timestamp[1] = pending->entries[position].timestamp[1];
            done->count = (uint16_t)(done->count + 1u);
            for (int32_t cursor = position; cursor < (int32_t)pending->count - 1; ++cursor)
                pending->entries[cursor] = pending->entries[cursor + 1];
            pending->count = (uint16_t)(pending->count - 1u);
        }
        return;
    }
}
#endif

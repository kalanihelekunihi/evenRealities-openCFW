/* QuickList page data requests, completed-UID temp cache and input forwarding,
 * stock D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c.
 * Native 0x4f5fd0..0x4f62ef, 0x4f658c..0x4f6863 and 0x4f6880..0x4f69d7; literal
 * pools 0x4f6310..0x4f6314, 0x4f6760, 0x4f69d8..0x4f6a0c, 0x4f6d1c..0x4f6d80,
 * 0x4f6e58..0x4f6e68, 0x4f6f98..0x4f6fc0 and 0x4f7160.
 *
 * Paging: the app keeps at most 20 rows on the glasses; when the focus comes
 * within five rows of either end, an UP (top UID) or DOWN (bottom UID) data
 * request is sent through the QuickList protobuf service, at most once per
 * 500 ms. Rows ticked on the glasses are first held in a temp cache and merged
 * into the completed cache that quicklist_send_completed_uids (0x4f6328) sends.
 * On a slave-side page, raw input codes are forwarded to the master as 6-byte
 * {0, code, x lo, x hi, y lo, y hi} display-refresh frames on channel 1. */
#include "ui_quicklist_page_private.h"

/* Payload of APP_PbNotifyEncodeQuicklistEvent. */
typedef struct {
    uint8_t event_type;    /* +0x0 QL_REQUEST_UP / QL_REQUEST_DOWN */
    uint8_t reserved_1[3];
    uint32_t uid;          /* +0x4 boundary row UID */
    uint8_t flag;          /* +0x8 always 0 */
    uint8_t reserved_9[3];
} g2_quicklist_request_event_t;
_Static_assert(sizeof(g2_quicklist_request_event_t) == 12u, "quicklist request event");

/* lv_event_t head (LVGL 9.3): param pointer at +0x10. */
typedef struct {
    void *current_target;  /* +0x00 */
    void *original_target; /* +0x04 */
    uint32_t code;         /* +0x08 */
    void *user_data;       /* +0x0c */
    void *param;           /* +0x10 */
} g2_lv_event_head_t;

extern uint32_t audio_quicklist_refresh_lock_4ffac8(void);   /* quicklist_lock_storage */
extern void audio_quicklist_refresh_unlock_4ffb26(void);     /* quicklist_unlock_storage */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern uint32_t osKernelGetTickCount(void);                  /* 0x4490cc */
extern int32_t APP_PbNotifyEncodeQuicklistEvent(uint32_t unused, const g2_quicklist_request_event_t *event); /* 0x55960c */
extern int32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                 uint32_t flags); /* 0x464bb2 */

static const char module_tag[] = "quicklist.page"; /* ROM 0x789e40 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c"; /* ROM 0x6f7538 */

static const char fn_send_request[] = "quicklist_send_data_request_event"; /* ROM 0x75c984 */
static const char no_data[] = "No quicklist data available, cannot send data request event"; /* ROM 0x71acc8 */
static const char no_data_short[] =
    "[quicklist.page]No quicklist data available, cannot send data request event"; /* ROM 0x6f7584 */
static const char send_up[] = "Sending UP data request event with top UID: %u"; /* ROM 0x73ac34 */
static const char send_up_short[] = "[quicklist.page]Sending UP data request event with top UID: %u"; /* ROM 0x7112e4 */
static const char send_down[] = "Sending DOWN data request event with bottom UID: %u"; /* ROM 0x730238 */
static const char send_down_short[] =
    "[quicklist.page]Sending DOWN data request event with bottom UID: %u"; /* ROM 0x707e44 */
static const char bad_type[] = "Invalid event type: %d"; /* ROM 0x77d4bc */
static const char bad_type_short[] = "[quicklist.page]Invalid event type: %d"; /* ROM 0x750c5c */
static const char send_failed[] = "Failed to send quicklist data request event, result: %d"; /* ROM 0x7258b0 */
static const char send_failed_short[] =
    "[quicklist.page]Failed to send quicklist data request event, result: %d"; /* ROM 0x6fedbc */
static const char fn_can_send[] = "quicklist_can_send_data_request"; /* ROM 0x767930 */
static const char too_frequent[] = "Request too frequent, time_diff=%llu ms, required=%d ms"; /* ROM 0x7258e8 */
static const char too_frequent_short[] =
    "[quicklist.page]Request too frequent, time_diff=%llu ms, required=%d ms"; /* ROM 0x6fee04 */
static const char fn_debounce[] = "quicklist_request_data_with_debounce"; /* ROM 0x750c84 */
static const char debounce[] = "Requesting data with debounce: event_type=%d"; /* ROM 0x73ac64 */
static const char debounce_short[] = "[quicklist.page]Requesting data with debounce: event_type=%d"; /* ROM 0x711324 */
static const char fn_add_temp[] = "quicklist_add_completed_uid_to_temp_cache"; /* ROM 0x746278 */
static const char temp_full[] = "Temp cache completed UIDs storage is full, cannot add UID: %u"; /* ROM 0x711364 */
static const char temp_full_short[] =
    "[quicklist.page]Temp cache completed UIDs storage is full, cannot add UID: %u"; /* ROM 0x6f0bc8 */
static const char temp_added[] = "Added UID %u to temp cache, count: %d"; /* ROM 0x750cd4 */
static const char temp_added_short[] = "[quicklist.page]Added UID %u to temp cache, count: %d"; /* ROM 0x725990 */
static const char fn_remove_temp[] = "quicklist_remove_completed_uid_from_temp_cache"; /* ROM 0x73ac94 */
static const char temp_removed[] = "Removed UID %u from temp cache, count: %d"; /* ROM 0x7462a4 */
static const char temp_removed_short[] =
    "[quicklist.page]Removed UID %u from temp cache, count: %d"; /* ROM 0x71ad04 */
static const char temp_missing[] = "UID %u not found in temp cache"; /* ROM 0x767970 */
static const char temp_missing_short[] = "[quicklist.page]UID %u not found in temp cache"; /* ROM 0x73acc4 */
static const char fn_merge[] = "quicklist_merge_temp_cache_to_completed_items"; /* ROM 0x73acf4 */
static const char merged[] = "Merged %d items from temp cache to completed items, total: %d"; /* ROM 0x7113a4 */
static const char merged_short[] =
    "[quicklist.page]Merged %d items from temp cache to completed items, total: %d"; /* ROM 0x6f0c18 */
static const char fn_input[] = "QuicklistInputEventHandler"; /* ROM 0x77426c */
static const char animating[] = "Animation in progress (scroll:%d), return"; /* ROM 0x7462d0 */
static const char animating_short[] = "[quicklist.page]Animation in progress (scroll:%d), return"; /* ROM 0x71ad40 */

#define QL_REQUEST_DEBOUNCE_MS 500u
#define QL_REQUEST_EDGE_ROWS 5
#define QL_REQUEST_MIN_ROWS 20u

void quicklist_send_data_request_event_4f5fd0(uint8_t event_type)
{
    g2_quicklist_ui_data_t *const ui = &g2_quicklist_ui_data_2012a72c;
    g2_quicklist_request_event_t event;
    int32_t result;

    if (ui->count == 0u) {
        QL_LOG(2u, fn_send_request, 1106u, 0x08000000u, no_data, no_data_short);
        return;
    }
    (void)audio_quicklist_refresh_lock_4ffac8();
    ui->last_request_event = event_type;
    audio_quicklist_refresh_unlock_4ffb26();

    audio_uart_buffer_zero(&event, sizeof event, 0u);
    event.event_type = event_type;
    event.flag = 0u;
    if (event_type == QL_REQUEST_UP) {
        event.uid = ui->items[0].uid;
        QL_LOG(4u, fn_send_request, 1124u, 0x10400000u, send_up, send_up_short, event.uid);
    } else if (event_type == QL_REQUEST_DOWN) {
        event.uid = ui->items[ui->count - 1u].uid;
        QL_LOG(4u, fn_send_request, 1129u, 0x10400000u, send_down, send_down_short, event.uid);
    } else {
        QL_LOG(1u, fn_send_request, 1131u, 0x04400000u, bad_type, bad_type_short, event_type);
        return;
    }

    result = APP_PbNotifyEncodeQuicklistEvent(0u, &event);
    if (result != 0)
        QL_LOG(1u, fn_send_request, 1138u, 0x04400000u, send_failed, send_failed_short, result);
}

/* True when a full page is loaded and the focus is within five rows of the
 * edge the request would extend. */
uint8_t quicklist_need_data_request_4f61a0(uint8_t event_type)
{
    const uint32_t count = g2_quicklist_ui_data_2012a72c.count;

    if (count < QL_REQUEST_MIN_ROWS)
        return 0u;
    if (event_type == QL_REQUEST_UP)
        return (uint8_t)(g2_quicklist_focus_index_200042c0 + 1 < QL_REQUEST_EDGE_ROWS);
    if (event_type == QL_REQUEST_DOWN)
        return (uint8_t)((int32_t)(count - (uint32_t)g2_quicklist_focus_index_200042c0) - 1 <
                         QL_REQUEST_EDGE_ROWS);
    return 0u;
}

uint8_t quicklist_can_send_data_request_4f61f4(void)
{
    const uint64_t now = osKernelGetTickCount();

    if (g2_quicklist_request_tick_200741a8 != 0u) {
        const uint64_t diff = now - g2_quicklist_request_tick_200741a8;
        if (diff < QL_REQUEST_DEBOUNCE_MS) {
            QL_LOG(4u, fn_can_send, 1185u, 0x10800000u, too_frequent, too_frequent_short, diff,
                   (int32_t)QL_REQUEST_DEBOUNCE_MS);
            return 0u;
        }
    }
    return 1u;
}

void quicklist_request_data_with_debounce_4f6282(uint8_t event_type)
{
    if (quicklist_can_send_data_request_4f61f4() == 0u)
        return;
    g2_quicklist_request_tick_200741a8 = osKernelGetTickCount();
    QL_LOG(4u, fn_debounce, 1206u, 0x10400000u, debounce, debounce_short, event_type);
    quicklist_send_data_request_event_4f5fd0(event_type);
}

/* `stamp` is the 64-bit second argument (r2:r3); r1 is unused padding. */
int32_t quicklist_add_completed_uid_to_temp_cache_4f658c(uint32_t uid, uint64_t stamp)
{
    g2_quicklist_uid_cache_t *const cache = &g2_quicklist_temp_cache_20130654;

    if (cache->count >= QL_MAX_ITEMS) {
        QL_LOG(2u, fn_add_temp, 1326u, 0x08400000u, temp_full, temp_full_short, uid);
        return -1;
    }
    cache->entries[cache->count].uid = uid;
    cache->entries[cache->count].stamp = stamp;
    ++cache->count;
    QL_LOG(4u, fn_add_temp, 1346u, 0x10800000u, temp_added, temp_added_short, uid, cache->count);
    return 0;
}

int32_t quicklist_remove_completed_uid_from_temp_cache_4f6664(uint32_t uid)
{
    g2_quicklist_uid_cache_t *const cache = &g2_quicklist_temp_cache_20130654;
    int32_t index;

    for (index = 0; index < (int32_t)cache->count; ++index) {
        if (cache->entries[index].uid == uid)
            break;
    }
    if (index >= (int32_t)cache->count) {
        QL_LOG(4u, fn_remove_temp, 1368u, 0x10400000u, temp_missing, temp_missing_short, uid);
        return -1;
    }
    for (; index < (int32_t)cache->count - 1; ++index) {
        uint8_t *const dst = (uint8_t *)&cache->entries[index];
        const uint8_t *const src = (const uint8_t *)&cache->entries[index + 1];
        for (uint32_t i = 0u; i < sizeof cache->entries[0]; ++i)
            dst[i] = src[i];
    }
    --cache->count;
    QL_LOG(4u, fn_remove_temp, 1364u, 0x10800000u, temp_removed, temp_removed_short, uid, cache->count);
    return 0;
}

/* Returns the number of UIDs appended (existing UIDs only get a new stamp). */
int32_t quicklist_merge_temp_cache_to_completed_items_4f6770(void)
{
    g2_quicklist_uid_cache_t *const temp = &g2_quicklist_temp_cache_20130654;
    g2_quicklist_uid_cache_t *const done = &g2_quicklist_completed_201303cc;
    int32_t added = 0;

    for (int32_t i = 0; i < (int32_t)temp->count; ++i) {
        const uint32_t uid = temp->entries[i].uid;
        const uint64_t stamp = temp->entries[i].stamp;
        uint8_t found = 0u;

        for (int32_t j = 0; j < (int32_t)done->count; ++j) {
            if (done->entries[j].uid == uid) {
                done->entries[j].stamp = stamp;
                found = 1u;
                break;
            }
        }
        if (found == 0u && done->count < QL_MAX_ITEMS) {
            done->entries[done->count].uid = uid;
            done->entries[done->count].stamp = stamp;
            ++done->count;
            ++added;
        }
    }
    audio_uart_buffer_zero(temp, sizeof *temp, 0u);
    QL_LOG(4u, fn_merge, 1408u, 0x10800000u, merged, merged_short, added, done->count);
    return added;
}

/* Input codes 0x0a (click), 0x44/0x45 (scroll with point), 0x48 (back),
 * 0x49 (exit) are forwarded to the master. The stock returns r0 unchanged for
 * other codes (the event pointer); 0 is returned here. */
int32_t QuicklistInputEventHandler_4f6880(int32_t code, const void *e)
{
    uint8_t frame[6];

    if (g2_quicklist_anim_state_20074e20 != 0) {
        QL_LOG(3u, fn_input, 1418u, 0x0c400000u, animating, animating_short,
               g2_quicklist_anim_state_20074e20);
        return 0;
    }
    if (code == 0x0a || code == 0x48 || code == 0x49) {
        frame[0] = 0u;
        frame[1] = (uint8_t)code;
        frame[2] = 0u;
        frame[3] = 0u;
        frame[4] = 0u;
        frame[5] = 0u;
        return audio_uart_master_display_refresh(1u, frame, 6u, 0u);
    }
    if (code == 0x45 || code == 0x44) {
        const int32_t *const point = (const int32_t *)((const g2_lv_event_head_t *)e)->param;
        frame[0] = 0u;
        frame[1] = (uint8_t)code;
        frame[2] = (uint8_t)point[0];
        frame[3] = (uint8_t)(point[0] >> 8);
        frame[4] = (uint8_t)point[1];
        frame[5] = (uint8_t)(point[1] >> 8);
        return audio_uart_master_display_refresh(1u, frame, 6u, 0u);
    }
    return 0;
}

/* Dashboard page-state sync to the phone app, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\page_state_sync.c.
 * Native 0x4ffe14..0x5002ef; literal pool 0x5002f0..0x500377.
 *
 * The current page state lives in one 0x3c-byte record (RAM 0x200732ac).
 * Each page_state_sync_* entry fills it and send_page_state_to_app packs it
 * into the 64-byte page-state payload of a dashboard app message (data_type 3,
 * dashboard_send_page_state_to_app 0x4ff7dc). Only the master (service mode 1)
 * sends; the slave returns 0 without sending. */
#include <stdint.h>
#include <stddef.h>

#define PAGE_STATE_ITEMS_MAX 10u

/* Page-state kinds (record type; the wire kind is type + 1). */
enum {
    PAGE_STATE_NONE = 0u,
    PAGE_STATE_DASHBOARD_MAIN = 1u,
    PAGE_STATE_2 = 2u,
    PAGE_STATE_STOCK_EXPANDED = 3u,
    PAGE_STATE_CALENDAR_EXPANDED = 4u,
    PAGE_STATE_QUICKLIST_EXPANDED = 5u,
    PAGE_STATE_HEALTH_EXPANDED = 6u,
};

typedef struct {
    uint8_t type;              /* +0x00 */
    uint8_t reserved_01[3];
    uint32_t value;            /* +0x04 tile index, page or quicklist count */
    union {
        uint8_t widget;        /* +0x08 dashboard main */
        uint32_t items[PAGE_STATE_ITEMS_MAX]; /* +0x08 quicklist */
    } u;
    uint32_t border;           /* +0x30 */
    uint32_t focused;          /* +0x34 */
    uint8_t completed;         /* +0x38 */
    uint8_t reserved_39[3];
} g2_page_state_t;
_Static_assert(sizeof(g2_page_state_t) == 0x3cu, "page state record is 60 bytes");

typedef struct {
    uint8_t type;              /* +0x00 */
    uint8_t reserved_01;
    uint16_t kind;             /* +0x02 type + 1 */
    uint32_t value;            /* +0x04 */
    union {
        uint8_t widget;        /* +0x08 */
        uint16_t item_count;   /* +0x08 */
    } u;
    uint8_t reserved_0a[2];
    uint32_t items[PAGE_STATE_ITEMS_MAX]; /* +0x0c */
    uint32_t border;           /* +0x34 */
    uint32_t focused;          /* +0x38 */
    uint8_t completed;         /* +0x3c */
    uint8_t reserved_3d[3];
} g2_page_state_msg_t;
_Static_assert(sizeof(g2_page_state_msg_t) == 0x40u, "page state payload is 64 bytes");

extern g2_page_state_t g2_page_state;          /* RAM 0x200732ac */
extern uint32_t g2_page_state_package_id;      /* RAM 0x20003060 (initialised data) */
extern int32_t g2_dashboard_last_saved_tile;   /* RAM 0x20074bb4 */

extern const uint8_t *dashboard_layout_get_current_558142(void);
extern uint8_t audio_uart_service_mode(void); /* 0x45a570, 1 = master */
extern int32_t dashboard_send_page_state_to_app_4ff7dc(uint32_t package_id, uint8_t flag, const void *page_state);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void audio_uart_lv_memzero_48949c(void *dst, uint32_t len);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

#define LOG_E(level, fn, line, ...)                                                          \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), __VA_ARGS__); \
    } while (0)
#define LOG_C(code, ...)                                                \
    do {                                                                \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))       \
            (void)compress_log_output((code), __VA_ARGS__);             \
    } while (0)

static const char module_tag[] = "page_state_sync"; /* ROM 0x787c60 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\page_state_sync.c"; /* ROM 0x6fbccc */
static const char init_fn[] = "page_state_sync_init";                        /* ROM 0x779f34 */
static const char send_fn[] = "send_page_state_to_app";                      /* ROM 0x779f4c */
static const char main_fn[] = "page_state_sync_dashboard_main";              /* ROM 0x762ef0 */
static const char stock_fn[] = "page_state_sync_stock_expanded";             /* ROM 0x762f10 */
static const char calendar_fn[] = "page_state_sync_calendar_expanded";       /* ROM 0x757620 */
static const char quicklist_fn[] = "page_state_sync_quicklist_expanded";     /* ROM 0x757644 */
static const char health_fn[] = "page_state_sync_health_expanded";           /* ROM 0x762f30 */
static const char init_start[] = "page state sync start, initial_tile_index=%d "; /* ROM 0x7365e4 */
static const char init_start_short[] =
    "[page_state_sync]page state sync start, initial_tile_index=%d "; /* ROM 0x70d864 */
static const char init_done[] = "Page state sync module initialized successfully"; /* ROM 0x736614 */
static const char init_done_short[] =
    "[page_state_sync]Page state sync module initialized successfully"; /* ROM 0x704638 */
static const char state_null[] = "Page state is NULL"; /* ROM 0x7817c8 */
static const char state_null_short[] = "[page_state_sync]Page state is NULL"; /* ROM 0x7575d8 */
static const char send_failed[] = "Failed to send page state to app, ret=%d"; /* ROM 0x7410d4 */
static const char send_failed_short[] = "[page_state_sync]Failed to send page state to app, ret=%d"; /* ROM 0x717488 */
static const char send_ok[] = "Page state sent to app successfully"; /* ROM 0x7575fc */
static const char send_ok_short[] = "[page_state_sync]Page state sent to app successfully"; /* ROM 0x721208 */
static const char main_synced[] = "Dashboard main page state synced: tile=%d, widget=%d"; /* ROM 0x721240 */
static const char main_synced_short[] =
    "[page_state_sync]Dashboard main page state synced: tile=%d, widget=%d"; /* ROM 0x6fbd14 */
static const char stock_synced[] = "Stock expanded page state synced: page=%d"; /* ROM 0x741100 */
static const char stock_synced_short[] = "[page_state_sync]Stock expanded page state synced: page=%d"; /* ROM 0x7174c4 */
static const char calendar_synced[] = "Calendar expanded page state synced: page=%d"; /* ROM 0x736644 */
static const char calendar_synced_short[] =
    "[page_state_sync]Calendar expanded page state synced: page=%d"; /* ROM 0x70d8a4 */
static const char quicklist_synced[] =
    "Quicklist expanded page state synced: count=%d, border=%d, focused=%d, completed=%s"; /* ROM 0x6e9118 */
static const char quicklist_synced_short[] =
    "[page_state_sync]Quicklist expanded page state synced: count=%d, border=%d, focused=%d, completed=%s"; /* ROM 0x6d93c4 */
static const char health_synced[] = "Health expanded page state synced: page=%d"; /* ROM 0x74112c */
static const char health_synced_short[] =
    "[page_state_sync]Health expanded page state synced: page=%d"; /* ROM 0x717500 */
static const char str_true[] = "true";   /* ROM 0x78de6c */
static const char str_false[] = "false"; /* ROM 0x78de74 */

void page_state_sync_init_4ffe14(void)
{
    int32_t tile = g2_dashboard_last_saved_tile;

    LOG_E(4u, init_fn, 0x23u, init_start, tile);
    LOG_C(0x10400000u, init_start_short, init_start_short, tile);
    (void)aeabi_memset_43c0e4(&g2_page_state, sizeof g2_page_state, 0);
    LOG_E(4u, init_fn, 0x27u, init_done);
    LOG_C(0x10000000u, init_done_short, init_done_short);
}

/* Widget code of a dashboard tile from the current layout (layout byte 1 =
 * tile count, bytes 2.. = per-tile widget kinds). Unknown tiles map to 1. */
uint8_t dashboard_widget_page_type_4ffeb4(uint32_t tile_index)
{
    const uint8_t *layout = dashboard_layout_get_current_558142();

    if (layout == NULL || tile_index >= layout[1])
        return 1u;
    switch (layout[tile_index + 2u]) {
    case 0u: return 1u;
    case 1u: return 2u;
    case 2u: return 3u;
    case 3u: return 5u;
    case 4u: return 4u;
    default: return 1u;
    }
}

int32_t send_page_state_to_app_4ffef8(const g2_page_state_t *state)
{
    g2_page_state_msg_t msg;
    uint32_t n;
    uint32_t i;
    int32_t ret;

    if (state == NULL) {
        LOG_E(1u, send_fn, 0x62u, state_null);
        LOG_C(0x04000000u, state_null_short, state_null_short);
        return -1;
    }
    if (audio_uart_service_mode() != 1u)
        return 0;

    audio_uart_lv_memzero_48949c(&msg, sizeof msg);
    switch (state->type) {
    case PAGE_STATE_DASHBOARD_MAIN:
        msg.type = 1u;
        msg.kind = 2u;
        msg.value = state->value;
        msg.u.widget = state->u.widget;
        break;
    case PAGE_STATE_2:
        msg.type = 2u;
        msg.kind = 3u;
        msg.value = state->value;
        break;
    case PAGE_STATE_STOCK_EXPANDED:
        msg.type = 3u;
        msg.kind = 4u;
        msg.value = state->value;
        break;
    case PAGE_STATE_CALENDAR_EXPANDED:
        msg.type = 4u;
        msg.kind = 5u;
        msg.value = state->value;
        break;
    case PAGE_STATE_QUICKLIST_EXPANDED:
        msg.type = 5u;
        msg.kind = 6u;
        msg.value = state->value;
        msg.border = state->border;
        msg.focused = state->focused;
        msg.completed = state->completed;
        n = (state->value < PAGE_STATE_ITEMS_MAX + 1u) ? state->value : PAGE_STATE_ITEMS_MAX;
        msg.u.item_count = (uint16_t)n;
        for (i = 0u; i < n; i++)
            msg.items[i] = state->u.items[i];
        break;
    case PAGE_STATE_HEALTH_EXPANDED:
        msg.type = 6u;
        msg.kind = 7u;
        msg.value = state->value;
        break;
    default:
        break;
    }

    ret = dashboard_send_page_state_to_app_4ff7dc(g2_page_state_package_id++, 0u, &msg);
    if (ret != 0) {
        LOG_E(1u, send_fn, 0xa1u, send_failed, ret);
        LOG_C(0x04400000u, send_failed_short, send_failed_short, ret);
        return -1;
    }
    LOG_E(4u, send_fn, 0xa5u, send_ok);
    LOG_C(0x10000000u, send_ok_short, send_ok_short);
    return 0;
}

int32_t page_state_sync_dashboard_main_5000cc(uint32_t tile_index, uint8_t widget)
{
    int32_t ret;

    g2_page_state.type = PAGE_STATE_DASHBOARD_MAIN;
    g2_page_state.value = tile_index;
    g2_page_state.u.widget = widget;
    ret = send_page_state_to_app_4ffef8(&g2_page_state);
    LOG_E(4u, main_fn, 0xb4u, main_synced, tile_index, widget);
    LOG_C(0x10800000u, main_synced_short, main_synced_short, tile_index, widget);
    return ret;
}

int32_t page_state_sync_stock_expanded_50012e(uint32_t page)
{
    int32_t ret;

    g2_page_state.type = PAGE_STATE_STOCK_EXPANDED;
    g2_page_state.value = page;
    ret = send_page_state_to_app_4ffef8(&g2_page_state);
    LOG_E(4u, stock_fn, 0xd0u, stock_synced, page);
    LOG_C(0x10400000u, stock_synced_short, stock_synced_short, page);
    return ret;
}

int32_t page_state_sync_calendar_expanded_500180(uint32_t page)
{
    int32_t ret;

    g2_page_state.type = PAGE_STATE_CALENDAR_EXPANDED;
    g2_page_state.value = page;
    ret = send_page_state_to_app_4ffef8(&g2_page_state);
    LOG_E(4u, calendar_fn, 0xdeu, calendar_synced, page);
    LOG_C(0x10400000u, calendar_synced_short, calendar_synced_short, page);
    return ret;
}

int32_t page_state_sync_quicklist_expanded_5001d2(uint32_t count, const uint32_t *items, uint32_t border,
                                                  uint32_t focused, uint8_t completed)
{
    uint32_t n;
    int32_t ret;

    g2_page_state.type = PAGE_STATE_QUICKLIST_EXPANDED;
    g2_page_state.value = count;
    g2_page_state.border = border;
    g2_page_state.focused = focused;
    g2_page_state.completed = completed;
    n = (count < PAGE_STATE_ITEMS_MAX + 1u) ? count : PAGE_STATE_ITEMS_MAX;
    if (n == 0u || items == NULL)
        (void)aeabi_memset_43c0e4(g2_page_state.u.items, sizeof g2_page_state.u.items, 0);
    else
        (void)audio_queue_copy_bytes(g2_page_state.u.items, items, n * 4u);
    ret = send_page_state_to_app_4ffef8(&g2_page_state);
    LOG_E(4u, quicklist_fn, 0x100u, quicklist_synced, count, border, focused,
          completed ? str_true : str_false);
    LOG_C(0x11000000u, quicklist_synced_short, quicklist_synced_short, count, border, focused,
          completed ? str_true : str_false);
    return ret;
}

int32_t page_state_sync_health_expanded_50029c(uint32_t page)
{
    int32_t ret;

    g2_page_state.type = PAGE_STATE_HEALTH_EXPANDED;
    g2_page_state.value = page;
    ret = send_page_state_to_app_4ffef8(&g2_page_state);
    LOG_E(4u, health_fn, 0x10fu, health_synced, page);
    LOG_C(0x10400000u, health_synced_short, health_synced_short, page);
    return ret;
}

/* Teleprompt page cache, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_page_data.c.
 * Native 0x58a8e0..0x58bc06; literal pools 0x58b344..0x58b36f,
 * 0x58b528..0x58b567, 0x58b830..0x58b83b, 0x58b8ec..0x58b8ef,
 * 0x58b954..0x58b97f, 0x58bc08..0x58bcdf.
 *
 * Pages arrive from the phone one at a time (PageData). They are kept in a
 * 20-slot ring (slot = page % 20). The UI shows a 4-page window starting at
 * window_start; the cache additionally preloads [window_start - 5,
 * window_start + 8]. A one-shot 2.5 s timer re-requests pages that are
 * missing or whose request is older than 5 s; requests younger than 500 ms
 * are debounced. Only the master (right) arm talks to the phone. */
#include <stddef.h>
#include <stdint.h>
#include "g2_teleprompt_page_data.h"

#define PAGE_WINDOW_PAGES 4u
#define PRELOAD_BEFORE 5u
#define PRELOAD_AFTER 8u
#define PRELOAD_TIMER_TICKS 2500u     /* 0x9c4 */
#define REQUEST_DEBOUNCE_TICKS 500u
#define LOADING_TIMEOUT_TICKS 5000u   /* > 4999 */
#define DEVICE_ROLE_MASTER 1
#define TELEPROMPT_EVT_LOADING_DONE 5u

enum {
    SLOT_EMPTY = 0u,
    SLOT_REQUESTED = 1u,
    SLOT_LOADED = 2u,
};

typedef struct {
    g2_teleprompt_page_t page; /* +0x000 */
    uint8_t state;             /* +0x40c SLOT_* */
    uint8_t reserved_40d[3];
    uint32_t request_tick;     /* +0x410 tick of the last request, 0 none */
} teleprompt_page_slot_t;
_Static_assert(sizeof(teleprompt_page_slot_t) == 0x414, "stock slot stride is 0x414");

typedef struct {
    teleprompt_page_slot_t slot[G2_TELEPROMPT_PAGE_SLOTS]; /* +0x0000 */
    uint32_t total_pages;      /* +0x5190 */
    uint32_t window_start;     /* +0x5194 */
    uint32_t window_ready;     /* +0x5198 loading-done posted for this window */
    uint32_t window_tick;      /* +0x519c */
    uint8_t initialized;       /* +0x51a0 */
    uint8_t window_set;        /* +0x51a1 */
    uint8_t reserved_51a2[2];
} teleprompt_page_ctx_t;
_Static_assert(offsetof(teleprompt_page_ctx_t, total_pages) == 0x5190, "total_pages at +0x5190");
_Static_assert(offsetof(teleprompt_page_ctx_t, window_set) == 0x51a1, "window_set at +0x51a1");
_Static_assert(sizeof(teleprompt_page_ctx_t) == 0x51a4, "stock memset size");

typedef struct {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
} os_timer_attr_t;

static teleprompt_page_ctx_t g2_teleprompt_page_ctx;     /* RAM 0x2010a328 */
static void *g2_teleprompt_page_mutex;                   /* RAM 0x20074a6c */
static void *g2_teleprompt_preload_timer;                /* RAM 0x20074a70 */
static g2_teleprompt_page_t g2_teleprompt_page_copy;     /* RAM 0x2006b11c, returned by _get */
static uint32_t g2_teleprompt_preload_timer_cb[11];      /* RAM 0x20073700, 0x2c-byte timer CB */

static const char preload_timer_name[] = "teleprompt_preload_timer"; /* ROM 0x772c1c */
static const os_timer_attr_t preload_timer_attr = {      /* ROM 0x7897a0 */
    preload_timer_name, 0u, g2_teleprompt_preload_timer_cb, sizeof g2_teleprompt_preload_timer_cb,
};

extern void *osMutexNew(const void *attr);                                       /* 0x44971c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                    /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                      /* 0x44981c */
extern int32_t osMutexDelete(void *mutex);
extern void *osTimerNew(void (*func)(void *), uint32_t type, void *argument, const void *attr); /* 0x4493b0 */
extern int32_t osTimerStart(void *timer, uint32_t ticks);                        /* 0x449498 */
extern int32_t osTimerStop(void *timer);
extern int32_t osTimerDelete(void *timer);
extern uint32_t osKernelGetTickCount(void);                                      /* 0x4490cc */
extern uint32_t APP_PbTxEncodePageDataRequest(const uint32_t *request);          /* 0x588b40 */
extern uint32_t teleprompt_controller_post_589b68(uint8_t event, uint32_t arg);
extern uint32_t display_driver_uled_mode_45a568(void);        /* device role, 1 = master */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);   /* 0x439be4 memcpy */
extern uint32_t audio_log_flags(void);                                           /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);  /* 0x43ce9e */

void teleprompt_preload_timer_callback(void *argument);
void teleprompt_page_data_set_window(uint32_t window_start);

static const char module_tag[] = "teleprompt.page"; /* ROM 0x789780 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_page_data.c"; /* ROM 0x6f0128 */

static const char fn_lock[] = "page_data_lock"; /* ROM 0x789770 */
static const char lock_failed[] = "page_data_lock failed"; /* ROM 0x77c49c */
static const char lock_failed_c[] = "[teleprompt.page]page_data_lock failed"; /* ROM 0x74ef74 */

static const char fn_timer_create[] = "teleprompt_preload_timer_ensure_created"; /* ROM 0x74ef9c */
static const char timer_create_failed[] = "create preload timer failed"; /* ROM 0x772c38 */
static const char timer_create_failed_c[] = "[teleprompt.page]create preload timer failed"; /* ROM 0x739164 */
static const char timer_created[] = "preload timer created"; /* ROM 0x77c4b4 */
static const char timer_created_c[] = "[teleprompt.page]preload timer created"; /* ROM 0x74efc4 */

static const char fn_request_locked[] = "request_page_data_locked"; /* ROM 0x772c54 */
static const char invalid_page[] = "Invalid page_id: %d, max: %d"; /* ROM 0x765e30 */
static const char invalid_page_c[] = "[teleprompt.page]Invalid page_id: %d, max: %d"; /* ROM 0x739194 */
static const char req_loaded[] = "request skip: page=%u already loaded (slot=%u)"; /* ROM 0x7391c4 */
static const char req_loaded_c[] = "[teleprompt.page]request skip: page=%u already loaded (slot=%u)"; /* ROM 0x70fca4 */
static const char req_debounce[] = "request debounce: page=%u slot=%u delta=%u"; /* ROM 0x7445f0 */
static const char req_debounce_c[] = "[teleprompt.page]request debounce: page=%u slot=%u delta=%u"; /* ROM 0x7194e0 */
static const char req_loading[] = "request skip: page=%u still loading (slot=%u), waiting timeout"; /* ROM 0x70fce4 */
static const char req_loading_c[] = "[teleprompt.page]request skip: page=%u still loading (slot=%u), waiting timeout"; /* ROM 0x6f0178 */
static const char req_retry[] = "request retry: page=%u loading timeout (slot=%u elapsed=%u)"; /* ROM 0x71951c */
static const char req_retry_c[] = "[teleprompt.page]request retry: page=%u loading timeout (slot=%u elapsed=%u)"; /* ROM 0x6f01c8 */
static const char req_bad_flag[] = "Invalid page %d slot %d preload flag: %d"; /* ROM 0x74461c */
static const char req_bad_flag_c[] = "[teleprompt.page]Invalid page %d slot %d preload flag: %d"; /* ROM 0x719558 */
static const char req_sent[] = "request sent: page=%u slot=%u"; /* ROM 0x765e50 */
static const char req_sent_c[] = "[teleprompt.page]request sent: page=%u slot=%u"; /* ROM 0x7391f4 */
static const char req_timer_failed[] = "timer start failed after request: page=%u"; /* ROM 0x744648 */
static const char req_timer_failed_c[] = "[teleprompt.page]timer start failed after request: page=%u"; /* ROM 0x719594 */

static const char fn_request[] = "teleprompt_request_page_data"; /* ROM 0x765e70 */
static const char req_not_master[] = "request skip: not master role, page=%u"; /* ROM 0x74efec */
static const char req_not_master_c[] = "[teleprompt.page]request skip: not master role, page=%u"; /* ROM 0x723d90 */
static const char req_lock_failed[] = "request failed: lock failed, page=%u"; /* ROM 0x74f014 */
static const char req_lock_failed_c[] = "[teleprompt.page]request failed: lock failed, page=%u"; /* ROM 0x723dc8 */

static const char fn_timer_cb[] = "teleprompt_preload_timer_callback"; /* ROM 0x75adac */
static const char cb_lock_failed[] = "timer callback abort: lock failed"; /* ROM 0x75add0 */
static const char cb_lock_failed_c[] = "[teleprompt.page]timer callback abort: lock failed"; /* ROM 0x72e6cc */
static const char cb_complete[] = "timer callback: ensure range already complete"; /* ROM 0x739224 */
static const char cb_complete_c[] = "[teleprompt.page]timer callback: ensure range already complete"; /* ROM 0x70fd24 */
static const char cb_retry[] = "timer retry page=%u"; /* ROM 0x783e88 */
static const char cb_retry_c[] = "[teleprompt.page]timer retry page=%u"; /* ROM 0x74f03c */
static const char cb_restart_failed[] = "timer restart failed on waiting-loading state"; /* ROM 0x739254 */
static const char cb_restart_failed_c[] = "[teleprompt.page]timer restart failed on waiting-loading state"; /* ROM 0x70fd64 */

static const char fn_init[] = "teleprompt_page_data_init"; /* ROM 0x772c70 */
static const char init_invalid[] = "Invalid total_pages: %d, start_page_id: %d"; /* ROM 0x744674 */
static const char init_invalid_c[] = "[teleprompt.page]Invalid total_pages: %d, start_page_id: %d"; /* ROM 0x7195d0 */
static const char init_mutex_failed[] = "teleprompt page_data mutex create failed"; /* ROM 0x7446a0 */
static const char init_mutex_failed_c[] = "[teleprompt.page]teleprompt page_data mutex create failed"; /* ROM 0x71960c */
static const char init_lock_failed[] = "init failed: lock failed"; /* ROM 0x772c8c */
static const char init_lock_failed_c[] = "[teleprompt.page]init failed: lock failed"; /* ROM 0x7446cc */
static const char init_ok[] = "init ok: start_page=%u total=%u window_start=%u"; /* ROM 0x739284 */
static const char init_ok_c[] = "[teleprompt.page]init ok: start_page=%u total=%u window_start=%u"; /* ROM 0x7067b0 */

static const char fn_deinit[] = "teleprompt_page_data_deinit"; /* ROM 0x772ca8 */
static const char deinit_skip[] = "deinit skip: not initialized"; /* ROM 0x765e90 */
static const char deinit_skip_c[] = "[teleprompt.page]deinit skip: not initialized"; /* ROM 0x7392b4 */
static const char deinit_lock_failed[] = "deinit failed: lock failed"; /* ROM 0x772cc4 */
static const char deinit_lock_failed_c[] = "[teleprompt.page]deinit failed: lock failed"; /* ROM 0x7446f8 */
static const char deinit_begin[] = "deinit begin"; /* ROM 0x789790 */
static const char deinit_begin_c[] = "[teleprompt.page]deinit begin"; /* ROM 0x765eb0 */
static const char deinit_done[] = "deinit done"; /* ROM 0x78c500 */
static const char deinit_done_c[] = "[teleprompt.page]deinit done"; /* ROM 0x765ed0 */

static const char fn_update[] = "teleprompt_page_data_update"; /* ROM 0x772ce0 */
static const char update_null[] = "page_data is NULL"; /* ROM 0x783e9c */
static const char update_null_c[] = "[teleprompt.page]page_data is NULL"; /* ROM 0x75adf4 */
static const char update_lock_failed[] = "update failed: lock failed"; /* ROM 0x772cfc */
static const char update_lock_failed_c[] = "[teleprompt.page]update failed: lock failed"; /* ROM 0x744724 */
static const char update_loaded[] = "update skip: page=%u already loaded (slot=%u)"; /* ROM 0x7392e4 */
static const char update_loaded_c[] = "[teleprompt.page]update skip: page=%u already loaded (slot=%u)"; /* ROM 0x70fda4 */
static const char update_ok[] = "update ok: page=%u slot=%u text_size=%u"; /* ROM 0x74f064 */
static const char update_ok_c[] = "[teleprompt.page]update ok: page=%u slot=%u text_size=%u"; /* ROM 0x719648 */
static const char update_ready[] = "window ready, trigger loading done"; /* ROM 0x75ae18 */
static const char update_ready_c[] = "[teleprompt.page]window ready, trigger loading done"; /* ROM 0x72e700 */

static const char fn_get[] = "teleprompt_page_data_get"; /* ROM 0x772d18 */
static const char get_lock_failed[] = "get failed: lock failed, page=%u"; /* ROM 0x75ae3c */
static const char get_lock_failed_c[] = "[teleprompt.page]get failed: lock failed, page=%u"; /* ROM 0x72e734 */

static const char fn_set_window[] = "teleprompt_page_data_set_window"; /* ROM 0x765ef0 */
static const char win_lock_failed[] = "set_window failed: lock failed, window_start=%u"; /* ROM 0x739314 */
static const char win_lock_failed_c[] = "[teleprompt.page]set_window failed: lock failed, window_start=%u"; /* ROM 0x7067f4 */
static const char win_unchanged[] = "set_window skip: unchanged window=%u delta=%u"; /* ROM 0x739344 */
static const char win_unchanged_c[] = "[teleprompt.page]set_window skip: unchanged window=%u delta=%u"; /* ROM 0x70fde4 */
static const char win_set[] = "set_window: req_start=%u effective_start=%u ensure=[%u,%u]"; /* ROM 0x719684 */
static const char win_set_c[] = "[teleprompt.page]set_window: req_start=%u effective_start=%u ensure=[%u,%u]"; /* ROM 0x6f6828 */
static const char win_timer_failed[] = "set_window timer start failed"; /* ROM 0x765f10 */
static const char win_timer_failed_c[] = "[teleprompt.page]set_window timer start failed"; /* ROM 0x739374 */
static const char win_done[] = "set_window done: win_req=%u preload_req=%u"; /* ROM 0x744750 */
static const char win_done_c[] = "[teleprompt.page]set_window done: win_req=%u preload_req=%u"; /* ROM 0x7196c0 */

/* Extended log (flag bit 1) then compressed log (bit 0 or 2); cflags is
 * level << 26 | argument count << 22. */
#define TP_LOG(level, fn, line, msg, cflags, cmsg, ...)                                      \
    do {                                                                                     \
        if (audio_log_flags() & 2u)                                                          \
            audio_log_extended((level), module_tag, source_file, (fn), (line), (msg), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                            \
            (void)compress_log_output((cflags), (cmsg), (cmsg), ##__VA_ARGS__);              \
    } while (0)

/* Returns 1 when locked or when no mutex exists yet, 0 on acquire failure. */
uint8_t page_data_lock(void)
{
    if (g2_teleprompt_page_mutex == NULL)
        return 1u;
    if (osMutexAcquire(g2_teleprompt_page_mutex, 0xffffffffu) == 0)
        return 1u;
    TP_LOG(1u, fn_lock, 0x5au, lock_failed, 0x04000000u, lock_failed_c);
    return 0u;
}

void semantic_page_data_unlock(void)
{
    if (g2_teleprompt_page_mutex != NULL)
        (void)osMutexRelease(g2_teleprompt_page_mutex);
}

int32_t teleprompt_preload_timer_ensure_created(void)
{
    if (g2_teleprompt_preload_timer != NULL)
        return 0;
    g2_teleprompt_preload_timer = osTimerNew(teleprompt_preload_timer_callback, 0u, NULL, &preload_timer_attr);
    if (g2_teleprompt_preload_timer == NULL) {
        TP_LOG(1u, fn_timer_create, 0x70u, timer_create_failed, 0x04000000u, timer_create_failed_c);
        return -1;
    }
    TP_LOG(3u, fn_timer_create, 0x73u, timer_created, 0x0c000000u, timer_created_c);
    return 0;
}

uint32_t semantic_page_to_slot(uint32_t page)
{
    return page % G2_TELEPROMPT_PAGE_SLOTS;
}

uint8_t semantic_slot_loaded(uint32_t slot, uint32_t page)
{
    const teleprompt_page_slot_t *s = &g2_teleprompt_page_ctx.slot[slot];
    return (s->state == SLOT_LOADED && s->page.page_id == page) ? 1u : 0u;
}

uint32_t semantic_clamp_window_start(uint32_t start)
{
    uint32_t total = g2_teleprompt_page_ctx.total_pages;
    if (total < PAGE_WINDOW_PAGES + 1u)
        start = 0u;
    else if (total < start + PAGE_WINDOW_PAGES)
        start = total - PAGE_WINDOW_PAGES;
    return start;
}

uint8_t semantic_loading_timed_out(uint32_t slot, uint32_t page, uint32_t now);

/* Caller holds the lock. Returns 0 when sent or skipped, -1 on a bad page
 * id or an inconsistent slot. */
int32_t request_page_data_locked(uint32_t page, uint8_t start_timer)
{
    teleprompt_page_ctx_t *ctx = &g2_teleprompt_page_ctx;

    if (page >= ctx->total_pages) {
        TP_LOG(1u, fn_request_locked, 0x94u, invalid_page, 0x04800000u, invalid_page_c, page,
               ctx->total_pages - 1u);
        return -1;
    }

    uint32_t slot = semantic_page_to_slot(page);
    if (semantic_slot_loaded(slot, page)) {
        TP_LOG(3u, fn_request_locked, 0x9au, req_loaded, 0x0c800000u, req_loaded_c, page, slot);
        return 0;
    }

    teleprompt_page_slot_t *s = &ctx->slot[slot];
    uint32_t now = osKernelGetTickCount();
    if (s->request_tick != 0u && s->page.page_id == page && now - s->request_tick < REQUEST_DEBOUNCE_TICKS) {
        TP_LOG(4u, fn_request_locked, 0xa3u, req_debounce, 0x10c00000u, req_debounce_c, page, slot,
               now - s->request_tick);
        return 0;
    }

    if (s->state == SLOT_REQUESTED && s->page.page_id == page) {
        if (!semantic_loading_timed_out(slot, page, now)) {
            TP_LOG(3u, fn_request_locked, 0xaau, req_loading, 0x0c800000u, req_loading_c, page, slot);
            return 0;
        }
        uint32_t elapsed = now - s->request_tick;
        TP_LOG(2u, fn_request_locked, 0xaeu, req_retry, 0x08c00000u, req_retry_c, page, slot, elapsed);
    } else {
        if (s->state != SLOT_EMPTY && s->page.page_id == page) {
            TP_LOG(1u, fn_request_locked, 0xb4u, req_bad_flag, 0x04c00000u, req_bad_flag_c, page, slot,
                   s->state);
            return -1;
        }
        s->state = SLOT_REQUESTED;
        s->page.page_id = page;
    }

    uint32_t request = page;
    (void)APP_PbTxEncodePageDataRequest(&request);
    s->request_tick = now;
    TP_LOG(3u, fn_request_locked, 0xbbu, req_sent, 0x0c800000u, req_sent_c, page, slot);

    if (start_timer != 0u && teleprompt_preload_timer_ensure_created() == 0 &&
        osTimerStart(g2_teleprompt_preload_timer, PRELOAD_TIMER_TICKS) != 0)
        TP_LOG(2u, fn_request_locked, 0xbfu, req_timer_failed, 0x08400000u, req_timer_failed_c, page);
    return 0;
}

/* Public entry: master arm only, takes the cache lock. */
int32_t teleprompt_request_page_data(uint32_t page, uint8_t start_timer)
{
    if (display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER) {
        TP_LOG(4u, fn_request, 200u, req_not_master, 0x10400000u, req_not_master_c, page);
        return 0;
    }
    if (!page_data_lock()) {
        TP_LOG(1u, fn_request, 0xccu, req_lock_failed, 0x04400000u, req_lock_failed_c, page);
        return -1;
    }
    int32_t ret = request_page_data_locked(page, start_timer);
    semantic_page_data_unlock();
    return ret;
}

/* Preload range: [window_start - 5, window_start + 8] clipped to the document. */
void semantic_ensure_range(uint32_t *start, uint32_t *end)
{
    uint32_t window = g2_teleprompt_page_ctx.window_start;
    uint32_t total = g2_teleprompt_page_ctx.total_pages;
    *start = window < PRELOAD_BEFORE ? 0u : window - PRELOAD_BEFORE;
    *end = window + PRELOAD_AFTER;
    if (*end >= total)
        *end = total != 0u ? total - 1u : 0u;
}

uint8_t semantic_range_ready(void)
{
    uint32_t start, end;
    semantic_ensure_range(&start, &end);
    for (uint32_t page = start; page <= end; page++) {
        if (!semantic_slot_loaded(semantic_page_to_slot(page), page))
            return 0u;
    }
    return 1u;
}

uint8_t semantic_loading_timed_out(uint32_t slot, uint32_t page, uint32_t now)
{
    const teleprompt_page_slot_t *s = &g2_teleprompt_page_ctx.slot[slot];
    if (s->state == SLOT_REQUESTED && s->page.page_id == page && s->request_tick != 0u)
        return (now - s->request_tick > LOADING_TIMEOUT_TICKS - 1u) ? 1u : 0u;
    return 0u;
}

/* First page in [first, last] that is neither loaded nor still within its
 * loading timeout. */
uint8_t semantic_find_requestable(uint32_t first, uint32_t last, uint32_t now, uint32_t *out)
{
    for (uint32_t page = first; page <= last; page++) {
        uint32_t slot = semantic_page_to_slot(page);
        if (semantic_slot_loaded(slot, page))
            continue;
        const teleprompt_page_slot_t *s = &g2_teleprompt_page_ctx.slot[slot];
        if (s->state != SLOT_REQUESTED || s->page.page_id != page || semantic_loading_timed_out(slot, page, now)) {
            *out = page;
            return 1u;
        }
    }
    return 0u;
}

/* Visible window first, then the whole preload range. */
uint8_t semantic_find_next_request(uint32_t *out)
{
    uint32_t start, end;
    semantic_ensure_range(&start, &end);
    uint32_t first = g2_teleprompt_page_ctx.window_start;
    uint32_t last = first + PAGE_WINDOW_PAGES - 1u;
    if (last >= g2_teleprompt_page_ctx.total_pages)
        last = g2_teleprompt_page_ctx.total_pages - 1u;
    uint32_t now = osKernelGetTickCount();
    if (semantic_find_requestable(first, last, now, out))
        return 1u;
    return semantic_find_requestable(start, end, now, out);
}

void teleprompt_preload_timer_callback(void *argument)
{
    (void)argument;
    if (!page_data_lock()) {
        TP_LOG(1u, fn_timer_cb, 0x126u, cb_lock_failed, 0x04000000u, cb_lock_failed_c);
        return;
    }
    if (semantic_range_ready()) {
        TP_LOG(4u, fn_timer_cb, 299u, cb_complete, 0x10000000u, cb_complete_c);
        semantic_page_data_unlock();
        return;
    }
    uint32_t page = 0u;
    if (semantic_find_next_request(&page)) {
        TP_LOG(3u, fn_timer_cb, 0x132u, cb_retry, 0x0c400000u, cb_retry_c, page);
        semantic_page_data_unlock();
        (void)teleprompt_request_page_data(page, 1u);
        return;
    }
    if (osTimerStart(g2_teleprompt_preload_timer, PRELOAD_TIMER_TICKS) != 0)
        TP_LOG(2u, fn_timer_cb, 0x13au, cb_restart_failed, 0x08000000u, cb_restart_failed_c);
    semantic_page_data_unlock();
}

void semantic_preload_timer_stop(void)
{
    if (g2_teleprompt_preload_timer != NULL)
        (void)osTimerStop(g2_teleprompt_preload_timer);
}

void teleprompt_page_data_init(uint32_t start_page, uint32_t total_pages)
{
    teleprompt_page_ctx_t *ctx = &g2_teleprompt_page_ctx;

    if (total_pages == 0u || start_page >= total_pages) {
        TP_LOG(1u, fn_init, 0x14du, init_invalid, 0x04800000u, init_invalid_c, total_pages, start_page);
        return;
    }
    if (g2_teleprompt_page_mutex == NULL) {
        g2_teleprompt_page_mutex = osMutexNew(NULL);
        if (g2_teleprompt_page_mutex == NULL) {
            TP_LOG(1u, fn_init, 0x154u, init_mutex_failed, 0x04000000u, init_mutex_failed_c);
            return;
        }
    }
    if (!page_data_lock()) {
        TP_LOG(1u, fn_init, 0x15au, init_lock_failed, 0x04000000u, init_lock_failed_c);
        return;
    }
    (void)aeabi_memset_43c0e4(ctx, sizeof *ctx, 0);
    ctx->total_pages = total_pages;
    ctx->initialized = 1u;
    semantic_page_data_unlock();

    /* Keep one page of context above the start page. */
    uint32_t window = semantic_clamp_window_start(start_page != 0u ? start_page - 1u : 0u);
    TP_LOG(3u, fn_init, 0x165u, init_ok, 0x0cc00000u, init_ok_c, start_page, total_pages, window);
    teleprompt_page_data_set_window(window);
}

void teleprompt_page_data_deinit(void)
{
    if (g2_teleprompt_page_mutex == NULL) {
        TP_LOG(4u, fn_deinit, 0x16cu, deinit_skip, 0x10000000u, deinit_skip_c);
        return;
    }
    if (!page_data_lock()) {
        TP_LOG(1u, fn_deinit, 0x170u, deinit_lock_failed, 0x04000000u, deinit_lock_failed_c);
        return;
    }
    if (g2_teleprompt_page_ctx.initialized == 0u) {
        semantic_page_data_unlock();
        TP_LOG(4u, fn_deinit, 0x175u, deinit_skip, 0x10000000u, deinit_skip_c);
        return;
    }
    TP_LOG(3u, fn_deinit, 0x178u, deinit_begin, 0x0c000000u, deinit_begin_c);
    semantic_preload_timer_stop();
    if (g2_teleprompt_preload_timer != NULL) {
        (void)osTimerDelete(g2_teleprompt_preload_timer);
        g2_teleprompt_preload_timer = NULL;
    }
    (void)aeabi_memset_43c0e4(&g2_teleprompt_page_ctx, sizeof g2_teleprompt_page_ctx, 0);
    semantic_page_data_unlock();
    if (g2_teleprompt_page_mutex != NULL) {
        (void)osMutexDelete(g2_teleprompt_page_mutex);
        g2_teleprompt_page_mutex = NULL;
    }
    TP_LOG(3u, fn_deinit, 0x184u, deinit_done, 0x0c000000u, deinit_done_c);
}

/* Store an arriving page. Returns 1 when stored; posts loading-done (5) to
 * the controller the first time all pages of the current window are cached. */
uint8_t teleprompt_page_data_update(const g2_teleprompt_page_t *page)
{
    teleprompt_page_ctx_t *ctx = &g2_teleprompt_page_ctx;

    if (page == NULL) {
        TP_LOG(1u, fn_update, 0x18cu, update_null, 0x04000000u, update_null_c);
        return 0u;
    }
    if (!page_data_lock()) {
        TP_LOG(1u, fn_update, 400u, update_lock_failed, 0x04000000u, update_lock_failed_c);
        return 0u;
    }

    uint32_t id = page->page_id;
    if (id >= ctx->total_pages) {
        TP_LOG(1u, fn_update, 0x196u, invalid_page, 0x04800000u, invalid_page_c, id, ctx->total_pages - 1u);
        semantic_page_data_unlock();
        return 0u;
    }
    uint32_t slot = semantic_page_to_slot(id);
    if (semantic_slot_loaded(slot, id)) {
        TP_LOG(4u, fn_update, 0x19du, update_loaded, 0x10800000u, update_loaded_c, id, slot);
        semantic_page_data_unlock();
        return 0u;
    }

    (void)audio_queue_copy_bytes(&ctx->slot[slot].page, page, G2_TELEPROMPT_PAGE_SIZE);
    ctx->slot[slot].state = SLOT_LOADED;
    TP_LOG(3u, fn_update, 0x1a5u, update_ok, 0x0cc00000u, update_ok_c, id, slot, (uint32_t)page->text_size);

    uint8_t ready = 0u;
    uint32_t first = ctx->window_start;
    if (id >= first && id < first + PAGE_WINDOW_PAGES && ctx->window_ready == 0u) {
        ready = ctx->total_pages != 0u ? 1u : 0u;
        for (uint32_t p = first; ready && p < first + PAGE_WINDOW_PAGES && p < ctx->total_pages; p++) {
            if (!semantic_slot_loaded(semantic_page_to_slot(p), p))
                ready = 0u;
        }
        if (ready)
            ctx->window_ready = 1u;
    }
    semantic_page_data_unlock();

    if (ready) {
        TP_LOG(3u, fn_update, 0x1bcu, update_ready, 0x0c000000u, update_ready_c);
        (void)teleprompt_controller_post_589b68(TELEPROMPT_EVT_LOADING_DONE, 0u);
    }
    return 1u;
}

/* Copy of a cached page in a static buffer, NULL when not loaded. */
const g2_teleprompt_page_t *teleprompt_page_data_get(uint32_t page)
{
    if (!page_data_lock()) {
        TP_LOG(1u, fn_get, 0x1c8u, get_lock_failed, 0x04400000u, get_lock_failed_c, page);
        return NULL;
    }
    if (page >= g2_teleprompt_page_ctx.total_pages) {
        semantic_page_data_unlock();
        return NULL;
    }
    uint32_t slot = semantic_page_to_slot(page);
    if (!semantic_slot_loaded(slot, page)) {
        semantic_page_data_unlock();
        return NULL;
    }
    (void)audio_queue_copy_bytes(&g2_teleprompt_page_copy, &g2_teleprompt_page_ctx.slot[slot].page,
                                 G2_TELEPROMPT_PAGE_SIZE);
    semantic_page_data_unlock();
    return &g2_teleprompt_page_copy;
}

/* 1 when page lies inside the current preload range. */
uint8_t semantic_page_in_ensure_window(uint32_t page)
{
    if (!page_data_lock())
        return 0u;
    if (g2_teleprompt_page_ctx.total_pages == 0u || g2_teleprompt_page_ctx.window_set == 0u ||
        page >= g2_teleprompt_page_ctx.total_pages) {
        semantic_page_data_unlock();
        return 0u;
    }
    uint32_t start, end;
    semantic_ensure_range(&start, &end);
    uint8_t inside = (page < start || page > end) ? 0u : 1u;
    semantic_page_data_unlock();
    return inside;
}

/* Move the 4-page window; request missing window pages first, then the rest
 * of the preload range, and (re)arm the preload timer. */
void teleprompt_page_data_set_window(uint32_t window_start)
{
    teleprompt_page_ctx_t *ctx = &g2_teleprompt_page_ctx;

    if (!page_data_lock()) {
        TP_LOG(1u, fn_set_window, 500u, win_lock_failed, 0x04400000u, win_lock_failed_c, window_start);
        return;
    }
    if (ctx->total_pages == 0u) {
        semantic_page_data_unlock();
        return;
    }

    uint32_t effective = semantic_clamp_window_start(window_start);
    uint32_t now = osKernelGetTickCount();
    if (ctx->window_set != 0u && ctx->window_start == effective) {
        TP_LOG(3u, fn_set_window, 0x202u, win_unchanged, 0x0c800000u, win_unchanged_c, effective,
               now - ctx->window_tick);
        if (teleprompt_preload_timer_ensure_created() == 0)
            (void)osTimerStart(g2_teleprompt_preload_timer, PRELOAD_TIMER_TICKS);
        ctx->window_tick = now;
        semantic_page_data_unlock();
        return;
    }

    ctx->window_start = effective;
    ctx->window_set = 1u;
    ctx->window_tick = now;
    uint32_t start, end;
    semantic_ensure_range(&start, &end);
    TP_LOG(3u, fn_set_window, 0x212u, win_set, 0x0d000000u, win_set_c, window_start, ctx->window_start, start, end);

    uint32_t last = ctx->window_start + PAGE_WINDOW_PAGES - 1u;
    if (last >= ctx->total_pages)
        last = ctx->total_pages - 1u;

    uint32_t window_requests = 0u;
    for (uint32_t page = ctx->window_start; page <= last; page++) {
        if (!semantic_slot_loaded(semantic_page_to_slot(page), page)) {
            (void)request_page_data_locked(page, 0u);
            window_requests++;
        }
    }
    uint32_t preload_requests = 0u;
    for (uint32_t page = start; page <= end; page++) {
        if (page < ctx->window_start || page > last) {
            if (!semantic_slot_loaded(semantic_page_to_slot(page), page)) {
                (void)request_page_data_locked(page, 0u);
                preload_requests++;
            }
        }
    }

    if (teleprompt_preload_timer_ensure_created() == 0 &&
        osTimerStart(g2_teleprompt_preload_timer, PRELOAD_TIMER_TICKS) != 0)
        TP_LOG(2u, fn_set_window, 0x22du, win_timer_failed, 0x08000000u, win_timer_failed_c);
    TP_LOG(3u, fn_set_window, 0x230u, win_done, 0x0c800000u, win_done_c, window_requests, preload_requests);
    semantic_page_data_unlock();
}

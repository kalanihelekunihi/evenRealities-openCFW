/* Teleprompt FSM action handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_fsm.c.
 * Native 0x58d000..0x58d410 (page_data, ai_sync, scroll_sync, heartbeat);
 * literal pools 0x58d2d8..0x58d2f3 and 0x58d410..0x58d51b.
 *
 * Each handler takes the FSM control block (RAM 0x20109390) and the decoded
 * event payload, returns 0 when handled and -1 for a NULL payload, and posts
 * follow-up work to the teleprompt controller (0x589b68) as (event, arg).
 * Page/line pairs are packed as page * 10 + line for the controller. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t reserved_00[4];
    uint8_t mode;               /* +0x04 0 = AI-driven scrolling */
    uint8_t reserved_05[0x0b];
    uint32_t total_pages;       /* +0x10 */
    uint8_t reserved_14[0x1c];
    uint32_t ai_sync[3];        /* +0x30 last page/line/char from the app */
    uint8_t reserved_3c;
    uint8_t jump_pending;       /* +0x3d cleared by 0x58c882 */
    uint8_t reserved_3e[2];
    uint32_t jump_page;         /* +0x40 */
} g2_teleprompt_fsm_ctrl_t;
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, ai_sync) == 0x30, "ai_sync at +0x30");
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, jump_page) == 0x40, "jump_page at +0x40");

/* Teleprompt UI/page-window state (RAM 0x20073068). */
typedef struct {
    uint8_t reserved_00[0x18];
    uint32_t content;           /* +0x18 nonzero once a document is loaded */
    uint8_t reserved_1c[5];
    uint8_t busy;               /* +0x21 */
    uint8_t reserved_22[0x0a];
    uint32_t window_first_page; /* +0x2c first page of the 4-page window */
    uint8_t reserved_30[0x0c];
    uint32_t request_pending;   /* +0x3c */
} g2_teleprompt_ui_window_t;
_Static_assert(offsetof(g2_teleprompt_ui_window_t, request_pending) == 0x3c, "pending at +0x3c");

typedef struct { uint32_t page_id, line_id, char_id; } g2_teleprompt_ai_sync_t;
typedef struct { uint32_t page_id, line_id; } g2_teleprompt_scroll_sync_t;
typedef struct { uint32_t app_page_id, app_line_id, os_page_id, os_line_id; } g2_teleprompt_heartbeat_t;

enum {
    TELEPROMPT_UI_MAIN = 2u,
    TELEPROMPT_EVT_PAGE_REQUEST = 6u,
    TELEPROMPT_EVT_AI_SYNC = 0x10u,
    TELEPROMPT_EVT_SCROLL_SYNC = 0x11u,
};

extern g2_teleprompt_ui_window_t g2_teleprompt_ui_window; /* RAM 0x20073068 */

extern void teleprompt_page_data_update(const void *page_data);
extern uint32_t teleprompt_controller_post_589b68(uint8_t event, uint32_t arg);
extern uint8_t teleprompt_ui_state_get_5540b2(void);
extern const char *teleprompt_ui_state_name_5540bc(uint8_t state);
extern void teleprompt_fsm_jump_clear_58c882(void);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "teleprompt.fsm"; /* ROM 0x789730 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_fsm.c"; /* ROM 0x6fd8ec */

static const char fn_page_data[] = "teleprompt_action_page_data"; /* ROM 0x772bc8 */
static const char page_data_null[] = "page_data is NULL"; /* ROM 0x783e4c */
static const char page_data_null_short[] = "[teleprompt.fsm]page_data is NULL"; /* ROM 0x75ad1c */

static const char fn_ai_sync[] = "teleprompt_action_ai_sync"; /* ROM 0x772be4 */
static const char ai_sync_null[] = "ai_sync is NULL"; /* ROM 0x789760 */
static const char ai_sync_null_short[] = "[teleprompt.fsm]ai_sync is NULL"; /* ROM 0x765dd0 */
static const char ai_not_ai[] = "mode is not AI, skip ai sync"; /* ROM 0x765df0 */
static const char ai_not_ai_short[] = "[teleprompt.fsm]mode is not AI, skip ai sync"; /* ROM 0x739134 */
static const char ai_not_main[] = "current ui state is not main, skip ai sync"; /* ROM 0x744598 */
static const char ai_not_main_short[] = "[teleprompt.fsm]current ui state is not main, skip ai sync"; /* ROM 0x719468 */
static const char ai_sync_fmt[] = "ai_sync: page_id=%d, line_id=%d, char_id=%d"; /* ROM 0x7445c4 */
static const char ai_sync_fmt_short[] = "[teleprompt.fsm]ai_sync: page_id=%d, line_id=%d, char_id=%d"; /* ROM 0x7194a4 */

static const char fn_scroll_sync[] = "teleprompt_action_scroll_sync"; /* ROM 0x765e10 */
static const char scroll_null[] = "scroll_sync is NULL"; /* ROM 0x783e60 */
static const char scroll_null_short[] = "[teleprompt.fsm]scroll_sync is NULL"; /* ROM 0x75ad40 */
static const char scroll_fmt[] = "scroll_sync: page_id=%d, line_id=%d"; /* ROM 0x75ad64 */
static const char scroll_fmt_short[] = "[teleprompt.fsm]scroll_sync: page_id=%d, line_id=%d"; /* ROM 0x72e698 */

static const char fn_heartbeat[] = "teleprompt_action_heartbeat"; /* ROM 0x772c00 */
static const char hb_null[] = "heartbeat is NULL"; /* ROM 0x783e74 */
static const char hb_null_short[] = "[teleprompt.fsm]heartbeat is NULL"; /* ROM 0x75ad88 */
static const char hb_bad_state[] = "recv heartbeat, teleprompt ui state is invalid: [%d:%s]"; /* ROM 0x723d58 */
static const char hb_bad_state_short[] = "[teleprompt.fsm]recv heartbeat, teleprompt ui state is invalid: [%d:%s]"; /* ROM 0x6fd934 */
static const char hb_fmt[] = "heartbeat recv: app_page_id=%d, app_line_id=%d, os_page_id=%d, os_line_id=%d"; /* ROM 0x6f00d8 */
static const char hb_fmt_short[] = "[teleprompt.fsm]heartbeat recv: app_page_id=%d, app_line_id=%d, os_page_id=%d, os_line_id=%d"; /* ROM 0x6deb54 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* After new page text arrives, request the next page when the UI is on the
 * main screen with a loaded, idle document and either the arrived page is
 * the pending jump target or lies inside the current 4-page window. */
int32_t teleprompt_action_page_data_58d000(g2_teleprompt_fsm_ctrl_t *ctrl, const uint32_t *page_data)
{
    if (page_data == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_page_data, 0x127u, page_data_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, page_data_null_short, page_data_null_short);
        return -1;
    }

    teleprompt_page_data_update(page_data);
    uint32_t page = page_data[0];

    uint8_t ui_ready = 0u;
    if (teleprompt_ui_state_get_5540b2() == TELEPROMPT_UI_MAIN && g2_teleprompt_ui_window.content != 0u &&
        g2_teleprompt_ui_window.busy == 0u && g2_teleprompt_ui_window.request_pending == 0u)
        ui_ready = 1u;

    uint8_t is_jump = (ctrl->jump_pending != 0u && ctrl->jump_page == page) ? 1u : 0u;

    uint32_t first = g2_teleprompt_ui_window.window_first_page;
    uint8_t in_window = 0u;
    if (ctrl->total_pages != 0u && page < ctrl->total_pages && page >= first && page < first + 4u)
        in_window = 1u;

    if (ui_ready & (in_window | is_jump)) {
        if (is_jump)
            teleprompt_fsm_jump_clear_58c882();
        (void)teleprompt_controller_post_589b68(TELEPROMPT_EVT_PAGE_REQUEST, page);
    }
    return 0;
}

int32_t teleprompt_action_ai_sync_58d0d0(g2_teleprompt_fsm_ctrl_t *ctrl, const g2_teleprompt_ai_sync_t *sync)
{
    if (sync == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_ai_sync, 0x154u, ai_sync_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, ai_sync_null_short, ai_sync_null_short);
        return -1;
    }
    if (ctrl->mode != 0u) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_ai_sync, 0x159u, ai_not_ai);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, ai_not_ai_short, ai_not_ai_short);
        return 0;
    }
    if (teleprompt_ui_state_get_5540b2() != TELEPROMPT_UI_MAIN) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_ai_sync, 0x15fu, ai_not_main);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, ai_not_main_short, ai_not_main_short);
        return 0;
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_ai_sync, 0x163u, ai_sync_fmt,
                           sync->page_id, sync->line_id, sync->char_id);
    if (log_compressed_on())
        (void)compress_log_output(0x0cc00000u, ai_sync_fmt_short, ai_sync_fmt_short,
                                  sync->page_id, sync->line_id, sync->char_id);
    (void)audio_queue_copy_bytes(ctrl->ai_sync, sync, sizeof(*sync));
    (void)teleprompt_controller_post_589b68(TELEPROMPT_EVT_AI_SYNC, sync->page_id * 10u + sync->line_id);
    return 0;
}

int32_t teleprompt_action_scroll_sync_58d228(g2_teleprompt_fsm_ctrl_t *ctrl, const g2_teleprompt_scroll_sync_t *sync)
{
    (void)ctrl;
    if (sync == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_scroll_sync, 0x178u, scroll_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, scroll_null_short, scroll_null_short);
        return -1;
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_scroll_sync, 0x17cu, scroll_fmt,
                           sync->page_id, sync->line_id);
    if (log_compressed_on())
        (void)compress_log_output(0x0c800000u, scroll_fmt_short, scroll_fmt_short,
                                  sync->page_id, sync->line_id);
    (void)teleprompt_controller_post_589b68(TELEPROMPT_EVT_SCROLL_SYNC, sync->page_id * 10u + sync->line_id);
    return 0;
}

/* Heartbeats are only logged; UI states 0 and 3 reject them with -1. */
int32_t teleprompt_action_heartbeat_58d2f4(g2_teleprompt_fsm_ctrl_t *ctrl, const g2_teleprompt_heartbeat_t *hb)
{
    (void)ctrl;
    if (hb == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_heartbeat, 0x186u, hb_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, hb_null_short, hb_null_short);
        return -1;
    }
    uint8_t state = teleprompt_ui_state_get_5540b2();
    if (state == 0u || state == 3u) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_heartbeat, 0x18cu, hb_bad_state,
                               state, teleprompt_ui_state_name_5540bc(state));
        if (log_compressed_on())
            (void)compress_log_output(0x08800000u, hb_bad_state_short, hb_bad_state_short,
                                      state, teleprompt_ui_state_name_5540bc(state));
        return -1;
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_heartbeat, 400u, hb_fmt,
                           hb->app_page_id, hb->app_line_id, hb->os_page_id, hb->os_line_id);
    if (log_compressed_on())
        (void)compress_log_output(0x0d000000u, hb_fmt_short, hb_fmt_short,
                                  hb->app_page_id, hb->app_line_id, hb->os_page_id, hb->os_line_id);
    return 0;
}

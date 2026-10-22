/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_ui.c
 * Native rows 0x554080..0x5540ef and 0x554170..0x555513 (UI state machine,
 * init/deinit, scroll geometry, scrollbar, input handling, scroll sync);
 * literal pools 0x554b18..0x554b2b, 0x554c5c..0x554c67, 0x554d28..0x554d57,
 * 0x554e90..0x554e9b, 0x554ee4..0x554ee7, 0x554f28..0x554f4b,
 * 0x5551cc..0x5551ff and 0x5553c4..0x5553c7. Small helpers 0x5540f0..0x55416f
 * and the page/file-list actions from 0x555514 on belong to the same file.
 *
 * Text is laid out as pages of 10 lines, 28 px per line (280 px per page);
 * the content container holds a window of up to four pages starting at
 * window_first_page. Requests go to the teleprompt controller (0x589b68) as
 * (event, value) pairs; page/line pairs are packed page | line << 16. */
#include <stdint.h>
#include <stddef.h>

enum {
    TP_LINE_H = 0x1c,
    TP_PAGE_LINES = 10u,
    TP_PAGE_H = 0x118,
    TP_WINDOW_PAGES = 4u,
    TP_UI_STATES = 4u,
    TP_UI_EVENTS = 0x13u,
};

enum { TP_UI_STATE_FILE_LIST = 1u, TP_UI_STATE_MAIN = 2u };
enum { DEVICE_ROLE_MASTER = 1u };

enum {
    INPUT_CLICK = 0x0au,
    INPUT_SCROLL_UP = 0x44u,
    INPUT_SCROLL_DOWN = 0x45u,
    INPUT_CLOSE = 0x48u,
    INPUT_SCROLL_STOP = 0x4au,
};

/* Controller requests (teleprompt_controller_post_589b68 event codes). */
enum {
    TP_REQ_OPEN_FILE = 0x04u,
    TP_REQ_PAUSE = 0x07u,
    TP_REQ_RESUME = 0x08u,
    TP_REQ_EXIT = 0x09u,
    TP_REQ_SCROLL_TOP = 0x0bu,
    TP_REQ_SCROLL_UP = 0x0cu,
    TP_REQ_SCROLL_DOWN = 0x0du,
    TP_REQ_PREV_WINDOW = 0x0eu,
    TP_REQ_NEXT_WINDOW = 0x0fu,
    TP_REQ_ELAPSED = 0x12u,
};

enum {
    LV_OBJ_FLAG_SCROLLABLE = 0x10u,
    LV_ALIGN_TOP_MID = 2u,
    LV_SIZE_CONTENT = 0x3fffffff,
    LV_PART_SELECTED = 0x40000u,
};

/* Teleprompt FSM control block (RAM 0x20109390; stock also addresses it
 * through a second pool word 0x20109394 = +4). */
typedef struct {
    uint8_t reserved_00[4];
    uint8_t mode;               /* +0x04 0 = AI-driven scrolling */
    uint8_t reserved_05[0x0b];
    uint32_t total_pages;       /* +0x10 */
    uint32_t total_lines;       /* +0x14 */
    uint8_t reserved_18[0x10];
    uint32_t visible_lines;     /* +0x28 */
    uint8_t scroll_mode;        /* +0x2c 1 = page step, 2 = locked */
    uint8_t reserved_2d[3];
    uint32_t ai_page_id;        /* +0x30 */
    uint32_t ai_line_id;        /* +0x34 */
    uint32_t ai_char_id;        /* +0x38 */
} g2_teleprompt_fsm_ctrl_t;
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, total_pages) == 0x10, "total_pages at +0x10");
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, scroll_mode) == 0x2c, "scroll_mode at +0x2c");
_Static_assert(offsetof(g2_teleprompt_fsm_ctrl_t, ai_char_id) == 0x38, "ai_char_id at +0x38");

/* Teleprompt UI/page-window state (RAM 0x20073068, 0x48 bytes); field names
 * follow ui/a-54-teleprompt-ui/teleprompt_ui_internal.h. */
typedef struct {
    void *menu_page;            /* +0x00 file-list page */
    void *menu_list;            /* +0x04 */
    void *menu_selected;        /* +0x08 */
    int32_t menu_index;         /* +0x0c focused file index */
    void *root;                 /* +0x10 main page parent */
    void *title_bar;            /* +0x14 */
    void *content;              /* +0x18 page scroll container */
    void *scroll_bar;           /* +0x1c */
    uint8_t state;              /* +0x20 */
    uint8_t busy;               /* +0x21 */
    uint8_t reserved_22[2];
    uint32_t start_timestamp;   /* +0x24 RTC seconds at open */
    uint32_t sync_mode;         /* +0x28 sent with every scroll sync */
    uint32_t window_first_page; /* +0x2c */
    uint32_t current_page;      /* +0x30 */
    uint32_t current_line;      /* +0x34 */
    int32_t last_scroll_y;      /* +0x38 */
    uint32_t switching;         /* +0x3c window switch in progress */
    uint32_t paused;            /* +0x40 */
    uint8_t pause_hint;         /* +0x44 */
    uint8_t flag_45;            /* +0x45 queued page step: 0 none, 1 up, 2 down */
    uint8_t reserved_46[2];
} g2_teleprompt_ui_t;
_Static_assert(offsetof(g2_teleprompt_ui_t, switching) == 0x3c, "switching at +0x3c");
_Static_assert(sizeof(g2_teleprompt_ui_t) == 0x48, "stock memset size");

/* UI FSM table entry (ROM 0x6a9cf4, [4 states][19 events]). */
typedef struct {
    uint8_t next_state;
    uint8_t reserved_01[3];
    int32_t (*action)(uint8_t state, uint32_t arg);
} g2_teleprompt_ui_transition_t;
_Static_assert(sizeof(g2_teleprompt_ui_transition_t) == 8, "stock entry is 8 bytes");

typedef struct {
    uint32_t page_id;
    uint32_t line_id;
    uint32_t mode;
} g2_teleprompt_scroll_sync_t;

typedef struct {
    int32_t speed;  /* +0x00 */
    int32_t offset; /* +0x04 */
} g2_teleprompt_scroll_input_t;

extern g2_teleprompt_ui_t g2_teleprompt_ui_window;   /* RAM 0x20073068 */
extern g2_teleprompt_fsm_ctrl_t g2_teleprompt_fsm_ctrl;     /* RAM 0x20109390 */
extern void *g2_teleprompt_root_20074a7c;                   /* RAM 0x20074a7c */
extern int32_t g2_teleprompt_elapsed_20074a80;              /* RAM 0x20074a80 last reported seconds */
extern const char *const g2_teleprompt_ui_state_names_20003dec[TP_UI_STATES]; /* RAM 0x20003dec */
extern const char *const g2_teleprompt_ui_event_names_20003e00[TP_UI_EVENTS]; /* RAM 0x20003e00 */
extern const g2_teleprompt_ui_transition_t g2_teleprompt_ui_fsm_table_6a9cf4[TP_UI_STATES][TP_UI_EVENTS]; /* ROM 0x6a9cf4 */
extern const void *audio_uart_ring_primary_head_cell;       /* RAM 0x200746dc: active lv_font_t * */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t display_driver_uled_mode_45a568(void);         /* device role, 1 master */
extern uint32_t service_time_rtc_refresh(void);                 /* 0x44a1ea, epoch seconds */
extern void APP_PbTxEncodeScrollSync(const g2_teleprompt_scroll_sync_t *sync); /* 0x588c16 */
extern void system_close_page_factory_0046ae9c(uint32_t, uint32_t);
extern uint32_t teleprompt_controller_post_589b68(uint8_t event, uint32_t arg);
extern void teleprompt_timer_mgr_init_589152(void);
extern void teleprompt_timer_mgr_deinit_5891b6(void);
extern void teleprompt_timer_mgr_on_state_change_58930a(uint8_t from, uint8_t to);
extern void audio_terminal_list_anim_init_58966c(void);
extern void audio_terminal_ui_stop_voice_5896b4(void);
extern uint8_t teleprompt_file_request_busy_5897e0(void);
extern uint8_t teleprompt_is_current_file_58a83e(const void *obj);
extern void teleprompt_activity_tick_update_589cb4(void);
extern uint16_t teleprompt_ui_file_count_555710(void);
extern uint32_t teleprompt_ui_visible_lines_5540f0(void);      /* fsm_ctrl.visible_lines */
extern void teleprompt_ui_pause_notify_send_554102(uint8_t cmd);

extern void *audio_uart_page_43de82(void *parent);                              /* lv_obj_create */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                   /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);            /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);            /* lv_obj_set_size */
extern void audio_uart_page_43f6b8(void *obj, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                      /* lv_obj_get_height */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);          /* lv_obj_get_child */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                           /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);                   /* lv_obj_get_scroll_bottom */
extern void lv_obj_get_scroll_end_44e75e(void *obj, int32_t *point);           /* lv_point_t {x, y} */
extern uint32_t audio_uart_page_event_code_450286(const void *event);           /* lv_event_get_code */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                           /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);         /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);         /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);         /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);         /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);    /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);      /* bg_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);         /* border_width */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel);    /* text_color */
extern void audio_uart_page_44143e(void *obj, const void *font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44144c(void *obj, int32_t v, uint32_t sel);         /* text_line_space */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel);    /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);         /* radius */
extern uint32_t g2_log_module_length(const char *text); /* strlen 0x44a43c */
extern void *audio_uart_page_499416(void *parent);                              /* lv_label_create */
extern void audio_uart_page_49942e(void *label, const char *text);              /* lv_label_set_text */
extern void lv_label_set_text_selection_start_499716(void *label, uint32_t index);
extern void lv_label_set_text_selection_end_499752(void *label, uint32_t index);
extern void lv_label_set_recolor_499790(void *label, uint8_t enable);
extern const char *audio_uart_page_text_pointer_4997f8(const void *label);      /* lv_label_get_text */

static const char module_tag[] = "teleprompt.ui"; /* ROM 0x7897d0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_ui.c"; /* ROM 0x6fd97c */
static const char unknown_state[] = "UNKNOWN_STATE"; /* ROM 0x7897b0 */
static const char unknown_event[] = "UNKNOWN_EVENT"; /* ROM 0x7897c0 */

static const char fn_fsm[] = "teleprompt_ui_fsm_handler"; /* ROM 0x772e68 */
static const char ev_invalid[] = "UI event is invalid: %d"; /* ROM 0x77c574 */
static const char ev_invalid_short[] = "[teleprompt.ui]UI event is invalid: %d"; /* ROM 0x74f1cc */
static const char ev_fmt[] = "UI event [%d|%s]"; /* ROM 0x783ed8 */
static const char ev_fmt_short[] = "[teleprompt.ui]UI event [%d|%s]"; /* ROM 0x7660b0 */
static const char st_invalid[] = "UI current state is invalid: %d"; /* ROM 0x7660d0 */
static const char st_invalid_short[] = "[teleprompt.ui]UI current state is invalid: %d"; /* ROM 0x739464 */
static const char no_action[] = "UI current state[%d|%s] no match action for event[%d|%s]"; /* ROM 0x719774 */
static const char no_action_short[] = "[teleprompt.ui]UI current state[%d|%s] no match action for event[%d|%s]"; /* ROM 0x6fd9c4 */
static const char st_change[] = "UI state [%d|%s] -> [%d|%s]"; /* ROM 0x772e84 */
static const char st_change_short[] = "[teleprompt.ui]UI state [%d|%s] -> [%d|%s]"; /* ROM 0x74482c */
static const char act_fail[] = "UI transition action failed"; /* ROM 0x772ea0 */
static const char act_fail_short[] = "[teleprompt.ui]UI transition action failed"; /* ROM 0x744858 */

static const char fn_init[] = "teleprompt_ui_init"; /* ROM 0x783eec */
static const char parent_null[] = "parent_obj is NULL"; /* ROM 0x783f00 */
static const char parent_null_short[] = "[teleprompt.ui]parent_obj is NULL"; /* ROM 0x75af5c */
static const char init_done[] = "teleprompt UI initialized"; /* ROM 0x772ebc */
static const char init_done_short[] = "[teleprompt.ui]teleprompt UI initialized"; /* ROM 0x744884 */
static const char fn_deinit[] = "teleprompt_ui_deinit"; /* ROM 0x77c58c */
static const char deinit_done[] = "teleprompt UI deinitialized"; /* ROM 0x772ed8 */
static const char deinit_done_short[] = "[teleprompt.ui]teleprompt UI deinitialized"; /* ROM 0x7448b0 */

static const char fn_get_scroll_y[] = "common_ui_get_scroll_y"; /* ROM 0x77c5a4 */
static const char scroll_null[] = "scroll_obj is NULL"; /* ROM 0x783f14 */
static const char scroll_null_short[] = "[teleprompt.ui]scroll_obj is NULL"; /* ROM 0x75af80 */
static const char scroll_fmt[] = "scroll_offset=%d, speed=%d, current_y=%d, max=%d, target_y=%d"; /* ROM 0x70fe24 */
static const char scroll_fmt_short[] = "[teleprompt.ui]scroll_offset=%d, speed=%d, current_y=%d, max=%d, target_y=%d"; /* ROM 0x6f0268 */
static const char no_scroll[] = "scroll_max <= 0, can't scroll"; /* ROM 0x7660f0 */
static const char no_scroll_short[] = "[teleprompt.ui]scroll_max <= 0, can't scroll"; /* ROM 0x739494 */
static const char clamp_min[] = "Clamped target_y from %d to min 0"; /* ROM 0x75afa4 */
static const char clamp_min_short[] = "[teleprompt.ui]Clamped target_y from %d to min 0"; /* ROM 0x72e768 */
static const char clamp_max[] = "Clamped target_y from %d to max %d"; /* ROM 0x75afc8 */
static const char clamp_max_short[] = "[teleprompt.ui]Clamped target_y from %d to max %d"; /* ROM 0x72e79c */

static const char fn_by_page_line[] = "teleprompt_ui_get_scroll_y_by_page_line_id"; /* ROM 0x7448dc */
static const char fn_ai_page[] = "teleprompt_ui_ai_mode_page_process"; /* ROM 0x75afec */
static const char label_null[] = "page_label is NULL"; /* ROM 0x783f28 */
static const char label_null_short[] = "[teleprompt.ui]page_label is NULL"; /* ROM 0x75b010 */
static const char not_ai[] = "mode is not AI, skip ai mode page process"; /* ROM 0x744908 */
static const char not_ai_short[] = "[teleprompt.ui]mode is not AI, skip ai mode page process"; /* ROM 0x7197b0 */
static const char out_of_window[] = "page_id is out of window range: %d"; /* ROM 0x75b034 */
static const char out_of_window_short[] = "[teleprompt.ui]page_id is out of window range: %d"; /* ROM 0x72e7d0 */

static const char fn_bar_set[] = "teleprompt_ui_scroll_bar_set_value"; /* ROM 0x75b058 */
static const char bar_fmt[] = "scrollbar set: page_id=%d, line_id=%d, line_in_total=%d/%d, visible_lines=%d, scrollable_lines=%d, y_pos=%d/%d"; /* ROM 0x6d7660 */
static const char bar_fmt_short[] = "[teleprompt.ui]scrollbar set: page_id=%d, line_id=%d, line_in_total=%d/%d, visible_lines=%d, scrollable_lines=%d, y_pos=%d/%d"; /* ROM 0x6d5b58 */

static const char fn_end_check[] = "teleprompt_ui_scroll_container_scroll_end_check"; /* ROM 0x7394c4 */
static const char switching[] = "page switching is in progress, skip scroll end check"; /* ROM 0x723e38 */
static const char switching_short[] = "[teleprompt.ui]page switching is in progress, skip scroll end check"; /* ROM 0x7068c0 */
static const char check_fmt[] = "scroll check: idx=%d page=%d line=%d y=%d"; /* ROM 0x744934 */
static const char check_fmt_short[] = "[teleprompt.ui]scroll check: idx=%d page=%d line=%d y=%d"; /* ROM 0x7197ec */

static const char fn_sync_send[] = "teleprompt_ui_scroll_sync_send"; /* ROM 0x766110 */
static const char sync_fmt[] = "scroll sync send: page_id=%d, line_id=%d, mode=%d"; /* ROM 0x72e804 */
static const char sync_fmt_short[] = "[teleprompt.ui]scroll sync send: page_id=%d, line_id=%d, mode=%d"; /* ROM 0x706904 */
static const char empty_text[] = ""; /* ROM 0x555748 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* Non-inlined copy of LVGL lv_obj_set_style_pad_all. */
void lv_obj_set_style_pad_all_554080(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

uint8_t teleprompt_ui_state_get_5540b2(void)
{
    return g2_teleprompt_ui_window.state;
}

const char *teleprompt_ui_state_name_5540bc(uint8_t state)
{
    if (state < TP_UI_STATES)
        return g2_teleprompt_ui_state_names_20003dec[state];
    return unknown_state;
}

const char *teleprompt_ui_event_name_5540d6(uint8_t event)
{
    if (event < TP_UI_EVENTS)
        return g2_teleprompt_ui_event_names_20003e00[event];
    return unknown_event;
}

/* Runs the table action for (state, event); on success the state moves to
 * the entry's next state and the timer manager is told about the change. */
void teleprompt_ui_fsm_handler_554170(uint8_t event, uint32_t arg)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;

    if (event >= TP_UI_EVENTS) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_fsm, 0xf6u, ev_invalid, event);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, ev_invalid_short, ev_invalid_short, event);
        return;
    }
    if (event == 0x12u) {
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_fsm, 0xfbu, ev_fmt, 0x12u,
                               teleprompt_ui_event_name_5540d6(0x12u));
        if (log_compressed_on())
            (void)compress_log_output(0x10800000u, ev_fmt_short, ev_fmt_short, 0x12u,
                                      teleprompt_ui_event_name_5540d6(0x12u));
    } else {
        if (log_extended_on())
            audio_log_extended(3u, module_tag, source_file, fn_fsm, 0xfdu, ev_fmt, event,
                               teleprompt_ui_event_name_5540d6(event));
        if (log_compressed_on())
            (void)compress_log_output(0x0c800000u, ev_fmt_short, ev_fmt_short, event,
                                      teleprompt_ui_event_name_5540d6(event));
    }
    if (ui->state >= TP_UI_STATES) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_fsm, 0x102u, st_invalid, ui->state);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, st_invalid_short, st_invalid_short, ui->state);
        return;
    }
    const g2_teleprompt_ui_transition_t *entry = &g2_teleprompt_ui_fsm_table_6a9cf4[ui->state][event];
    if (entry->action == NULL) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_fsm, 0x10cu, no_action, ui->state,
                               teleprompt_ui_state_name_5540bc(ui->state), event,
                               teleprompt_ui_event_name_5540d6(event));
        if (log_compressed_on())
            (void)compress_log_output(0x09000000u, no_action_short, no_action_short, ui->state,
                                      teleprompt_ui_state_name_5540bc(ui->state), event,
                                      teleprompt_ui_event_name_5540d6(event));
        return;
    }
    if (entry->action(ui->state, arg) != 0) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_fsm, 0x121u, act_fail);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, act_fail_short, act_fail_short);
        return;
    }
    uint8_t from = ui->state;
    if (from != entry->next_state) {
        if (log_extended_on())
            audio_log_extended(3u, module_tag, source_file, fn_fsm, 0x11au, st_change, ui->state,
                               teleprompt_ui_state_name_5540bc(ui->state), entry->next_state,
                               teleprompt_ui_state_name_5540bc(entry->next_state));
        if (log_compressed_on())
            (void)compress_log_output(0x0d000000u, st_change_short, st_change_short, ui->state,
                                      teleprompt_ui_state_name_5540bc(ui->state), entry->next_state,
                                      teleprompt_ui_state_name_5540bc(entry->next_state));
    }
    ui->state = entry->next_state;
    teleprompt_timer_mgr_on_state_change_58930a(from, entry->next_state);
}

static void *create_plain_cont(void *parent)
{
    void *obj = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(obj, 0x240, 0x120);
    audio_uart_page_43f09a(obj, 0, 0);
    audio_uart_page_44129e(obj, 0u, 0u);
    audio_uart_page_44131c(obj, 0, 0u);
    return obj;
}

void teleprompt_ui_init_55448e(void *parent)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;

    if (parent == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_init, 0x12du, parent_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, parent_null_short, parent_null_short);
        return;
    }
    (void)aeabi_memset_43c0e4(ui, sizeof(*ui), 0);

    g2_teleprompt_root_20074a7c = create_plain_cont(parent);
    audio_uart_page_44146a(g2_teleprompt_root_20074a7c, 0, 0u);
    lv_obj_set_style_pad_all_554080(g2_teleprompt_root_20074a7c, 0, 0u);
    audio_uart_page_43dfa4(g2_teleprompt_root_20074a7c, 0x70u);

    ui->menu_page = create_plain_cont(g2_teleprompt_root_20074a7c);
    audio_uart_page_44146a(ui->menu_page, 0, 0u);
    lv_obj_set_style_pad_all_554080(ui->menu_page, 0, 0u);
    audio_uart_page_43dfa4(ui->menu_page, LV_OBJ_FLAG_SCROLLABLE);

    ui->root = create_plain_cont(g2_teleprompt_root_20074a7c);
    lv_obj_set_style_pad_all_554080(ui->root, 0, 0u);
    audio_uart_page_44146a(ui->root, 0, 0u);
    audio_uart_page_43dfa4(ui->root, LV_OBJ_FLAG_SCROLLABLE);

    teleprompt_timer_mgr_init_589152();
    audio_terminal_list_anim_init_58966c();
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_init, 0x158u, init_done);
    if (log_compressed_on())
        (void)compress_log_output(0x0c000000u, init_done_short, init_done_short);
}

void teleprompt_ui_deinit_55462e(void)
{
    teleprompt_timer_mgr_deinit_5891b6();
    audio_terminal_ui_stop_voice_5896b4();
    (void)aeabi_memset_43c0e4(&g2_teleprompt_ui_window, sizeof(g2_teleprompt_ui_window), 0);
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_deinit, 0x166u, deinit_done);
    if (log_compressed_on())
        (void)compress_log_output(0x0c000000u, deinit_done_short, deinit_done_short);
}

/* Master eye: reports elapsed reading time (s) whenever it changes. */
void teleprompt_ui_elapsed_time_update_55468c(void)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;

    if (display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER || ui->start_timestamp == 0u)
        return;
    int32_t elapsed = (int32_t)(service_time_rtc_refresh() - ui->start_timestamp);
    if (elapsed != g2_teleprompt_elapsed_20074a80) {
        g2_teleprompt_elapsed_20074a80 = elapsed;
        (void)teleprompt_controller_post_589b68(TP_REQ_ELAPSED, (uint32_t)elapsed);
    }
}

/* Target scroll y for an input offset: doubled above speed 100, rounded away
 * from the current position to a multiple of step, clamped to [0, max]. */
int32_t common_ui_get_scroll_y_5546be(void *obj, int32_t offset, int32_t speed, int32_t step)
{
    int32_t end[2];

    if (obj == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_get_scroll_y, 0x187u, scroll_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, scroll_null_short, scroll_null_short);
        return 0;
    }
    (void)aeabi_memset_43c0e4(end, sizeof(end), 0);
    lv_obj_get_scroll_end_44e75e(obj, end);
    int32_t current = end[1];
    int32_t max = audio_uart_lv_scroll_bottom_44e4bc(obj) + current;
    int32_t delta = offset;
    if (speed > 100)
        delta = offset << 1;
    int32_t target;
    if (delta >= 1)
        target = step * ((step + delta + current - 1) / step);
    else if (delta < 0)
        target = step * ((delta + current) / step);
    else
        target = current;

    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_get_scroll_y, 0x1a8u, scroll_fmt, offset, speed, current,
                           max, target);
    if (log_compressed_on())
        (void)compress_log_output(0x11400000u, scroll_fmt_short, scroll_fmt_short, offset, speed, current, max,
                                  target);
    if (max < 1) {
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_get_scroll_y, 0x1aau, no_scroll);
        if (log_compressed_on())
            (void)compress_log_output(0x10000000u, no_scroll_short, no_scroll_short);
        return 0;
    }
    if (target < 0) {
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_get_scroll_y, 0x1b0u, clamp_min, target);
        if (log_compressed_on())
            (void)compress_log_output(0x10400000u, clamp_min_short, clamp_min_short, target);
        return 0;
    }
    if (max < target) {
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_get_scroll_y, 0x1b5u, clamp_max, target, max);
        if (log_compressed_on())
            (void)compress_log_output(0x10800000u, clamp_max_short, clamp_max_short, target, max);
        return max;
    }
    return target;
}

/* Line-aligned target y, additionally limited to the document end (last
 * window) or to the last whole screen in page-step mode. */
int32_t teleprompt_ui_get_scroll_target_y_5548c4(void *obj, int32_t offset, int32_t speed)
{
    const g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;
    int32_t target = common_ui_get_scroll_y_5546be(obj, offset, speed, TP_LINE_H);
    int32_t height = audio_uart_lv_obj_height_43fdda(obj);
    int32_t limit = (int32_t)ctrl->total_lines * TP_LINE_H;

    limit = height < limit ? limit - height : 0;
    int last_window = !(ctrl->total_pages < TP_WINDOW_PAGES ||
                        g2_teleprompt_ui_window.window_first_page + TP_WINDOW_PAGES < ctrl->total_pages);
    if (last_window) {
        uint32_t rest = ctrl->total_lines % TP_PAGE_LINES;
        if (rest != 0u) {
            int32_t alt = (int32_t)(rest + 30u) * TP_LINE_H;
            alt = height < alt ? alt - height : 0;
            if (alt < limit)
                limit = alt;
        }
    } else if (ctrl->scroll_mode == 1u && ctrl->visible_lines != 0u && ctrl->total_lines != 0u) {
        limit = (int32_t)(ctrl->visible_lines * ((ctrl->total_lines - 1u) / ctrl->visible_lines)) * TP_LINE_H;
    }
    if (target <= limit)
        limit = target;
    return limit;
}

/* Maximum scroll y of the four-page window starting at first_page. */
int32_t teleprompt_ui_window_scroll_max_554968(void *obj, uint32_t first_page)
{
    const g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;

    if (obj == NULL)
        return 0;
    if (ctrl->total_pages == 0u)
        return 0;
    int32_t height = audio_uart_lv_obj_height_43fdda(obj);
    uint32_t last = first_page + 3u;
    if (ctrl->total_pages <= last)
        last = ctrl->total_pages - 1u;
    int32_t lines = 0;
    for (; first_page <= last; first_page++) {
        if (first_page == ctrl->total_pages - 1u && ctrl->total_lines % TP_PAGE_LINES != 0u)
            lines += (int32_t)(ctrl->total_lines % TP_PAGE_LINES);
        else
            lines += (int32_t)TP_PAGE_LINES;
    }
    return height < lines * TP_LINE_H ? lines * TP_LINE_H - height : 0;
}

uint8_t teleprompt_ui_line_in_window_5549e6(void *obj, uint32_t first_page, uint32_t page, int32_t line)
{
    if (page < first_page || first_page + TP_WINDOW_PAGES <= page)
        return 0u;
    int32_t y = ((int32_t)(page - first_page) * (int32_t)TP_PAGE_LINES + line) * TP_LINE_H;
    return teleprompt_ui_window_scroll_max_554968(obj, first_page) >= y ? 1u : 0u;
}

/* First page of a window that shows (page, line), preferring first_page. */
uint32_t teleprompt_ui_window_first_page_for_554a16(void *obj, uint32_t first_page, uint32_t page, int32_t line)
{
    const g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;

    if (ctrl->total_pages < 5u)
        return 0u;
    if (teleprompt_ui_line_in_window_5549e6(obj, first_page, page, line) != 0u)
        return first_page;
    first_page = page != 0u ? page - 1u : 0u;
    if (ctrl->total_pages < first_page + TP_WINDOW_PAGES)
        first_page = ctrl->total_pages - TP_WINDOW_PAGES;
    while (first_page < page && teleprompt_ui_line_in_window_5549e6(obj, first_page, page, line) == 0u)
        first_page++;
    return first_page;
}

int32_t teleprompt_ui_get_scroll_y_by_page_line_id_554a84(void *obj, uint32_t page, int32_t line, uint8_t one_line_up)
{
    const g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;

    if (obj == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_by_page_line, 0x23au, scroll_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, scroll_null_short, scroll_null_short);
        return 0;
    }
    int32_t max = teleprompt_ui_window_scroll_max_554968(obj, ui->window_first_page);
    if (page < ui->window_first_page)
        return 0;
    if (page > ui->window_first_page + 3u)
        return max;
    int32_t y = line * TP_LINE_H + (int32_t)(page - ui->window_first_page) * TP_PAGE_H;
    if (one_line_up != 0u)
        y -= TP_LINE_H;
    if (y > max)
        return max;
    return y < 0 ? 0 : y;
}

/* AI mode: highlight (selection) the text the speaker has already read. */
void teleprompt_ui_ai_mode_page_process_554b2c(void *label, uint32_t page)
{
    const g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;

    if (label == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_ai_page, 0x264u, label_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, label_null_short, label_null_short);
        return;
    }
    if (ctrl->mode != 0u) {
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_ai_page, 0x26cu, not_ai);
        if (log_compressed_on())
            (void)compress_log_output(0x10000000u, not_ai_short, not_ai_short);
        return;
    }
    if (page < ctrl->ai_page_id) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_ai_page, 0x271u, out_of_window, page);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, out_of_window_short, out_of_window_short, page);
        lv_label_set_text_selection_start_499716(label, 0u);
        lv_label_set_text_selection_end_499752(
            label, g2_log_module_length(audio_uart_page_text_pointer_4997f8(label)));
    } else if (page == ctrl->ai_page_id) {
        lv_label_set_text_selection_start_499716(label, 0u);
        lv_label_set_text_selection_end_499752(label, ctrl->ai_char_id);
    } else {
        lv_label_set_text_selection_start_499716(label, 0xffffu);
        lv_label_set_text_selection_end_499752(label, 0xffffu);
    }
}

/* 2 px wide track (one screen high) with a 20 px white thumb. */
void *teleprompt_ui_scroll_bar_create_554c68(void *parent)
{
    void *bar = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(bar, 2, (int32_t)teleprompt_ui_visible_lines_5540f0() * TP_LINE_H);
    audio_uart_page_44146a(bar, 6, 0u);
    audio_uart_page_44127e(bar, audio_uart_page_44104c(0x444444u), 0u);
    audio_uart_page_44129e(bar, 0x7fu, 0u);
    audio_uart_page_44131c(bar, 0, 0u);
    lv_obj_set_style_pad_all_554080(bar, 0, 0u);
    audio_uart_page_43dfa4(bar, LV_OBJ_FLAG_SCROLLABLE);

    void *thumb = audio_uart_page_43de82(bar);
    audio_uart_page_43f4c0(thumb, 2, 0x14);
    audio_uart_page_44146a(thumb, 6, 0u);
    audio_uart_page_44127e(thumb, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44129e(thumb, 0xffu, 0u);
    audio_uart_page_44131c(thumb, 0, 0u);
    lv_obj_set_style_pad_all_554080(thumb, 0, 0u);
    audio_uart_page_43dfa4(thumb, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f6b8(thumb, LV_ALIGN_TOP_MID, 0, 0);
    return bar;
}

void teleprompt_ui_scroll_bar_set_value_554d58(void *bar, int32_t page, int32_t line)
{
    const g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;
    const g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    void *thumb;

    if (bar == NULL || ctrl->total_lines == 0u || ui->content == NULL ||
        (thumb = audio_uart_lv_child_get_44dce2(bar, 0)) == NULL)
        return;
    uint32_t line_in_total = (uint32_t)(page * (int32_t)TP_PAGE_LINES + line);
    if (ctrl->total_lines <= line_in_total)
        line_in_total = ctrl->total_lines - 1u;
    int32_t visible = audio_uart_lv_obj_height_43fdda(ui->content) / TP_LINE_H;
    int32_t bar_h = audio_uart_lv_obj_height_43fdda(bar);
    int32_t thumb_h = audio_uart_lv_obj_height_43fdda(thumb);
    int32_t scrollable = (int32_t)ctrl->total_lines - visible;
    int32_t travel = bar_h - thumb_h;
    if (scrollable < 1) {
        scrollable = 1;
        line_in_total = 0u;
    }
    if (travel < 0)
        travel = 0;
    int32_t y = (int32_t)(((uint32_t)travel * line_in_total) / (uint32_t)scrollable);
    if (travel < y)
        y = travel;
    if (y < 0)
        y = 0;
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_bar_set, 0x2d9u, bar_fmt, page, line, line_in_total,
                           ctrl->total_lines, visible, scrollable, y, travel);
    if (log_compressed_on())
        (void)compress_log_output(0x12000000u, bar_fmt_short, bar_fmt_short, page, line, line_in_total,
                                  ctrl->total_lines, visible, scrollable, y, travel);
    audio_uart_page_43f6b8(thumb, LV_ALIGN_TOP_MID, 0, y);
}

void teleprompt_ui_scroll_to_top_554e9c(void)
{
    (void)teleprompt_controller_post_589b68(TP_REQ_SCROLL_TOP, 0u);
}

/* File list scroll-up check: 0xaa = already at the first file (bounce),
 * 1 = move, 0 = a file request is still running. */
uint32_t teleprompt_ui_file_list_prev_check_554ea8(void)
{
    (void)teleprompt_ui_file_count_555710();
    uint8_t busy = teleprompt_file_request_busy_5897e0();
    uint8_t current = teleprompt_is_current_file_58a83e(g2_teleprompt_ui_window.menu_list);
    if (busy == 0u && current == 0u && g2_teleprompt_ui_window.menu_index < 1)
        return 0xaau;
    return busy == 0u ? 1u : 0u;
}

uint32_t teleprompt_ui_file_list_next_check_554ee8(void)
{
    uint32_t count = teleprompt_ui_file_count_555710();
    uint8_t busy = teleprompt_file_request_busy_5897e0();
    uint8_t current = teleprompt_is_current_file_58a83e(g2_teleprompt_ui_window.menu_list);
    if (busy == 0u && current == 0u && count - 1u <= (uint32_t)g2_teleprompt_ui_window.menu_index)
        return 0xaau;
    return busy == 0u ? 1u : 0u;
}

void teleprompt_ui_file_list_input_554f4c(uint32_t code)
{
    uint32_t count = teleprompt_ui_file_count_555710();
    uint32_t r;

    if (code == INPUT_CLICK) {
        if (count != 0u)
            (void)teleprompt_controller_post_589b68(TP_REQ_OPEN_FILE, 0u);
    } else if (code == INPUT_SCROLL_UP) {
        if (count != 0u && (r = teleprompt_ui_file_list_prev_check_554ea8()) != 0u)
            (void)teleprompt_controller_post_589b68(TP_REQ_SCROLL_UP, r);
    } else if (code == INPUT_SCROLL_DOWN) {
        if (count != 0u && (r = teleprompt_ui_file_list_next_check_554ee8()) != 0u)
            (void)teleprompt_controller_post_589b68(TP_REQ_SCROLL_DOWN, r);
    } else if (code == INPUT_CLOSE) {
        system_close_page_factory_0046ae9c(1u, 6u);
    }
}

void teleprompt_ui_scroll_container_scroll_end_check_555200(uint8_t force);

static void scroll_or_request(g2_teleprompt_ui_t *ui, int32_t target, uint8_t request)
{
    if (target == audio_uart_lv_obj_y_44e498(ui->content))
        teleprompt_ui_scroll_container_scroll_end_check_555200(1u);
    else
        (void)teleprompt_controller_post_589b68(request, (uint32_t)target);
}

/* Main reading screen input. event + 0x10 points at {speed, offset}. */
void teleprompt_ui_main_input_554fae(uint32_t code, const uint8_t *event)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;
    uint8_t locked = (ctrl->scroll_mode == 2u || ui->paused != 0u) ? 1u : 0u;
    uint8_t page_step = ctrl->scroll_mode == 1u ? 1u : 0u;

    if (code == INPUT_CLICK) {
        if (ui->busy != 1u && ui->content != NULL) {
            if (ui->paused == 0u) {
                (void)teleprompt_controller_post_589b68(TP_REQ_PAUSE, 1u);
                teleprompt_ui_pause_notify_send_554102(2u);
            } else {
                (void)teleprompt_controller_post_589b68(TP_REQ_RESUME, 0u);
                teleprompt_ui_pause_notify_send_554102(3u);
            }
        }
    } else if (code == INPUT_SCROLL_UP || code == INPUT_SCROLL_DOWN) {
        if (locked != 0u)
            return;
        if (page_step != 0u) {
            ui->flag_45 = code == INPUT_SCROLL_UP ? 1u : 2u;
        } else if (ui->content != NULL && ui->busy == 0u) {
            const g2_teleprompt_scroll_input_t *in = *(const g2_teleprompt_scroll_input_t *const *)(event + 0x10);
            int32_t offset = code == INPUT_SCROLL_UP ? -in->offset : in->offset;
            int32_t target = teleprompt_ui_get_scroll_target_y_5548c4(ui->content, offset, in->speed);
            scroll_or_request(ui, target, code == INPUT_SCROLL_UP ? TP_REQ_SCROLL_UP : TP_REQ_SCROLL_DOWN);
        }
    } else if (code == INPUT_CLOSE) {
        system_close_page_factory_0046ae9c(1u, 6u);
    } else if (code == INPUT_SCROLL_STOP) {
        /* page-step mode applies the queued step when the gesture ends */
        if ((page_step & (locked ^ 1u)) != 0u && ui->content != NULL && ui->busy != 1u) {
            if (ui->flag_45 != 0u) {
                uint8_t down = ui->flag_45 != 1u ? 1u : 0u;
                int32_t lines = (int32_t)teleprompt_ui_visible_lines_5540f0();
                int32_t offset = lines * TP_LINE_H;
                ui->flag_45 = 0u;
                if (down == 0u)
                    offset = lines * -TP_LINE_H;
                int32_t target = teleprompt_ui_get_scroll_target_y_5548c4(ui->content, offset, 0);
                scroll_or_request(ui, target, down != 0u ? TP_REQ_SCROLL_DOWN : TP_REQ_SCROLL_UP);
            }
        } else {
            ui->flag_45 = 0u;
        }
    }
}

/* Input entry point; only the master eye handles input. */
void teleprompt_ui_input_handler_555178(uint32_t code, const uint8_t *event)
{
    uint32_t scratch[2];

    if (display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER)
        return;
    (void)aeabi_memset_43c0e4(scratch, sizeof(scratch), 0);
    teleprompt_activity_tick_update_589cb4();
    if (g2_teleprompt_ui_window.state == TP_UI_STATE_MAIN)
        teleprompt_ui_main_input_554fae(code, event);
    else if (g2_teleprompt_ui_window.state == TP_UI_STATE_FILE_LIST)
        teleprompt_ui_file_list_input_554f4c(code);
    else if (code == INPUT_CLOSE)
        (void)teleprompt_controller_post_589b68(TP_REQ_EXIT, 0u);
}

/* Derives page/line from the content scroll position, updates the scrollbar
 * and, when forced, asks for the previous/next window near its edges. */
void teleprompt_ui_scroll_container_scroll_end_check_555200(uint8_t force)
{
    g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    const g2_teleprompt_fsm_ctrl_t *ctrl = &g2_teleprompt_fsm_ctrl;

    if (ui->switching != 0u) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_end_check, 0x3c7u, switching);
        if (log_compressed_on())
            (void)compress_log_output(0x08000000u, switching_short, switching_short);
        return;
    }
    if (ui->content == NULL) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_end_check, 0x3cdu, scroll_null);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, scroll_null_short, scroll_null_short);
        return;
    }
    int32_t y = audio_uart_lv_obj_y_44e498(ui->content);
    if (force == 0u && (y == ui->last_scroll_y || y % TP_LINE_H != 0))
        return;
    uint32_t idx = (uint32_t)(y / TP_PAGE_H);
    if (idx > 3u)
        idx = 3u;
    ui->current_page = idx + ui->window_first_page;
    ui->current_line = ((uint32_t)y - idx * (uint32_t)TP_PAGE_H) / (uint32_t)TP_LINE_H;
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_end_check, 0x3e4u, check_fmt, idx, ui->current_page, ui->current_line,
                           y);
    if (log_compressed_on())
        (void)compress_log_output(0x11000000u, check_fmt_short, check_fmt_short, idx, ui->current_page, ui->current_line, y);
    ui->last_scroll_y = y;
    teleprompt_ui_scroll_bar_set_value_554d58(ui->scroll_bar, (int32_t)ui->current_page, (int32_t)ui->current_line);
    if (ctrl->total_pages > TP_WINDOW_PAGES && force != 0u) {
        uint32_t packed = (ui->current_page & 0xffffu) | (ui->current_line << 16);
        if (ui->current_page < ui->window_first_page + 1u && ui->current_page != 0u && ui->switching == 0u)
            (void)teleprompt_controller_post_589b68(TP_REQ_PREV_WINDOW, packed);
        else if (ui->window_first_page + 1u < ui->current_page &&
                 ui->window_first_page + TP_WINDOW_PAGES < ctrl->total_pages && ui->switching == 0u)
            (void)teleprompt_controller_post_589b68(TP_REQ_NEXT_WINDOW, packed);
    }
}

void teleprompt_ui_scroll_sync_send_5553c8(void)
{
    const g2_teleprompt_ui_t *ui = &g2_teleprompt_ui_window;
    g2_teleprompt_scroll_sync_t sync;

    if (display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER || ui->switching != 0u)
        return;
    (void)aeabi_memset_43c0e4(&sync, sizeof(sync), 0);
    sync.page_id = ui->current_page;
    sync.line_id = ui->current_line;
    sync.mode = ui->sync_mode;
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_sync_send, 0x415u, sync_fmt, sync.page_id, sync.line_id,
                           sync.mode);
    if (log_compressed_on())
        (void)compress_log_output(0x0cc00000u, sync_fmt_short, sync_fmt_short, sync.page_id, sync.line_id,
                                  sync.mode);
    APP_PbTxEncodeScrollSync(&sync);
}

/* LVGL event callback of the content container (codes 0x0e / 0x0f). */
void teleprompt_ui_scroll_event_cb_55545c(const void *event)
{
    uint32_t code = audio_uart_page_event_code_450286(event);
    if (code == 0x0cu)
        return;
    if (code == 0x0eu) {
        teleprompt_ui_scroll_container_scroll_end_check_555200(1u);
        teleprompt_ui_scroll_sync_send_5553c8();
    } else if (code == 0x0fu) {
        teleprompt_ui_scroll_container_scroll_end_check_555200(0u);
    }
}

/* One 280 px page label; read text is shown as a grey selection. */
void *teleprompt_ui_page_label_create_555486(void *parent)
{
    void *label = audio_uart_page_499416(parent);
    audio_uart_page_43f4c0(label, LV_SIZE_CONTENT, TP_PAGE_H);
    lv_label_set_recolor_499790(label, 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), LV_PART_SELECTED);
    audio_uart_page_44127e(label, audio_uart_page_44104c(0u), LV_PART_SELECTED);
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0u);
    /* line_height of the lv_font_t is the int32 at +0x0c */
    audio_uart_page_44144c(label, TP_LINE_H - ((const int32_t *)audio_uart_ring_primary_head_cell)[3], 0u);
    audio_uart_page_44145a(label, 1u, 0u);
    audio_uart_page_49942e(label, empty_text);
    return label;
}

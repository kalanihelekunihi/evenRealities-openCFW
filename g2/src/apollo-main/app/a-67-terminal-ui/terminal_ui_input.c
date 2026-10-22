/* Terminal UI input handling, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\terminal\terminal_ui.c
 * (terminal_input_event_handler; the filter 0x5e444c sits right after
 * terminal_request_display of terminal.c). Native rows 0x5e444c..0x5e4487,
 * 0x5e4b68..0x5e4c83, 0x5e4cb6..0x5e4f0f, 0x5e4f1a..0x5e4f53,
 * 0x5e72f4..0x5e7b0f; literal pool 0x5e7e0c..0x5e7e5b.
 *
 * Scroll/selection results are handed to the display thread packed into one
 * 32-bit request value; the small pack/unpack helpers below are the stock
 * out-of-line accessors of those bitfield records. Scroll positions snap to
 * 28-pixel text lines and fast flicks (speed > 100) double the step. */
#include <stddef.h>
#include <stdint.h>
#include "terminal_ui_a67.h"

typedef struct {
    int32_t speed; /* +0x0 */
    int32_t delta; /* +0x4 */
} g2_terminal_scroll_t;

typedef struct {
    uint8_t reserved[0x10];
    const g2_terminal_scroll_t *scroll; /* +0x10 */
} g2_terminal_input_event_t;

#define TERMINAL_LINE_HEIGHT 28
#define TERMINAL_FAST_SPEED 100
#define TERMINAL_SCROLL_THROTTLE_MS 300u
#define TERMINAL_SWITCH_SYNC_MS 5000u
#define TD_HOST_STATUS 0xa1d8u          /* audio_td_state_ptr_alias1() + 0xa1d8 */
#define TD_SESSION_QUERY_COUNT 0x406u   /* audio_td_session_struct_ptr() + 0x406 */
#define HOST_STATUS_STREAMING 2u
#define LV_OBJ_FLAG_HIDDEN 1u

/* Display requests (terminal_request_display event codes). */
enum {
    REQ_VOICE_START = 8, REQ_EXIT = 9, REQ_CONFIRM_YES = 0x0d, REQ_CONFIRM_BACK = 0x0e,
    REQ_STATE10_CLICK = 0x17, REQ_STATE10_BACK = 0x18, REQ_QUERY_CLICK = 0x19,
    REQ_INTERRUPT_CONFIRM = 0x1a, REQ_SESSION_LIST = 0x1b, REQ_SESSION_SELECT = 0x1d,
    REQ_SESSION_BACK = 0x1e, REQ_SCROLL_UP = 0x24, REQ_SCROLL_DOWN = 0x25,
    REQ_INTERRUPT_YES = 0x26, REQ_STATE3_BACK = 0x27,
};

extern uint32_t audio_terminal_request_display(uint8_t event, uint32_t value); /* 0x5e43d2 terminal_request_display */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568, 1 = master */
extern uint8_t *audio_td_state_ptr_alias1(void); /* 0x597344 td_state_ptr_alias1 */
extern uint8_t *audio_td_session_struct_ptr(void); /* 0x59731e td_session_struct_ptr */
extern uint8_t UX_GetSystemBLEStatus(void);
extern uint32_t osKernelGetTickCount(void);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flag); /* lv_obj_has_flag */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj); /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj); /* lv_obj_get_scroll_bottom */
extern void lv_obj_get_scroll_end_44e75e(void *obj, int32_t *point); /* lv_point_t {x, y} */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t audio_terminal_display_fallback_5ecafa(void); /* current session index, unsigned */
extern uint8_t teleprompt_file_request_busy_5897e0(void);
extern uint32_t audio_terminal_query_hit_count_5eb576(uint32_t threshold, int32_t y);
extern int16_t terminal_session_list_step_5ed0b8(int16_t row, uint32_t input); /* x-03 */
extern uint8_t terminal_session_row_kind_5ed152(int16_t row); /* x-03 */
extern uint32_t terminal_session_select_pack_5eca32(uint8_t kind, int16_t index);
extern uint8_t audio_terminal_output_active_2007502c; /* RAM 0x2007502c */
extern uint8_t audio_terminal_output_mode_2007502d;   /* RAM 0x2007502d */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "terminal.ui"; /* ROM 0x78c5d8 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c"; /* ROM 0x706d44 */
static const char handler_fn[] = "terminal_input_event_handler"; /* ROM 0x7664d0 */
static const char switch_sync[] = "ignore input during session switch content sync: code=%d state=%d"; /* ROM 0x706f20 */
static const char switch_sync_short[] = "[terminal.ui]ignore input during session switch content sync: code=%d state=%d"; /* ROM 0x6f05d8 */
static const char voice_bt[] = "ignore long press voice start: bluetooth disconnected"; /* ROM 0x724650 */
static const char voice_bt_short[] = "[terminal.ui]ignore long press voice start: bluetooth disconnected"; /* ROM 0x706f64 */
static const char voice_host[] = "ignore long press voice start: host status not ready (%d)"; /* ROM 0x719ef4 */
static const char voice_host_short[] = "[terminal.ui]ignore long press voice start: host status not ready (%d)"; /* ROM 0x6fe15c */
static const char agent_long[] = "input: agent processing long pressed -> interrupt confirm"; /* ROM 0x719f30 */
static const char agent_long_short[] = "[terminal.ui]input: agent processing long pressed -> interrupt confirm"; /* ROM 0x6fe1a4 */
static const char confirm_scroll[] = "input: interrupt confirm scroll code=%d request_sel=%lu"; /* ROM 0x724688 */
static const char confirm_scroll_short[] = "[terminal.ui]input: interrupt confirm scroll code=%d request_sel=%lu"; /* ROM 0x6fe1ec */
static const char confirm_yes[] = "input: interrupt confirm clicked yes"; /* ROM 0x74f8d4 */
static const char confirm_yes_short[] = "[terminal.ui]input: interrupt confirm clicked yes"; /* ROM 0x72ee50 */
static const char confirm_cancel[] = "input: interrupt confirm clicked cancel"; /* ROM 0x74f8fc */
static const char confirm_cancel_short[] = "[terminal.ui]input: interrupt confirm clicked cancel"; /* ROM 0x7246c0 */

#define LOG_COMPRESSED() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

static uint8_t scroll_request(int32_t code)
{
    return (uint8_t)(code == TERMINAL_KEY_SCROLL_UP ? REQ_SCROLL_UP : REQ_SCROLL_DOWN);
}

/* ---- Scroll target computation ------------------------------------------ */

/* Next scroll_y for obj: current end position plus delta (doubled for fast
 * flicks) snapped to a text line, limited to [0, scroll_y + scroll_bottom]. */
int32_t terminal_ui_scroll_target_5e4b68(void *obj, int32_t delta, int32_t speed)
{
    int32_t end[2];
    (void)aeabi_memset_43c0e4(end, sizeof end, 0);
    if (obj == NULL)
        return 0;
    lv_obj_get_scroll_end_44e75e(obj, end);
    int32_t y = end[1];
    int32_t max = audio_uart_lv_scroll_bottom_44e4bc(obj) + y;
    int32_t target = y;
    if (speed > TERMINAL_FAST_SPEED)
        delta <<= 1;
    if (delta >= 1)
        target = ((delta + y + (TERMINAL_LINE_HEIGHT - 1)) / TERMINAL_LINE_HEIGHT) * TERMINAL_LINE_HEIGHT;
    else if (delta < 0)
        target = ((delta + y) / TERMINAL_LINE_HEIGHT) * TERMINAL_LINE_HEIGHT;
    if (max < 1)
        return 0;
    if (target < 0)
        return 0;
    return max < target ? max : target;
}

/* Interrupt-confirm scrolling is throttled unless the content row is focused. */
uint8_t terminal_ui_confirm_scroll_throttled_5e4bde(const g2_terminal_ui_t *ui, int32_t code)
{
    (void)code;
    if (ui == NULL || ui->confirm_content == NULL)
        return 0u;
    return ui->confirm_sel == 2u ? 0u : 1u;
}

int32_t terminal_ui_confirm_scroll_target_5e4bfe(const g2_terminal_ui_t *ui, int32_t code,
                                                 const g2_terminal_scroll_t *scroll)
{
    if (ui == NULL || ui->confirm_content == NULL || scroll == NULL)
        return 0;
    int32_t delta = code == TERMINAL_KEY_SCROLL_UP ? -scroll->delta : scroll->delta;
    return terminal_ui_scroll_target_5e4b68(ui->confirm_content, delta, scroll->speed);
}

int32_t terminal_ui_agent_scroll_target_5e4c2c(const g2_terminal_ui_t *ui, int32_t code,
                                               const g2_terminal_scroll_t *scroll)
{
    if (ui == NULL || ui->agent_text == NULL || scroll == NULL)
        return 0;
    int32_t delta = code == TERMINAL_KEY_SCROLL_UP ? -scroll->delta : scroll->delta;
    return terminal_ui_scroll_target_5e4b68(ui->agent_text, delta, scroll->speed);
}

int32_t terminal_ui_query_scroll_target_5e4c56(const g2_terminal_ui_t *ui, int32_t code,
                                               const g2_terminal_scroll_t *scroll)
{
    if (ui == NULL || ui->query_panel == NULL || scroll == NULL)
        return 0;
    int32_t delta = code == TERMINAL_KEY_SCROLL_UP ? -scroll->delta : scroll->delta;
    return terminal_ui_scroll_target_5e4b68(ui->query_panel, delta, scroll->speed);
}

/* ---- Query scroll record: y[15:0] | idx[23:16] | browsing[30] | moved[31] -- */

uint32_t terminal_ui_query_scroll_pack_5e4cb6(uint16_t y, uint8_t moved, uint8_t browsing, uint8_t idx)
{
    uint32_t v = y;
    if (moved != 0u)
        v |= 0x80000000u;
    if (browsing != 0u)
        v |= 0x40000000u;
    return v | ((uint32_t)idx << 16);
}

uint16_t terminal_ui_query_scroll_y_5e4cd4(uint32_t v) { return (uint16_t)v; }
uint8_t terminal_ui_query_scroll_moved_5e4cd8(uint32_t v) { return (uint8_t)(v >> 31); }
uint32_t terminal_ui_query_scroll_browsing_5e4cde(uint32_t v) { return (v >> 30) & 1u; }
uint8_t terminal_ui_query_scroll_index_5e4ce6(uint32_t v) { return (uint8_t)(v >> 16); }

/* ---- Query click record: idx[7:0] | output_mode[15:8] | output_active[31] -- */

uint32_t terminal_ui_query_click_pack_5e4cec(uint8_t idx, uint8_t output_active, uint8_t output_mode)
{
    uint32_t v = (uint32_t)idx | ((uint32_t)output_mode << 8);
    if (output_active != 0u)
        v |= 0x80000000u;
    return v;
}

uint8_t terminal_ui_query_click_index_5e4d00(uint32_t v) { return (uint8_t)v; }
uint8_t terminal_ui_query_click_output_active_5e4d04(uint32_t v) { return (uint8_t)(v >> 31); }
uint8_t terminal_ui_query_click_output_mode_5e4d0a(uint32_t v) { return (uint8_t)(v >> 8); }

/* Scrolling up from the first option enters free browsing once the target is
 * above the option block (fewer than two option rows overlap the view, or the
 * first option is no longer visible). */
uint8_t terminal_ui_query_enter_browsing_5e4d10(const g2_terminal_ui_t *ui, int32_t code,
                                                uint8_t scroll_ok, int32_t target)
{
    if (ui == NULL || ui->query_panel == NULL)
        return 0u;
    if (code != TERMINAL_KEY_SCROLL_UP || ui->query_browsing != 0u || ui->query_idx != 0u ||
        scroll_ok == 0u)
        return 0u;
    int32_t y = audio_uart_lv_obj_y_44e498(ui->query_panel);
    if (y < 1 || target >= y)
        return 0u;
    return (uint8_t)(audio_terminal_query_hit_count_5eb576(2u, target) == 0u ||
                     terminal_ui_query_item_visible_5eb47a(ui->query_idx, target) == 0u);
}

/* Scrolling down while browsing returns to option 0 once two option rows are
 * in view, the limit is reached, or nothing can scroll. */
uint8_t terminal_ui_query_leave_browsing_5e4d7c(const g2_terminal_ui_t *ui, int32_t code,
                                                int32_t target, int32_t limit)
{
    if (ui == NULL || ui->query_panel == NULL)
        return 0u;
    if (code != TERMINAL_KEY_SCROLL_DOWN || ui->query_browsing == 0u)
        return 0u;
    int32_t y = audio_uart_lv_obj_y_44e498(ui->query_panel);
    int32_t max = audio_uart_lv_scroll_bottom_44e4bc(ui->query_panel) + y;
    if (target < limit && audio_terminal_query_hit_count_5eb576(2u, target) == 0u && max >= 1)
        return 0u;
    return 1u;
}

/* ---- Confirm scroll record: y[15:0] | sel0[30] | sel1[29] | sel2[28] | moved[31] */

uint32_t terminal_ui_confirm_scroll_pack_5e4dd8(uint16_t y, uint8_t moved, uint8_t to_yes,
                                                uint8_t to_cancel, uint8_t to_content)
{
    uint32_t v = y;
    if (moved != 0u)
        v |= 0x80000000u;
    if (to_yes != 0u)
        v |= 0x40000000u;
    if (to_cancel != 0u)
        v |= 0x20000000u;
    if (to_content != 0u)
        v |= 0x10000000u;
    return v;
}

uint16_t terminal_ui_confirm_scroll_y_5e4e06(uint32_t v) { return (uint16_t)v; }
uint8_t terminal_ui_confirm_scroll_moved_5e4e0a(uint32_t v) { return (uint8_t)(v >> 31); }

uint8_t terminal_ui_confirm_scroll_selection_5e4e10(uint32_t v, uint8_t current)
{
    if ((v & 0x10000000u) != 0u)
        return 2u;
    if ((v & 0x20000000u) != 0u)
        return 1u;
    if ((v & 0x40000000u) != 0u)
        return 0u;
    return current;
}

uint8_t terminal_ui_confirm_click_pack_5e4e2e(uint8_t sel) { return sel; }

/* Moves the interrupt-confirm focus between content (2), yes (0) and cancel (1). */
uint32_t terminal_ui_confirm_scroll_result_5e4e32(const g2_terminal_ui_t *ui, int32_t code, int32_t pos)
{
    uint8_t moved = 0u, to_yes = 0u, to_cancel = 0u, to_content = 0u;
    if (ui == NULL || ui->confirm_content == NULL)
        return terminal_ui_confirm_scroll_pack_5e4dd8((uint16_t)pos, 0u, 0u, 0u, 0u);
    if (code == TERMINAL_KEY_SCROLL_UP) {
        if (ui->confirm_sel == 0u) {
            if (audio_uart_lv_obj_y_44e498(ui->confirm_content) >= 1) {
                to_content = 1u;
                moved = 1u;
            }
        } else if (ui->confirm_sel == 1u) {
            to_yes = 1u;
        } else {
            moved = 1u;
        }
    } else if (code == TERMINAL_KEY_SCROLL_DOWN) {
        if (ui->confirm_sel == 0u) {
            to_cancel = 1u;
        } else if (ui->confirm_sel != 1u) {
            moved = 1u;
            int32_t y = audio_uart_lv_obj_y_44e498(ui->confirm_content);
            if (pos >= audio_uart_lv_scroll_bottom_44e4bc(ui->confirm_content) + y)
                to_yes = 1u;
        }
    }
    return terminal_ui_confirm_scroll_pack_5e4dd8((uint16_t)pos, moved, to_yes, to_cancel, to_content);
}

/* Interrupt-confirm option requested by a scroll: up = yes (0), down = cancel (1). */
uint8_t terminal_ui_interrupt_scroll_selection_5e4eec(int32_t code)
{
    uint8_t sel = 0u;
    if (code == TERMINAL_KEY_SCROLL_UP)
        sel = 0u;
    else if (code == TERMINAL_KEY_SCROLL_DOWN)
        sel = 1u;
    return sel;
}

/* ---- Agent scroll record: y[15:0] | at_end[31] ----------------------------- */

uint32_t terminal_ui_agent_scroll_pack_5e4f02(uint16_t y, uint8_t at_end)
{
    uint32_t v = y;
    if (at_end != 0u)
        v |= 0x80000000u;
    return v;
}

uint8_t terminal_ui_agent_scroll_at_end_5e4f1a(const g2_terminal_ui_t *ui, int32_t pos)
{
    if (ui == NULL || ui->agent_text == NULL)
        return 1u;
    int32_t y = audio_uart_lv_obj_y_44e498(ui->agent_text);
    int32_t max = audio_uart_lv_scroll_bottom_44e4bc(ui->agent_text) + y;
    if (max < 1)
        return 1u;
    return (uint8_t)(pos >= max);
}

/* ---- Input dispatch -------------------------------------------------------- */

/* Input is ignored for 5 s after a session-switch content sync started. */
uint8_t terminal_ui_session_switch_sync_pending_5e72f4(g2_terminal_ui_t *ui)
{
    if (ui->sync_tick == 0u)
        return 0u;
    if (osKernelGetTickCount() - ui->sync_tick < TERMINAL_SWITCH_SYNC_MS)
        return 1u;
    ui->sync_tick = 0u;
    return 0u;
}

static void agent_scroll(g2_terminal_ui_t *ui, int32_t code, const g2_terminal_scroll_t *scroll)
{
    int32_t pos = terminal_ui_agent_scroll_target_5e4c2c(ui, code, scroll);
    uint8_t at_end = terminal_ui_agent_scroll_at_end_5e4f1a(ui, pos);
    (void)audio_terminal_request_display(scroll_request(code),
                                         terminal_ui_agent_scroll_pack_5e4f02((uint16_t)pos, at_end));
}

static void query_scroll(g2_terminal_ui_t *ui, int32_t code, const g2_terminal_scroll_t *scroll)
{
    uint8_t force = 0u, scroll_ok = 0u, moved = 0u, count = 0u;
    int32_t limit = 0;
    const uint8_t *session = audio_td_session_struct_ptr();
    if (ui->query_panel == NULL || scroll == NULL)
        return;
    uint8_t browsing = ui->query_browsing;
    uint8_t idx = ui->query_idx;
    int32_t cur_y = audio_uart_lv_obj_y_44e498(ui->query_panel);
    if (session != NULL)
        count = (uint8_t)*(const uint16_t *)(const void *)(session + TD_SESSION_QUERY_COUNT);
    if (code == TERMINAL_KEY_SCROLL_UP && ui->query_browsing == 0u && ui->query_idx == 0u && cur_y >= 1)
        force = 1u;
    if (ui->query_browsing != 0u ||
        (code == TERMINAL_KEY_SCROLL_UP && ui->query_browsing == 0u && ui->query_idx == 0u && cur_y >= 1))
        scroll_ok = 1u;
    if (ui->query_browsing == 0u && force == 0u) {
        uint32_t now = osKernelGetTickCount();
        if (now - ui->scroll_tick < TERMINAL_SCROLL_THROTTLE_MS)
            return;
        ui->scroll_tick = now;
    }
    int32_t target = scroll_ok != 0u ? terminal_ui_query_scroll_target_5e4c56(ui, code, scroll) : 0;
    if (ui->query_browsing != 0u && code == TERMINAL_KEY_SCROLL_DOWN) {
        limit = terminal_ui_query_first_option_limit_5eb4f6();
        if (limit < target)
            target = limit;
    }
    uint8_t enter = terminal_ui_query_enter_browsing_5e4d10(ui, code, scroll_ok, target);
    uint8_t leave = terminal_ui_query_leave_browsing_5e4d7c(ui, code, target, limit);
    if (code == TERMINAL_KEY_SCROLL_UP) {
        if (ui->query_browsing != 0u) {
            moved = scroll_ok;
        } else if (ui->query_idx != 0u) {
            idx = (uint8_t)(ui->query_idx - 1u);
        } else if (cur_y >= 1 && scroll_ok != 0u && target < cur_y) {
            moved = 1u;
            browsing = enter;
        }
    } else if (ui->query_browsing != 0u) {
        moved = 1u;
        if (leave != 0u) {
            browsing = 0u;
            idx = 0u;
            target = terminal_ui_query_panel_get_selected_target_y_5eb646(idx, 1u);
        }
    } else if (count != 0u && (uint32_t)ui->query_idx < (uint32_t)count - 1u) {
        idx = (uint8_t)(ui->query_idx + 1u);
        moved = 1u;
        target = terminal_ui_query_panel_get_selected_target_y_5eb646(idx, 1u);
    }
    if (moved == 0u)
        target = cur_y;
    if (browsing == ui->query_browsing && idx == ui->query_idx && target == cur_y)
        return;
    (void)audio_terminal_request_display(
        scroll_request(code), terminal_ui_query_scroll_pack_5e4cb6((uint16_t)target, moved, browsing, idx));
}

void terminal_input_event_handler_5e7324(int32_t code, const g2_terminal_input_event_t *event)
{
    g2_terminal_ui_t *ui = G2_TERMINAL_UI;
    const uint8_t *td = audio_td_state_ptr_alias1();
    const g2_terminal_scroll_t *scroll = event->scroll;
    if (audio_uart_device_role_get() != 1u)
        return;
    if (terminal_ui_session_switch_sync_pending_5e72f4(ui) != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, handler_fn, 1933u, switch_sync, code, ui->state);
        if (LOG_COMPRESSED())
            (void)compress_log_output(0x8800000u, switch_sync_short, switch_sync_short, code, ui->state);
        return;
    }
    switch (ui->state) {
    case 2: /* idle / ready */
        if (code == TERMINAL_KEY_LONG_PRESS) {
            if (UX_GetSystemBLEStatus() == 0u) {
                if (audio_log_flags() & 2u)
                    audio_log_extended(2u, module_tag, source_file, handler_fn, 1941u, voice_bt);
                if (LOG_COMPRESSED())
                    (void)compress_log_output(0x8000000u, voice_bt_short, voice_bt_short);
            } else {
                uint8_t host = td[TD_HOST_STATUS];
                if (host == HOST_STATUS_STREAMING) {
                    (void)audio_terminal_request_display(REQ_VOICE_START, 0u);
                } else {
                    if (audio_log_flags() & 2u)
                        audio_log_extended(2u, module_tag, source_file, handler_fn, 1946u, voice_host, host);
                    if (LOG_COMPRESSED())
                        (void)compress_log_output(0x8400000u, voice_host_short, voice_host_short, host);
                }
            }
        } else if (code == TERMINAL_KEY_SCROLL_UP || code == TERMINAL_KEY_SCROLL_DOWN) {
            if (ui->agent_text != NULL && scroll != NULL)
                agent_scroll(ui, code, scroll);
        } else if (code == TERMINAL_KEY_DOUBLE_CLICK) {
            (void)audio_terminal_request_display(REQ_SESSION_LIST, audio_terminal_display_fallback_5ecafa());
        }
        break;
    case 3:
        if (code == TERMINAL_KEY_SCROLL_UP || code == TERMINAL_KEY_SCROLL_DOWN) {
            if (ui->agent_text != NULL && scroll != NULL &&
                audio_uart_lv_obj_has_flag_43e0e0(ui->agent_text, LV_OBJ_FLAG_HIDDEN) == 0u)
                agent_scroll(ui, code, scroll);
        } else if (code == TERMINAL_KEY_DOUBLE_CLICK) {
            (void)audio_terminal_request_display(REQ_STATE3_BACK, 0u);
        }
        break;
    case 4:
        if (code == TERMINAL_KEY_EXIT)
            (void)audio_terminal_request_display(REQ_EXIT, 0u);
        break;
    case 5:
        if (code == TERMINAL_KEY_DOUBLE_CLICK)
            (void)audio_terminal_request_display(REQ_CONFIRM_BACK, 0u);
        break;
    case 6: /* yes/cancel confirm with scrollable content */
        if (code == TERMINAL_KEY_DOUBLE_CLICK) {
            (void)audio_terminal_request_display(REQ_CONFIRM_BACK, 0u);
        } else if (code == TERMINAL_KEY_SCROLL_UP || code == TERMINAL_KEY_SCROLL_DOWN) {
            uint32_t now = osKernelGetTickCount();
            if (ui->confirm_content == NULL || scroll == NULL)
                return;
            if (terminal_ui_confirm_scroll_throttled_5e4bde(ui, code) != 0u) {
                if (now - ui->scroll_tick < TERMINAL_SCROLL_THROTTLE_MS)
                    return;
                ui->scroll_tick = now;
            }
            int32_t pos = terminal_ui_confirm_scroll_target_5e4bfe(ui, code, scroll);
            (void)audio_terminal_request_display(scroll_request(code),
                                                 terminal_ui_confirm_scroll_result_5e4e32(ui, code, pos));
        } else if (code == TERMINAL_KEY_CLICK) {
            if (ui->confirm_sel == 0u)
                (void)audio_terminal_request_display(REQ_CONFIRM_YES,
                                                     terminal_ui_confirm_click_pack_5e4e2e(ui->confirm_sel));
            else if (ui->confirm_sel == 1u)
                (void)audio_terminal_request_display(REQ_CONFIRM_BACK,
                                                     terminal_ui_confirm_click_pack_5e4e2e(ui->confirm_sel));
        }
        break;
    case 7: /* agent processing */
        if (code == TERMINAL_KEY_SCROLL_UP || code == TERMINAL_KEY_SCROLL_DOWN) {
            if (ui->agent_text != NULL && scroll != NULL)
                agent_scroll(ui, code, scroll);
        } else if (code == TERMINAL_KEY_LONG_PRESS) {
            if (audio_log_flags() & 2u)
                audio_log_extended(3u, module_tag, source_file, handler_fn, 2030u, agent_long);
            if (LOG_COMPRESSED())
                (void)compress_log_output(0xc000000u, agent_long_short, agent_long_short);
            (void)audio_terminal_request_display(REQ_INTERRUPT_CONFIRM, 0u);
        } else if (code == TERMINAL_KEY_DOUBLE_CLICK) {
            (void)audio_terminal_request_display(REQ_SESSION_LIST, audio_terminal_display_fallback_5ecafa());
        }
        break;
    case 8: /* interrupt confirm */
        if (code == TERMINAL_KEY_SCROLL_UP || code == TERMINAL_KEY_SCROLL_DOWN) {
            uint8_t sel = terminal_ui_interrupt_scroll_selection_5e4eec(code);
            if (audio_log_flags() & 2u)
                audio_log_extended(3u, module_tag, source_file, handler_fn, 2040u, confirm_scroll, code, sel);
            if (LOG_COMPRESSED())
                (void)compress_log_output(0xc800000u, confirm_scroll_short, confirm_scroll_short, code, sel);
            (void)audio_terminal_request_display(scroll_request(code), sel);
        } else if (code == TERMINAL_KEY_CLICK) {
            if (ui->confirm_sel == 0u) {
                if (audio_log_flags() & 2u)
                    audio_log_extended(3u, module_tag, source_file, handler_fn, 2044u, confirm_yes);
                if (LOG_COMPRESSED())
                    (void)compress_log_output(0xc000000u, confirm_yes_short, confirm_yes_short);
                (void)audio_terminal_request_display(REQ_INTERRUPT_YES,
                                                     terminal_ui_confirm_click_pack_5e4e2e(ui->confirm_sel));
            } else if (ui->confirm_sel == 1u) {
                if (audio_log_flags() & 2u)
                    audio_log_extended(3u, module_tag, source_file, handler_fn, 2047u, confirm_cancel);
                if (LOG_COMPRESSED())
                    (void)compress_log_output(0xc000000u, confirm_cancel_short, confirm_cancel_short);
                (void)audio_terminal_request_display(REQ_CONFIRM_BACK,
                                                     terminal_ui_confirm_click_pack_5e4e2e(ui->confirm_sel));
            }
        } else if (code == TERMINAL_KEY_DOUBLE_CLICK) {
            (void)audio_terminal_request_display(REQ_SESSION_LIST, audio_terminal_display_fallback_5ecafa());
        }
        break;
    case 9: /* query panel */
        if (code == TERMINAL_KEY_SCROLL_UP || code == TERMINAL_KEY_SCROLL_DOWN) {
            query_scroll(ui, code, scroll);
        } else if (code == TERMINAL_KEY_CLICK && ui->query_browsing == 0u) {
            (void)audio_terminal_request_display(
                REQ_QUERY_CLICK,
                terminal_ui_query_click_pack_5e4cec(ui->query_idx, audio_terminal_output_active_2007502c,
                                                    audio_terminal_output_mode_2007502d));
        }
        break;
    case 10:
        if (code == TERMINAL_KEY_CLICK)
            (void)audio_terminal_request_display(REQ_STATE10_CLICK, 0u);
        else if (code == TERMINAL_KEY_DOUBLE_CLICK)
            (void)audio_terminal_request_display(REQ_STATE10_BACK, 0u);
        break;
    case 11: /* session list */
        if (ui->list_locked != 0u || teleprompt_file_request_busy_5897e0() != 0u)
            return;
        if (code == TERMINAL_KEY_SCROLL_UP || code == TERMINAL_KEY_SCROLL_DOWN) {
            int16_t next = terminal_session_list_step_5ed0b8(ui->session_idx, code);
            if (next != ui->session_idx)
                (void)audio_terminal_request_display(scroll_request(code), (uint16_t)next);
        } else if (code == TERMINAL_KEY_CLICK) {
            int16_t idx = ui->session_idx;
            (void)audio_terminal_request_display(
                REQ_SESSION_SELECT,
                terminal_session_select_pack_5eca32(terminal_session_row_kind_5ed152(idx), idx));
        } else if (code == TERMINAL_KEY_DOUBLE_CLICK) {
            (void)audio_terminal_request_display(REQ_SESSION_BACK, 0u);
        }
        break;
    case 12:
        if (code == TERMINAL_KEY_LONG_PRESS) {
            uint8_t host = td[TD_HOST_STATUS];
            if (UX_GetSystemBLEStatus() != 0u && host == HOST_STATUS_STREAMING)
                (void)audio_terminal_request_display(REQ_VOICE_START, 0u);
        } else if (code == TERMINAL_KEY_DOUBLE_CLICK) {
            (void)audio_terminal_request_display(REQ_SESSION_LIST, audio_terminal_display_fallback_5ecafa());
        }
        break;
    default:
        break;
    }
}

/* Input-manager filter: the terminal page mirrors the scroll direction, then
 * forwards long press, click, scroll, double click and exit. Always consumes. */
uint8_t terminal_ui_input_filter(void *context, uint32_t source, int32_t code,
                                 const g2_terminal_input_event_t *event)
{
    (void)context;
    (void)source;
    if (code == TERMINAL_KEY_SCROLL_UP)
        code = TERMINAL_KEY_SCROLL_DOWN;
    else if (code == TERMINAL_KEY_SCROLL_DOWN)
        code = TERMINAL_KEY_SCROLL_UP;
    if (code == TERMINAL_KEY_LONG_PRESS || code == TERMINAL_KEY_CLICK || code == TERMINAL_KEY_SCROLL_UP ||
        code == TERMINAL_KEY_SCROLL_DOWN || code == TERMINAL_KEY_DOUBLE_CLICK || code == TERMINAL_KEY_EXIT) {
        terminal_input_event_handler_5e7324(code, event);
        return 1u;
    }
    return 1u;
}

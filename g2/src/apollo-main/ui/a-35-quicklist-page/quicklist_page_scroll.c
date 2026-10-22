/* QuickList page scrolling, loading row and queued-event dispatch, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c.
 * Native 0x4f6a10..0x4f6d19, 0x4f6d50..0x4f6d5d, 0x4f6d84..0x4f6e55,
 * 0x4f6e6c..0x4f6f95, 0x4f6f9c..0x4f6fab, 0x4f6fc4..0x4f715d,
 * 0x4f7180..0x4f73ed, 0x4f73f8..0x4f7475 and 0x4f7480..0x4f74f7; literal pools
 * in the gaps up to 0x4f8094.
 *
 * Input events reach the page through a 5-byte FIFO record
 * {code, b1, b2, b3, b4} that scroll_container_anim_ready_cb drains once the
 * running scroll animation has finished:
 *   0x0a click   shrink the border to the focused row / toggle its completion
 *   0x44 'D'     next row (requests more data near the bottom edge)
 *   0x45 'E'     previous row (requests more data near the top edge)
 *   0x46 'F'     ignored
 *   0x47 'G'     b1 = 0: rebuild the page, remembering the fade-in request
 *                {type b2, count b3|b4<<8}; b1 = 1: fade the loading row out
 *   0x48 'H'     back: expand the border to the full widget or close the page
 *   0x49 'I'     exit: fade the dashboard out */
#include "ui_quicklist_page_private.h"

#define QL_ANIM_TIME_MS 100
#define QL_SAME_Y_ANIM_TIME_MS 10
#define QL_LOADING_GAP 4

enum {
    QL_EVT_CLICK = 0x0au,
    QL_EVT_NEXT = 0x44u,
    QL_EVT_PREV = 0x45u,
    QL_EVT_IGNORED = 0x46u,
    QL_EVT_REFRESH = 0x47u,
    QL_EVT_BACK = 0x48u,
    QL_EVT_EXIT = 0x49u,
};

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern uint32_t osKernelGetTickCount(void);                     /* 0x4490cc */
extern int32_t ui_common_api_fn_00509dfa(void *fifo);           /* 0 = events pending */
extern int32_t ui_common_api_fn_00509e14(void *fifo, void *data, uint32_t len); /* fifo get */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);   /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flag); /* lv_obj_has_flag */
extern void audio_uart_page_43f142(void *obj, int32_t y);       /* lv_obj_set_y */
extern void audio_uart_page_43f66c(void *obj);                  /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_x_43fc70(void *obj);           /* lv_obj_get_x */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);           /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *obj);       /* lv_obj_get_width */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);      /* lv_obj_get_height */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* style opa */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);           /* lv_obj_get_scroll_y */
extern int32_t audio_uart_lv_scroll_bottom_44e4bc(void *obj);   /* lv_obj_get_scroll_bottom */
extern void audio_uart_lv_scroll_to_y_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */
extern void audio_uart_lv_anim_init_4503d6(g2_lv_anim_t *anim);
extern void *audio_uart_lv_anim_start_450408(const g2_lv_anim_t *anim);
extern void audio_uart_lv_anim_values_4506ce(g2_lv_anim_t *anim, int32_t start, int32_t end);
extern int32_t audio_uart_lv_anim_path_450672(const void *anim); /* lv_anim_path_ease_out */
extern void Dashboard_Fadeout_Anim_Start_4e8a90(void);

/* Same TU, reconstructed separately. */
extern void quicklist_loading_fade_4f74f8(uint8_t opa, uint32_t time_ms, g2_lv_anim_ready_cb_t ready_cb);
extern void quicklist_hide_loading_finish_4f7860(void *anim);
extern void quicklist_border_shrink_to_item_4f7ae4(int32_t index);
extern void quicklist_border_expand_to_full_4f7b84(void);
extern void quicklist_focus_move_to_4f7c10(int32_t index);
extern void quicklist_toggle_item_completion_4f7cb0(int32_t index);
extern void quicklist_offset_all_items_down_4f7f18(int32_t offset);
extern void quicklist_animate_focus_items_fade_in_4f7fa8(void);
extern void quicklist_loading_anim_start_4f82d0(void);
extern void Quicklist_ext_WidgetPage_Create_4fac74(void *parent);
extern void quicklist_ext_page_close_4faf20(void);
extern void quicklist_page_delete_4fb1a4(void *page, uint8_t stop_timer);

static const char module_tag[] = "quicklist.page"; /* ROM 0x789e40 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c"; /* ROM 0x6f7538 */

static const char fn_ready[] = "scroll_container_anim_ready_cb"; /* ROM 0x767990 */
static const char no_focus[] = "No focused item to toggle, border_state: %d, focus_item: %d"; /* ROM 0x71ad7c */
static const char no_focus_short[] =
    "[quicklist.page]No focused item to toggle, border_state: %d, focus_item: %d"; /* ROM 0x6f75d0 */
static const char unknown_event[] = "QuicklistWidget_event_handler: unknown event type: %d"; /* ROM 0x7259c8 */
static const char unknown_event_short[] =
    "[quicklist.page]QuicklistWidget_event_handler: unknown event type: %d"; /* ROM 0x6fee94 */
static const char fn_clamp[] = "quicklist_scroll_clamp_target_y"; /* ROM 0x7679b0 */
static const char clamp_min[] = "Clamped target_y from %d to min %d"; /* ROM 0x75c9a8 */
static const char clamp_min_short[] = "[quicklist.page]Clamped target_y from %d to min %d"; /* ROM 0x7302a0 */
static const char clamp_max[] = "Clamped target_y from %d to max %d"; /* ROM 0x75c9cc */
static const char clamp_max_short[] = "[quicklist.page]Clamped target_y from %d to max %d"; /* ROM 0x7302d4 */
static const char fn_scroll[] = "quicklist_scroll_content_with_anim_ready_cb"; /* ROM 0x7462fc */
static const char same_y[] = "target_y == current_scroll_y, animation time = %d"; /* ROM 0x730308 */
static const char same_y_short[] =
    "[quicklist.page]target_y == current_scroll_y, animation time = %d"; /* ROM 0x707ecc */
static const char scrolling[] = "Scrolling from %d to %d with %dms animation"; /* ROM 0x746328 */
static const char scrolling_short[] = "[quicklist.page]Scrolling from %d to %d with %dms animation"; /* ROM 0x71adb8 */
static const char fn_visible[] = "quicklist_ensure_item_visible"; /* ROM 0x7679d0 */
static const char visible[] = "Ensure item %d visible: scroll from %d to %d"; /* ROM 0x73ad24 */
static const char visible_short[] = "[quicklist.page]Ensure item %d visible: scroll from %d to %d"; /* ROM 0x7113e4 */
static const char fn_loading[] = "quicklist_show_loading_as_item"; /* ROM 0x7679f0 */
static const char loading_bottom[] = "Loading slides in from bottom outside view: %d -> %d"; /* ROM 0x725a00 */
static const char loading_bottom_short[] =
    "[quicklist.page]Loading slides in from bottom outside view: %d -> %d"; /* ROM 0x6feedc */
static const char loading_scroll[] = "Scroll to show loading: scroll from %d to %d"; /* ROM 0x73ad54 */
static const char loading_scroll_short[] =
    "[quicklist.page]Scroll to show loading: scroll from %d to %d"; /* ROM 0x711424 */
static const char loading_top[] = "Loading slides in from top with item offset: %d -> %d"; /* ROM 0x725a38 */
static const char loading_top_short[] =
    "[quicklist.page]Loading slides in from top with item offset: %d -> %d"; /* ROM 0x6fef24 */
static const char fn_hide_new[] = "quicklist_hide_loading_with_fade_ready_cb_to_new_item"; /* ROM 0x725a70 */
static const char pending_fade[] =
    "UI refreshed, executing pending fade-in animation: type=%d, count=%d"; /* ROM 0x6fef6c */
static const char pending_fade_short[] =
    "[quicklist.page]UI refreshed, executing pending fade-in animation: type=%d, count=%d"; /* ROM 0x6e5a30 */
static const char fn_hide[] = "quicklist_hide_loading_with_fade_ready_cb"; /* ROM 0x746354 */
static const char org_scroll[] = "org_quicklist_container_scroll_y = %d"; /* ROM 0x750cfc */
static const char org_scroll_short[] = "[quicklist.page]org_quicklist_container_scroll_y = %d"; /* ROM 0x725aa8 */

/* Click/next/prev while the border still spans the whole widget: shrink it
 * onto the focused row (row 0 when nothing is focused yet). */
static void shrink_border_to_focus(void)
{
    if (g2_quicklist_ui_data_2012a72c.count != 0u) {
        if (g2_quicklist_focus_index_200042c0 < 0)
            quicklist_border_shrink_to_item_4f7ae4(0);
        else
            quicklist_border_shrink_to_item_4f7ae4(g2_quicklist_focus_index_200042c0);
    }
}

void scroll_container_anim_ready_cb_4f6a10(void *anim)
{
    uint8_t event[10];
    uint8_t code;
    uint32_t data;

    (void)anim;
    g2_quicklist_anim_state_20074e20 = 0;
    if (g2_quicklist_event_fifo_20074e14 == NULL ||
        ui_common_api_fn_00509dfa(g2_quicklist_event_fifo_20074e14) != 0 ||
        g2_quicklist_page_active_20074e1c != 1)
        return;

    audio_uart_buffer_zero(event, sizeof event, 0u);
    audio_uart_buffer_zero(event, sizeof event, 0u);
    (void)ui_common_api_fn_00509e14(g2_quicklist_event_fifo_20074e14, event, 5u);
    code = event[0];
    data = (uint32_t)event[1] | ((uint32_t)event[2] << 8) | ((uint32_t)event[3] << 16) |
           ((uint32_t)event[4] << 24);

    switch (code) {
    case QL_EVT_CLICK:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL) {
            shrink_border_to_focus();
        } else if (g2_quicklist_border_state_2007503f == QL_BORDER_ITEM &&
                   g2_quicklist_focus_index_200042c0 >= 0) {
            quicklist_toggle_item_completion_4f7cb0(g2_quicklist_focus_index_200042c0);
        } else {
            QL_LOG(4u, fn_ready, 1618u, 0x10800000u, no_focus, no_focus_short,
                   g2_quicklist_border_state_2007503f, g2_quicklist_focus_index_200042c0);
        }
        break;
    case QL_EVT_NEXT:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL) {
            shrink_border_to_focus();
        } else if (g2_quicklist_border_state_2007503f == QL_BORDER_ITEM &&
                   g2_quicklist_focus_index_200042c0 >= 0) {
            if (quicklist_need_data_request_4f61a0(QL_REQUEST_DOWN) != 0u)
                quicklist_request_data_with_debounce_4f6282(QL_REQUEST_DOWN);
            quicklist_focus_move_to_4f7c10(g2_quicklist_focus_index_200042c0 + 1);
        }
        break;
    case QL_EVT_PREV:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL) {
            shrink_border_to_focus();
        } else if (g2_quicklist_border_state_2007503f == QL_BORDER_ITEM &&
                   g2_quicklist_focus_index_200042c0 >= 0) {
            if (quicklist_need_data_request_4f61a0(QL_REQUEST_UP) != 0u)
                quicklist_request_data_with_debounce_4f6282(QL_REQUEST_UP);
            quicklist_focus_move_to_4f7c10(g2_quicklist_focus_index_200042c0 - 1);
        }
        break;
    case QL_EVT_IGNORED:
        break;
    case QL_EVT_REFRESH:
        if ((uint8_t)data == 0u) {
            g2_quicklist_ui_data_t *const ui = &g2_quicklist_ui_data_2012a72c;
            ui->pending_fade_type = event[2];
            ui->pending_fade_count = (uint16_t)(event[3] | (event[4] << 8));
            if (g2_quicklist_page_active_20074e1c == 1 && g2_quicklist_event_fifo_20074e14 != NULL &&
                g2_quicklist_anim_state_20074e20 == 0 && g2_dashboard_focus_frame != NULL) {
                g2_quicklist_anim_state_20074e20 = 2;
                if (ui->count == 0u || g2_quicklist_border_state_2007503f == QL_BORDER_FULL)
                    quicklist_page_delete_4fb1a4(g2_dashboard_focus_frame, 1u);
                Quicklist_ext_WidgetPage_Create_4fac74(g2_dashboard_focus_frame);
                if (g2_quicklist_anim_state_20074e20 == 2)
                    g2_quicklist_anim_state_20074e20 = 0;
            }
            ui->pending_fade_type = 0u;
            ui->pending_fade_count = 0u;
        } else if ((uint8_t)data == 1u && g2_quicklist_page_active_20074e1c == 1 &&
                   g2_quicklist_event_fifo_20074e14 != NULL && g2_dashboard_focus_frame != NULL) {
            quicklist_loading_fade_4f74f8(0u, QL_ANIM_TIME_MS,
                                          quicklist_hide_loading_with_fade_ready_cb_4f7480);
        }
        break;
    case QL_EVT_BACK:
        if (g2_quicklist_border_state_2007503f == QL_BORDER_ITEM)
            quicklist_border_expand_to_full_4f7b84();
        else if (g2_quicklist_border_state_2007503f == QL_BORDER_FULL)
            quicklist_ext_page_close_4faf20();
        break;
    case QL_EVT_EXIT:
        Dashboard_Fadeout_Anim_Start_4e8a90();
        g2_quicklist_page_active_20074e1c = 0;
        g2_quicklist_anim_state_20074e20 = 0;
        break;
    default:
        QL_LOG(2u, fn_ready, 1667u, 0x08400000u, unknown_event, unknown_event_short, code);
        break;
    }
}

void quicklist_scroll_anim_exec_cb_4f6d50(void *obj, int32_t y)
{
    if (obj != NULL)
        audio_uart_lv_scroll_to_y_44ea04(obj, y, LV_ANIM_OFF);
}

int32_t quicklist_scroll_clamp_target_y_4f6d84(void *obj, int32_t target_y)
{
    int32_t max_y;

    if (obj == NULL)
        return target_y;
    max_y = audio_uart_lv_obj_y_44e498(obj);
    max_y = audio_uart_lv_scroll_bottom_44e4bc(obj) + max_y;
    if (target_y < 0) {
        QL_LOG(4u, fn_clamp, 1868u, 0x10800000u, clamp_min, clamp_min_short, target_y, 0);
        return 0;
    }
    if (target_y > max_y) {
        QL_LOG(4u, fn_clamp, 1872u, 0x10800000u, clamp_max, clamp_max_short, target_y, max_y);
        return max_y;
    }
    return target_y;
}

void quicklist_scroll_content_with_anim_ready_cb_4f6e6c(void *obj, int32_t target_y, int32_t time_ms,
                                                        g2_lv_anim_ready_cb_t ready_cb)
{
    g2_lv_anim_t a;
    int32_t current_y;

    if (obj == NULL)
        return;
    audio_uart_page_43f66c(g2_quicklist_container_20074e00);
    current_y = audio_uart_lv_obj_y_44e498(obj);
    if (target_y == current_y) {
        time_ms = QL_SAME_Y_ANIM_TIME_MS;
        QL_LOG(4u, fn_scroll, 1898u, 0x10400000u, same_y, same_y_short, QL_SAME_Y_ANIM_TIME_MS);
    }
    QL_LOG(4u, fn_scroll, 1902u, 0x10c00000u, scrolling, scrolling_short, current_y, target_y, time_ms);
    if (time_ms < 1) {
        audio_uart_lv_scroll_to_y_44ea04(obj, target_y, LV_ANIM_OFF);
        return;
    }
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = obj;
    audio_uart_lv_anim_values_4506ce(&a, current_y, target_y);
    a.duration = time_ms;
    a.exec_cb = quicklist_scroll_anim_exec_cb_4f6d50;
    if (ready_cb != NULL)
        a.completed_cb = ready_cb;
    a.path_cb = audio_uart_lv_anim_path_450672;
    g2_quicklist_anim_state_20074e20 = 1;
    (void)audio_uart_lv_anim_start_450408(&a);
}

void quicklist_scroll_content_with_anim_4f6f9c(void *obj, int32_t target_y, int32_t time_ms)
{
    if (obj != NULL)
        quicklist_scroll_content_with_anim_ready_cb_4f6e6c(obj, target_y, time_ms,
                                                           scroll_container_anim_ready_cb_4f6a10);
}

/* Row geometry; index < 0 selects the loading row. Defaults: 0, 0, 576x288. */
void quicklist_get_item_geometry_4f6fc4(int32_t index, int32_t *x, int32_t *y, int32_t *w, int32_t *h)
{
    void *obj;

    if (x != NULL)
        *x = 0;
    if (y != NULL)
        *y = 0;
    if (w != NULL)
        *w = QL_SCREEN_W;
    if (h != NULL)
        *h = QL_SCREEN_H;
    if (index < 0) {
        obj = g2_quicklist_loading_20074e08;
        if (obj == NULL)
            return;
    } else {
        if ((uint32_t)index >= QL_MAX_ITEMS || g2_quicklist_rows_2006e370[index].obj == NULL)
            return;
        obj = g2_quicklist_rows_2006e370[index].obj;
    }
    if (x != NULL)
        *x = audio_uart_lv_obj_x_43fc70(obj);
    if (y != NULL)
        *y = audio_uart_lv_obj_y_43fce0(obj);
    if (w != NULL)
        *w = audio_uart_lv_obj_width_43fd9e(obj);
    if (h != NULL)
        *h = audio_uart_lv_obj_height_43fdda(obj);
}

void quicklist_ensure_item_visible_4f70a4(int32_t index)
{
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    int32_t view_h;
    int32_t scroll_y;
    int32_t target_y;

    if (g2_quicklist_container_20074e00 == NULL)
        return;
    quicklist_get_item_geometry_4f6fc4(index, &x, &y, &w, &h);
    view_h = audio_uart_lv_obj_height_43fdda(g2_quicklist_container_20074e00);
    scroll_y = audio_uart_lv_obj_y_44e498(g2_quicklist_container_20074e00);
    target_y = scroll_y;
    if (y - scroll_y < 0)
        target_y = y;
    else if (view_h < h + (y - scroll_y))
        target_y = h + y - view_h;
    target_y = quicklist_scroll_clamp_target_y_4f6d84(g2_quicklist_container_20074e00, target_y);
    if (target_y == scroll_y)
        return;
    audio_uart_lv_scroll_to_y_44ea04(g2_quicklist_container_20074e00, target_y, LV_ANIM_OFF);
    QL_LOG(4u, fn_visible, 2019u, 0x10c00000u, visible, visible_short, index, scroll_y, target_y);
}

void quicklist_show_loading_as_item_4f7180(uint8_t from_bottom)
{
    g2_lv_anim_t a;
    int32_t view_h;
    int32_t loading_h;
    int32_t scroll_y;

    if (g2_quicklist_loading_20074e08 == NULL ||
        audio_uart_lv_obj_has_flag_43e0e0(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN) == 0u)
        return;

    g2_quicklist_loading_tick_200741a0 = osKernelGetTickCount();
    g2_quicklist_loading_shown_20075040 = 1u;
    audio_uart_page_43dfa4(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN);
    audio_uart_display_audio_reset_441488(g2_quicklist_loading_20074e08, 0xffu, 0u);
    quicklist_loading_anim_start_4f82d0();
    view_h = audio_uart_lv_obj_height_43fdda(g2_quicklist_container_20074e00);
    loading_h = audio_uart_lv_obj_height_43fdda(g2_quicklist_loading_20074e08);
    scroll_y = audio_uart_lv_obj_y_44e498(g2_quicklist_container_20074e00);
    g2_quicklist_org_scroll_y_20074e24 = scroll_y;

    if (from_bottom != 0u) {
        int32_t last_y = 0;
        int32_t last_h = 0;
        int32_t bottom;
        int32_t delta;

        if (g2_quicklist_ui_data_2012a72c.count != 0u)
            quicklist_get_item_geometry_4f6fc4((int32_t)g2_quicklist_ui_data_2012a72c.count - 1, NULL,
                                               &last_y, NULL, &last_h);
        bottom = last_h + last_y + QL_LOADING_GAP;
        delta = bottom - scroll_y;
        if (!(view_h < loading_h + delta) && delta >= 0) {
            /* Room left below the last row: slide the loading row up from the bottom edge. */
            audio_uart_page_43f142(g2_quicklist_loading_20074e08, view_h);
            audio_uart_lv_anim_init_4503d6(&a);
            a.var = g2_quicklist_loading_20074e08;
            audio_uart_lv_anim_values_4506ce(&a, view_h, view_h - loading_h);
            a.duration = QL_ANIM_TIME_MS;
            a.exec_cb = audio_uart_page_43f142;
            a.completed_cb = scroll_container_anim_ready_cb_4f6a10;
            (void)audio_uart_lv_anim_start_450408(&a);
            QL_LOG(4u, fn_loading, 2123u, 0x10800000u, loading_bottom, loading_bottom_short, view_h,
                   view_h - loading_h);
        } else {
            const int32_t target_y = loading_h + bottom - view_h;
            audio_uart_page_43f142(g2_quicklist_loading_20074e08, bottom);
            quicklist_scroll_content_with_anim_4f6f9c(g2_quicklist_container_20074e00, target_y,
                                                      QL_ANIM_TIME_MS);
            QL_LOG(4u, fn_loading, 2134u, 0x10800000u, loading_scroll, loading_scroll_short, bottom,
                   target_y);
        }
    } else {
        int32_t first_y = 0;
        int32_t offset;

        if (g2_quicklist_ui_data_2012a72c.count != 0u && g2_quicklist_rows_2006e370[0].obj != NULL)
            first_y = audio_uart_lv_obj_y_43fce0(g2_quicklist_rows_2006e370[0].obj);
        offset = loading_h + QL_LOADING_GAP + first_y;
        audio_uart_page_43f142(g2_quicklist_loading_20074e08, 0);
        quicklist_offset_all_items_down_4f7f18(offset);
        g2_quicklist_org_scroll_y_20074e24 = offset;
        audio_uart_lv_scroll_to_y_44ea04(g2_quicklist_container_20074e00, offset, LV_ANIM_OFF);
        quicklist_scroll_content_with_anim_4f6f9c(g2_quicklist_container_20074e00, 0, QL_ANIM_TIME_MS);
        QL_LOG(4u, fn_loading, 2190u, 0x10800000u, loading_top, loading_top_short, first_y, offset);
    }
}

void quicklist_loading_opa_exec_cb_4f73f8(void *obj, int32_t opa)
{
    if (obj != NULL)
        audio_uart_display_audio_reset_441488(obj, (uint8_t)opa, 0u);
}

void quicklist_hide_loading_with_fade_ready_cb_to_new_item_4f7408(void *anim)
{
    const g2_quicklist_ui_data_t *const ui = &g2_quicklist_ui_data_2012a72c;

    (void)anim;
    if (ui->pending_fade_type == 0u || ui->pending_fade_count == 0u)
        return;
    QL_LOG(4u, fn_hide_new, 2219u, 0x10800000u, pending_fade, pending_fade_short, ui->pending_fade_type,
           ui->pending_fade_count);
    quicklist_animate_focus_items_fade_in_4f7fa8();
}

void quicklist_hide_loading_with_fade_ready_cb_4f7480(void *anim)
{
    QL_LOG(4u, fn_hide, 2236u, 0x10400000u, org_scroll, org_scroll_short, g2_quicklist_org_scroll_y_20074e24);
    if (g2_quicklist_org_scroll_y_20074e24 != 0)
        quicklist_scroll_content_with_anim_ready_cb_4f6e6c(g2_quicklist_container_20074e00,
                                                           g2_quicklist_org_scroll_y_20074e24,
                                                           QL_ANIM_TIME_MS,
                                                           quicklist_hide_loading_finish_4f7860);
    else
        quicklist_hide_loading_finish_4f7860(anim);
}

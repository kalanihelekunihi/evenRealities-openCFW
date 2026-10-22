/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c
 * (log tag "quicklist.page"), expanded-page update tail. Native 0x4F9AFC..0x4FB1BE
 * with literal pools 0x4F9BD8..0x4F9BF7, 0x4F9D78..0x4F9D83, 0x4F9F0C..0x4F9F13,
 * 0x4FA04C..0x4FA057, 0x4FA3F0..0x4FA403, 0x4FA704..0x4FA72B, 0x4FAA2C..0x4FAA43,
 * 0x4FAB04..0x4FAB17, 0x4FAC3C..0x4FAC73, 0x4FAF18..0x4FAF1F, 0x4FAF84..0x4FAF9B,
 * 0x4FB078..0x4FB08B, 0x4FB0E4..0x4FB1A3.
 *
 * The expanded QuickList page is a scrolling list (RAM 0x20074e00) of at most
 * 40 items (item objects at RAM 0x2006e370, 16 bytes each) with a focus border
 * (RAM 0x20074e04) and a "loading" row (RAM 0x20074e08). When the phone pushes
 * a batch, the record at RAM 0x2012a72c carries the batch size (+0x2e48) and
 * the operation (+0x2e4e): 1 full replace, 2 ADD_UP (older items prepended),
 * 3 ADD_DOWN (newer items appended), 4 modify in place. The handlers rebuild
 * the list and restore the scroll offset so the focused item (or the loading
 * row) stays where it was on screen. Items beyond 40 are dropped from the far
 * end. LVGL 9.3: 0x10000 selector = LV_PART_SCROLLBAR, flag 0x10 SCROLLABLE. */
#include <stddef.h>
#include <stdint.h>

#define QL_MAX_ITEMS           40   /* 0x28 */
#define QL_ITEM_GAP            4    /* row gap added to each item height */
#define QL_SCREEN_W            576  /* 0x240 */
#define QL_SCREEN_H            288  /* 0x120 */
#define QL_LIST_H              272  /* 0x110 */
#define QL_FOCUS_LOADING_UP    (-2) /* focus on the "loading older" row */
#define QL_FOCUS_LOADING_DOWN  (-1)

#define QL_OP_FULL      1u
#define QL_OP_ADD_UP    2u
#define QL_OP_ADD_DOWN  3u
#define QL_OP_MODIFY    4u

#define LV_OBJ_FLAG_HIDDEN      0x01u
#define LV_OBJ_FLAG_SCROLLABLE  0x10u
#define LV_PART_SCROLLBAR       0x10000u
#define LV_DIR_VER              0x0cu
#define LV_SCROLLBAR_MODE_OFF   0u
#define LV_SCROLLBAR_MODE_AUTO  3u
#define LV_ANIM_OFF             0u

/* QuickList data record (RAM 0x2012a72c; same layout as g2_quicklist_data_view_t in
 * a-35 ui_quicklist_page_private.h: 40 items of 0x128 bytes at +0x8). Only the
 * fields used here are named; "focused"/"completed" are fields of items[0]. */
typedef struct {
    uint16_t count;                 /* +0x0000 items currently shown */
    uint8_t reserved0[0x112];
    uint32_t focused;               /* +0x0114 items[0].uid, synced to the app as "focused" */
    uint8_t reserved1[0x11];
    uint8_t completed;              /* +0x0129 items[0] +0x121 */
    uint8_t reserved2[0x2e48 - 0x12a];
    uint16_t incoming;              /* +0x2e48 items in the received batch (pending_fade_count) */
    uint8_t reserved3[4];
    uint8_t operation;              /* +0x2e4e QL_OP_* (pending_fade_type) */
} g2_quicklist_data_view_t;
_Static_assert(offsetof(g2_quicklist_data_view_t, focused) == 0x114, "focused");
_Static_assert(offsetof(g2_quicklist_data_view_t, completed) == 0x129, "completed");
_Static_assert(offsetof(g2_quicklist_data_view_t, incoming) == 0x2e48, "incoming");
_Static_assert(offsetof(g2_quicklist_data_view_t, operation) == 0x2e4e, "operation");

/* One list row: container first, then three child objects. */
typedef struct {
    void *obj[4];
} g2_quicklist_item_t;
_Static_assert(sizeof(g2_quicklist_item_t) == 0x10, "item stride");

/* RAM state. */
extern g2_quicklist_data_view_t g2_quicklist_ui_data_2012a72c;     /* RAM 0x2012a72c */
extern g2_quicklist_item_t g2_quicklist_rows_2006e370[QL_MAX_ITEMS]; /* RAM 0x2006e370 */
extern int32_t g2_quicklist_focus_index_200042c0;                  /* RAM 0x200042c0 (.data) */
extern uint8_t g2_quicklist_border_state_2007503f;                 /* RAM 0x2007503f quicklist_border_state */
extern uint8_t g2_quicklist_loading_shown_20075040;                /* RAM 0x20075040 */
extern uint8_t g2_quicklist_flag_20075041;                         /* RAM 0x20075041 */
extern uint64_t g2_quicklist_request_tick_200741a8;                /* RAM 0x200741a8 */
extern uint32_t g2_quicklist_word_20074df8;                        /* RAM 0x20074df8 widget_quicklist_init_flag */
extern void *g2_quicklist_root;                                    /* RAM 0x20074dfc */
extern void *g2_quicklist_container_20074e00;                      /* RAM 0x20074e00 scroll container */
extern void *g2_quicklist_border;                                  /* RAM 0x20074e04 focus border */
extern void *g2_quicklist_loading_20074e08;                        /* RAM 0x20074e08 loading row */
extern void *g2_quicklist_event_fifo_20074e14;                     /* RAM 0x20074e14 quicklist_ext_fifo */
extern int32_t g2_quicklist_tile_index;                            /* RAM 0x20074e18 dashboard tile index */
extern int32_t g2_quicklist_page_active_20074e1c;                  /* RAM 0x20074e1c */
extern int32_t g2_quicklist_anim_state_20074e20;                   /* RAM 0x20074e20 */
extern int32_t g2_quicklist_word_20074e28;                         /* RAM 0x20074e28 */
extern void *g2_dashboard_focus_frame;                             /* RAM 0x20074b9c expanded-page parent */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* LVGL 9.3 (stock copies). */
extern void *audio_uart_page_43de82(void *parent);                            /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flag);                 /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flag);                 /* lv_obj_remove_flag */
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *obj, uint32_t flag);  /* lv_obj_has_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *obj);             /* lv_obj_is_valid */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);          /* lv_obj_set_pos */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);          /* lv_obj_set_size */
extern void audio_uart_page_43f66c(void *obj);                                /* lv_obj_update_layout */
extern int32_t audio_uart_lv_obj_y_43fce0(void *obj);                         /* lv_obj_get_y */
extern int32_t audio_uart_lv_obj_height_43fdda(void *obj);                    /* lv_obj_get_height */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                         /* lv_color_hex */
extern void audio_uart_page_441164(void *obj, int32_t v, uint32_t sel);       /* style width */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);       /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);       /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);       /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);       /* pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel);  /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);    /* bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel);  /* border_color */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);       /* border_width */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);       /* radius */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* opa */
extern void audio_lv_delete_44d7b8(void *obj);                                /* lv_obj_delete */
extern void audio_uart_page_44d878(void *obj);                                /* lv_obj_clean */
extern void *audio_uart_lv_child_get_44dce2(void *obj, int32_t index);        /* lv_obj_get_child */
extern int32_t audio_uart_lv_child_count_44ddea(void *obj);                   /* lv_obj_get_child_count */
extern void audio_uart_page_44e368(void *obj, uint32_t mode);                 /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *obj, uint32_t dir);                  /* lv_obj_set_scroll_dir */
extern int32_t audio_uart_lv_obj_y_44e498(void *obj);                         /* lv_obj_get_scroll_y */
extern void audio_terminal_display_status_44ea04(void *obj, int32_t y, uint32_t anim); /* lv_obj_scroll_to_y */

/* ui_quicklist_page.c helpers earlier in this TU and neighbouring modules. */
extern void lv_obj_set_style_pad_all_4f5068(void *obj, int32_t value, uint32_t selector); /* pad_all copy */
extern void audio_quicklist_refresh_pending_4f5596(void);  /* count += incoming, capped at 40 */
extern int32_t quicklist_scroll_clamp_target_y_4f6d84(void *list, int32_t y);
extern void quicklist_get_item_geometry_4f6fc4(int32_t index, int32_t *x, int32_t *y,
                                               int32_t *w, int32_t *h);
extern void quicklist_ensure_item_visible_4f70a4(int32_t index);
extern void quicklist_border_shrink_to_item_4f7ae4(int32_t index);
extern void quicklist_prepare_fade_animation_for_new_item_4f80a0(uint8_t is_last, uint8_t operation,
                                                                 int32_t added_count);
extern void quicklist_loading_anim_destroy_4f8298(void);
extern void quicklist_process_completed_items_on_exit_4f8348(void);
extern int32_t Quicklist_Page_Reflash_4f8644(const uint8_t *data, uint32_t len);
extern void quicklist_delete_item_objects_4f92f0(void);
extern void quicklist_create_items_4f9484(void);
extern void dashboard_focus_frame_shrink_anim_4e92f4(void);
extern int32_t page_state_sync_dashboard_main_5000cc(uint32_t tile_index, uint8_t widget);
extern int32_t page_state_sync_quicklist_expanded_5001d2(uint32_t count, const uint32_t *ids,
                                                         int32_t border, uint32_t focused,
                                                         uint8_t completed);
extern void *ui_common_api_fn_00509c1c(void);       /* fifo create */
extern void ui_common_api_fn_00509c96(void *fifo);  /* fifo destroy */

void quicklist_page_clean_4fb1a4(void *obj, uint8_t stop_loading);

static const char tag[] = "quicklist.page"; /* ROM 0x789e40 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c"; /* ROM 0x6f7538 */

static const char fn_border[] = "quicklist_update_and_show_border_to_item"; /* ROM 0x7464b4 */
static const char m_border[] = "Updated border to item %d: pos(%d,%d) size(%dx%d)"; /* ROM 0x730474 */
static const char t_border[] =
    "[quicklist.page]Updated border to item %d: pos(%d,%d) size(%dx%d)"; /* ROM 0x708020 */
static const char fn_focus_up[] = "quicklist_update_focus_item_after_add_up"; /* ROM 0x7464e0 */
static const char m_focus_up[] = "ADD_UP: old_focus=%d, removed=%d, added=%d, total=%d"; /* ROM 0x725c30 */
static const char t_focus_up[] =
    "[quicklist.page]ADD_UP: old_focus=%d, removed=%d, added=%d, total=%d"; /* ROM 0x6ff08c */
static const char m_focus_up_res[] = "ADD_UP result: new_focus=%d"; /* ROM 0x7742dc */
static const char t_focus_up_res[] = "[quicklist.page]ADD_UP result: new_focus=%d"; /* ROM 0x74650c */
static const char fn_focus_down[] = "quicklist_update_focus_item_after_add_down"; /* ROM 0x746538 */
static const char m_focus_down[] = "ADD_DOWN: old_focus=%d, removed=%d, added=%d, total=%d"; /* ROM 0x725c68 */
static const char t_focus_down[] =
    "[quicklist.page]ADD_DOWN: old_focus=%d, removed=%d, added=%d, total=%d"; /* ROM 0x6ff0d4 */
static const char m_focus_down_res[] = "ADD_DOWN result: new_focus=%d"; /* ROM 0x767b30 */
static const char t_focus_down_res[] = "[quicklist.page]ADD_DOWN result: new_focus=%d"; /* ROM 0x73ae14 */
static const char fn_added_h[] = "quicklist_calculate_added_items_real_height"; /* ROM 0x746564 */
static const char m_added_up[] =
    "ADD_UP real added height: added_count=%d, total_height=%d"; /* ROM 0x71af20 */
static const char t_added_up[] =
    "[quicklist.page]ADD_UP real added height: added_count=%d, total_height=%d"; /* ROM 0x6f76b4 */
static const char m_added_down[] =
    "ADD_DOWN real added height: added_count=%d, start_index=%d, total_height=%d"; /* ROM 0x6f7700 */
static const char t_added_down[] =
    "[quicklist.page]ADD_DOWN real added height: added_count=%d, start_index=%d, total_height=%d"; /* ROM 0x6e1e9c */
static const char fn_restore_cache[] = "quicklist_restore_scroll_position_with_cache"; /* ROM 0x73ae44 */
static const char m_cache_up[] =
    "ADD_UP scroll with cache: old=%d, removed_h=%d, added_h=%d, new=%d"; /* ROM 0x708064 */
static const char t_cache_up[] =
    "[quicklist.page]ADD_UP scroll with cache: old=%d, removed_h=%d, added_h=%d, new=%d"; /* ROM 0x6eaca8 */
static const char m_cache_down[] =
    "ADD_DOWN scroll with cache: old=%d, removed_h=%d, added_h=%d, new=%d"; /* ROM 0x6ff11c */
static const char t_cache_down[] =
    "[quicklist.page]ADD_DOWN scroll with cache: old=%d, removed_h=%d, added_h=%d, new=%d"; /* ROM 0x6e5a88 */
static const char m_precise[] =
    "Precise positioning: new_item_y=%d, old_offset=%d, precise_scroll=%d"; /* ROM 0x6ff164 */
static const char t_precise[] =
    "[quicklist.page]Precise positioning: new_item_y=%d, old_offset=%d, precise_scroll=%d"; /* ROM 0x6e5ae0 */
static const char m_use_precise[] = "Using precise scroll position: %d"; /* ROM 0x75cb58 */
static const char t_use_precise[] = "[quicklist.page]Using precise scroll position: %d"; /* ROM 0x7304a8 */
static const char m_restored_cache[] =
    "Restored scroll position with cache: old=%d, new=%d, operation=%d, focus_item=%d"; /* ROM 0x6eacfc */
static const char t_restored_cache[] =
    "[quicklist.page]Restored scroll position with cache: old=%d, new=%d, operation=%d, focus_item=%d"; /* ROM 0x6dbd1c */
static const char fn_restore[] = "quicklist_restore_scroll_position"; /* ROM 0x75cb7c */
static const char m_restored[] = "Restored scroll position: old=%d, new=%d, operation=%d"; /* ROM 0x725ca0 */
static const char t_restored[] =
    "[quicklist.page]Restored scroll position: old=%d, new=%d, operation=%d"; /* ROM 0x6ff1ac */
static const char fn_full[] = "quicklist_handle_full_update"; /* ROM 0x767b50 */
static const char m_full[] = "Full update completed, total_quicklist_num=%d"; /* ROM 0x73ae74 */
static const char t_full[] = "[quicklist.page]Full update completed, total_quicklist_num=%d"; /* ROM 0x711524 */
static const char fn_add_up[] = "quicklist_handle_add_up_update"; /* ROM 0x767b70 */
static const char m_add_up[] = "ADD_UP: old_total=%d, added=%d, removed=%d"; /* ROM 0x746590 */
static const char t_add_up[] = "[quicklist.page]ADD_UP: old_total=%d, added=%d, removed=%d"; /* ROM 0x71af5c */
static const char m_up_removed[] = "ADD_UP total removed height: %d"; /* ROM 0x767b90 */
static const char t_up_removed[] = "[quicklist.page]ADD_UP total removed height: %d"; /* ROM 0x73aea4 */
static const char m_up_focus[] =
    "ADD_UP cached focus item %d offset: %d (item_y=%d, scroll_y=%d)"; /* ROM 0x711564 */
static const char t_up_focus[] =
    "[quicklist.page]ADD_UP cached focus item %d offset: %d (item_y=%d, scroll_y=%d)"; /* ROM 0x6f0da8 */
static const char m_up_loading[] =
    "ADD_UP cached loading offset: %d (loading_height=%d, scroll_y=%d)"; /* ROM 0x7080a8 */
static const char t_up_loading[] =
    "[quicklist.page]ADD_UP cached loading offset: %d (loading_height=%d, scroll_y=%d)"; /* ROM 0x6ead50 */
static const char m_up_done[] = "Add up update completed"; /* ROM 0x77d4ec */
static const char t_up_done[] = "[quicklist.page]Add up update completed"; /* ROM 0x750dec */
static const char fn_add_down[] = "quicklist_handle_add_down_update"; /* ROM 0x75cba0 */
static const char m_add_down[] = "ADD_DOWN: old_total=%d, added=%d, removed=%d"; /* ROM 0x73aed4 */
static const char t_add_down[] = "[quicklist.page]ADD_DOWN: old_total=%d, added=%d, removed=%d"; /* ROM 0x7115a4 */
static const char m_down_removed[] = "ADD_DOWN total removed height: %d"; /* ROM 0x75cbc4 */
static const char t_down_removed[] = "[quicklist.page]ADD_DOWN total removed height: %d"; /* ROM 0x7304dc */
static const char m_down_focus[] =
    "ADD_DOWN cached focus item %d offset: %d (item_y=%d, scroll_y=%d)"; /* ROM 0x7080ec */
static const char t_down_focus[] =
    "[quicklist.page]ADD_DOWN cached focus item %d offset: %d (item_y=%d, scroll_y=%d)"; /* ROM 0x6eada4 */
static const char m_down_loading[] =
    "ADD_DOWN cached loading offset: %d (loading_y=%d, scroll_y=%d)"; /* ROM 0x7115e4 */
static const char t_down_loading[] =
    "[quicklist.page]ADD_DOWN cached loading offset: %d (loading_y=%d, scroll_y=%d)"; /* ROM 0x6f0df8 */
static const char m_down_done[] = "Add down update completed"; /* ROM 0x7742f8 */
static const char t_down_done[] = "[quicklist.page]Add down update completed"; /* ROM 0x7465bc */
static const char fn_modify[] = "quicklist_handle_modify_update"; /* ROM 0x767bb0 */
static const char m_modify[] = "Modify update completed"; /* ROM 0x77d504 */
static const char t_modify[] = "[quicklist.page]Modify update completed"; /* ROM 0x750e14 */
static const char fn_shrunk[] = "quicklist_handle_border_shrunk_update"; /* ROM 0x750e3c */
static const char m_shrunk[] =
    "Border shrunk update: operation=%d, focus_item=%d, scroll_y=%d"; /* ROM 0x711624 */
static const char t_shrunk[] =
    "[quicklist.page]Border shrunk update: operation=%d, focus_item=%d, scroll_y=%d"; /* ROM 0x6f0e48 */
static const char m_unknown_op[] = "Unknown operation type: %d"; /* ROM 0x774314 */
static const char t_unknown_op[] = "[quicklist.page]Unknown operation type: %d"; /* ROM 0x7465e8 */
static const char fn_create[] = "Quicklist_ext_WidgetPage_Create"; /* ROM 0x767bd0 */
static const char m_create[] = "total_quicklist_num=%d, quicklist_border_state=%d"; /* ROM 0x730510 */
static const char t_create[] =
    "[quicklist.page]total_quicklist_num=%d, quicklist_border_state=%d"; /* ROM 0x708130 */
static const char fn_init[] = "Quicklist_ext_Widget_init"; /* ROM 0x774330 */
static const char m_fifo_fail[] = "quicklist_ext_fifo create failed"; /* ROM 0x75cbe8 */
static const char t_fifo_fail[] = "[quicklist.page]quicklist_ext_fifo create failed"; /* ROM 0x730544 */

/* Stock expands the two-channel log macro at every call site:
 * full log (flag bit 1) and compressed log (flag bits 0/2, code level<<26 | nargs<<22). */
#define QL_LOG0(lvl, line, fn, m, t)                                                     \
    do {                                                                                 \
        if (audio_log_flags() & 2u)                                                      \
            audio_log_extended((lvl), tag, src, (fn), (line), (m));                      \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                        \
            (void)compress_log_output((uint32_t)(lvl) << 26, (t), (t));                  \
    } while (0)
#define QL_LOG(lvl, line, fn, m, t, n, ...)                                              \
    do {                                                                                 \
        if (audio_log_flags() & 2u)                                                      \
            audio_log_extended((lvl), tag, src, (fn), (line), (m), __VA_ARGS__);         \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                        \
            (void)compress_log_output(((uint32_t)(lvl) << 26) | ((uint32_t)(n) << 22),   \
                                      (t), (t), __VA_ARGS__);                            \
    } while (0)

static int32_t ql_item_height(int32_t index)
{
    return audio_uart_lv_obj_height_43fdda(g2_quicklist_rows_2006e370[index].obj[0]) + QL_ITEM_GAP;
}

/* Moves the focus border over item `index` and makes it visible. */
void quicklist_update_and_show_border_to_item_4f9afc(int32_t index)
{
    int32_t x, y, w, h;

    if (g2_quicklist_border == NULL || index < 0 || index >= (int32_t)g2_quicklist_ui_data_2012a72c.count)
        return;
    g2_quicklist_border_state_2007503f = 2;
    quicklist_get_item_geometry_4f6fc4(index, &x, &y, &w, &h);
    y -= audio_uart_lv_obj_y_44e498(g2_quicklist_container_20074e00);
    audio_uart_page_43dfa4(g2_quicklist_border, LV_OBJ_FLAG_HIDDEN);
    audio_uart_display_audio_reset_441488(g2_quicklist_border, 0xffu, 0u);
    audio_uart_page_43f09a(g2_quicklist_border, x + 12, y + 8);
    audio_uart_page_43f4c0(g2_quicklist_border, w, h);
    QL_LOG(4u, 0xf4fu, fn_border, m_border, t_border, 5, index, x, y, w, h);
}

/* ADD_UP: older items were prepended, so the old focus index shifts by `added`. */
void quicklist_update_focus_item_after_add_up_4f9bf8(int32_t old_focus, int32_t removed,
                                                     int32_t added)
{
    int32_t total = g2_quicklist_ui_data_2012a72c.count;
    int32_t idx;

    QL_LOG(4u, 0xf8bu, fn_focus_up, m_focus_up, t_focus_up, 4, old_focus, removed, added,
           (int32_t)g2_quicklist_ui_data_2012a72c.count);
    if (old_focus == QL_FOCUS_LOADING_DOWN) {
        idx = total - added;
        if (idx < 0 || idx >= total)
            g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -1
                                      : (int32_t)g2_quicklist_ui_data_2012a72c.count - 1;
        else
            g2_quicklist_focus_index_200042c0 = idx;
    } else if (old_focus == QL_FOCUS_LOADING_UP) {
        idx = added - 1;
        if (idx < 0 || idx >= total)
            g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -2 : 0;
        else
            g2_quicklist_focus_index_200042c0 = idx;
    } else if (old_focus < 0) {
        g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -1 : 0;
    } else {
        idx = added + old_focus;
        if (idx < 0 || idx >= total)
            g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -1 : 0;
        else
            g2_quicklist_focus_index_200042c0 = idx;
    }
    QL_LOG(4u, 0xfb9u, fn_focus_up, m_focus_up_res, t_focus_up_res, 1, g2_quicklist_focus_index_200042c0);
}

/* ADD_DOWN: newer items were appended and `removed` items dropped from the top. */
void quicklist_update_focus_item_after_add_down_4f9d84(int32_t old_focus, int32_t removed,
                                                       int32_t added)
{
    int32_t total = g2_quicklist_ui_data_2012a72c.count;
    int32_t idx;

    QL_LOG(4u, 0xfc2u, fn_focus_down, m_focus_down, t_focus_down, 4, old_focus, removed, added,
           (int32_t)g2_quicklist_ui_data_2012a72c.count);
    if (old_focus == QL_FOCUS_LOADING_DOWN) {
        idx = total - added;
        if (idx < 0 || idx >= total)
            g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -1
                                      : (int32_t)g2_quicklist_ui_data_2012a72c.count - 1;
        else
            g2_quicklist_focus_index_200042c0 = idx;
    } else if (old_focus == QL_FOCUS_LOADING_UP) {
        if (g2_quicklist_ui_data_2012a72c.count == 0)
            g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -2 : 0;
        else
            g2_quicklist_focus_index_200042c0 = 0;
    } else if (old_focus < 0) {
        g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -1 : 0;
    } else {
        idx = old_focus - removed;
        if (idx < 0 || idx >= total)
            g2_quicklist_focus_index_200042c0 = (g2_quicklist_ui_data_2012a72c.count == 0) ? -1 : 0;
        else
            g2_quicklist_focus_index_200042c0 = idx;
    }
    QL_LOG(4u, 0xfefu, fn_focus_down, m_focus_down_res, t_focus_down_res, 1,
           g2_quicklist_focus_index_200042c0);
}

/* Sum of (height + 4) of the `added_count` rows just inserted at the top
 * (ADD_UP) or bottom (ADD_DOWN) of the rebuilt list. */
int32_t quicklist_calculate_added_items_real_height_4f9f14(uint8_t op, int32_t added_count)
{
    int32_t total = 0;
    int32_t i, n, start;

    if (added_count < 1)
        return 0;
    if (op == QL_OP_ADD_UP) {
        n = added_count;
        if ((int32_t)g2_quicklist_ui_data_2012a72c.count < added_count)
            n = g2_quicklist_ui_data_2012a72c.count;
        for (i = 0; i < n; i++) {
            if (g2_quicklist_rows_2006e370[i].obj[0] != NULL)
                total += ql_item_height(i);
        }
        QL_LOG(4u, 0x100cu, fn_added_h, m_added_up, t_added_up, 2, added_count, total);
    } else if (op == QL_OP_ADD_DOWN) {
        start = (int32_t)g2_quicklist_ui_data_2012a72c.count - added_count;
        if (start < 0)
            start = 0;
        for (i = start; i < (int32_t)g2_quicklist_ui_data_2012a72c.count; i++) {
            if (g2_quicklist_rows_2006e370[i].obj[0] != NULL)
                total += ql_item_height(i);
        }
        QL_LOG(4u, 0x101cu, fn_added_h, m_added_down, t_added_down, 3, added_count, start, total);
    }
    return total;
}

/* Restores the list scroll after an ADD_UP/ADD_DOWN rebuild. `cached_offset`
 * is the focused item's on-screen y before the rebuild; when the item still
 * exists its new y minus that offset is used as the exact scroll target. */
void quicklist_restore_scroll_position_with_cache_4fa058(int32_t old_scroll, int32_t focus,
                                                         int32_t cached_offset, uint8_t op,
                                                         int32_t removed_h, int32_t added_count)
{
    int32_t target = old_scroll;
    int32_t added_h, item_y, precise, clamped;

    (void)focus;
    if (op == QL_OP_ADD_UP) {
        added_h = quicklist_calculate_added_items_real_height_4f9f14(QL_OP_ADD_UP, added_count);
        target = added_h + old_scroll;
        QL_LOG(4u, 0x105fu, fn_restore_cache, m_cache_up, t_cache_up, 4, old_scroll, removed_h,
               added_h, target);
    } else if (op == QL_OP_ADD_DOWN) {
        added_h = quicklist_calculate_added_items_real_height_4f9f14(QL_OP_ADD_DOWN, added_count);
        target = old_scroll - removed_h;
        QL_LOG(4u, 0x1069u, fn_restore_cache, m_cache_down, t_cache_down, 4, old_scroll,
               removed_h, added_h, target);
    }
    if (g2_quicklist_focus_index_200042c0 >= 0 && g2_quicklist_focus_index_200042c0 < (int32_t)g2_quicklist_ui_data_2012a72c.count &&
        g2_quicklist_rows_2006e370[g2_quicklist_focus_index_200042c0].obj[0] != NULL) {
        item_y = audio_uart_lv_obj_y_43fce0(g2_quicklist_rows_2006e370[g2_quicklist_focus_index_200042c0].obj[0]);
        precise = item_y - cached_offset;
        QL_LOG(4u, 0x1076u, fn_restore_cache, m_precise, t_precise, 3, item_y, cached_offset,
               precise);
        if (precise >= 0) {
            QL_LOG(4u, 0x107bu, fn_restore_cache, m_use_precise, t_use_precise, 1, precise);
            target = precise;
        }
    }
    clamped = quicklist_scroll_clamp_target_y_4f6d84(g2_quicklist_container_20074e00, target);
    audio_terminal_display_status_44ea04(g2_quicklist_container_20074e00, clamped, LV_ANIM_OFF);
    QL_LOG(4u, 0x1087u, fn_restore_cache, m_restored_cache, t_restored_cache, 4, old_scroll,
           clamped, (uint32_t)op, g2_quicklist_focus_index_200042c0);
}

/* Modify keeps the previous scroll offset unchanged. */
void quicklist_restore_scroll_position_4fa2a4(int32_t old_scroll, int32_t focus, uint8_t op)
{
    int32_t target = old_scroll;

    (void)focus;
    audio_terminal_display_status_44ea04(g2_quicklist_container_20074e00, target, LV_ANIM_OFF);
    QL_LOG(4u, 0x109bu, fn_restore, m_restored, t_restored, 3, old_scroll, target, (uint32_t)op);
}

void quicklist_handle_full_update_4fa314(int32_t scroll_y, int32_t focus)
{
    (void)scroll_y;
    (void)focus;
    if (g2_quicklist_container_20074e00 == NULL || audio_terminal_ui_object_valid_43e2ea(g2_quicklist_container_20074e00) == 0u)
        return;
    quicklist_page_clean_4fb1a4(g2_quicklist_container_20074e00, 1u);
    audio_quicklist_refresh_pending_4f5596();
    quicklist_create_items_4f9484();
    audio_uart_page_43f66c(g2_quicklist_container_20074e00);
    if (g2_quicklist_ui_data_2012a72c.count != 0u) {
        g2_quicklist_focus_index_200042c0 = 0;
        quicklist_update_and_show_border_to_item_4f9afc(0);
    } else if (g2_quicklist_border != NULL &&
               audio_terminal_ui_object_valid_43e2ea(g2_quicklist_border) == 1u) {
        /* Empty list: the border frames the whole page. */
        g2_quicklist_border_state_2007503f = 0;
        g2_quicklist_focus_index_200042c0 = -1;
        audio_uart_page_43dfa4(g2_quicklist_border, LV_OBJ_FLAG_HIDDEN);
        audio_uart_display_audio_reset_441488(g2_quicklist_border, 0xffu, 0u);
        audio_uart_page_43f09a(g2_quicklist_border, 0, 0);
        audio_uart_page_43f4c0(g2_quicklist_border, QL_SCREEN_W, QL_SCREEN_H);
    }
    QL_LOG(4u, 0x10bcu, fn_full, m_full, t_full, 1, (int32_t)g2_quicklist_ui_data_2012a72c.count);
}

void quicklist_handle_add_up_update_4fa404(int32_t scroll_y, int32_t focus)
{
    uint16_t added;
    int16_t removed;
    int32_t removed_h = 0;
    int32_t cached = 0;
    int32_t h, item_y;
    uint16_t i;

    if (g2_quicklist_container_20074e00 == NULL || audio_terminal_ui_object_valid_43e2ea(g2_quicklist_container_20074e00) == 0u)
        return;
    added = g2_quicklist_ui_data_2012a72c.incoming;
    removed = 0;
    if ((uint32_t)g2_quicklist_ui_data_2012a72c.incoming + (uint32_t)g2_quicklist_ui_data_2012a72c.count > QL_MAX_ITEMS)
        removed = (int16_t)(g2_quicklist_ui_data_2012a72c.incoming + g2_quicklist_ui_data_2012a72c.count - QL_MAX_ITEMS);
    QL_LOG(4u, 0x10cfu, fn_add_up, m_add_up, t_add_up, 3, (int32_t)g2_quicklist_ui_data_2012a72c.count,
           (int32_t)added, (int32_t)removed);
    if (removed != 0) {
        /* Oldest-at-bottom rows that fall off the end. */
        for (i = (uint16_t)(g2_quicklist_ui_data_2012a72c.count - removed); (int32_t)i < (int32_t)g2_quicklist_ui_data_2012a72c.count;
             i++) {
            if (g2_quicklist_rows_2006e370[i].obj[0] != NULL)
                removed_h += ql_item_height(i);
        }
        QL_LOG(4u, 0x10e1u, fn_add_up, m_up_removed, t_up_removed, 1, removed_h);
    }
    if (focus < 0 || focus >= (int32_t)g2_quicklist_ui_data_2012a72c.count) {
        if (focus == QL_FOCUS_LOADING_UP && g2_quicklist_loading_20074e08 != NULL &&
            audio_uart_lv_obj_has_flag_43e0e0(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN) == 0u) {
            h = audio_uart_lv_obj_height_43fdda(g2_quicklist_loading_20074e08);
            cached = h + QL_ITEM_GAP;
            QL_LOG(4u, 0x10f9u, fn_add_up, m_up_loading, t_up_loading, 3, cached, h, scroll_y);
        }
    } else if (g2_quicklist_rows_2006e370[focus].obj[0] != NULL) {
        item_y = audio_uart_lv_obj_y_43fce0(g2_quicklist_rows_2006e370[focus].obj[0]);
        cached = item_y - scroll_y;
        QL_LOG(4u, 0x10eau, fn_add_up, m_up_focus, t_up_focus, 4, focus, cached, item_y, scroll_y);
    }
    quicklist_delete_item_objects_4f92f0();
    audio_quicklist_refresh_pending_4f5596();
    quicklist_create_items_4f9484();
    audio_uart_page_43f66c(g2_quicklist_container_20074e00);
    quicklist_update_focus_item_after_add_up_4f9bf8(focus, removed, added);
    quicklist_restore_scroll_position_with_cache_4fa058(scroll_y, focus, cached, QL_OP_ADD_UP,
                                                        removed_h, added);
    if (g2_quicklist_loading_20074e08 == NULL ||
        audio_uart_lv_obj_has_flag_43e0e0(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN) != 0u) {
        if (g2_quicklist_focus_index_200042c0 >= 0 && g2_quicklist_focus_index_200042c0 < (int32_t)g2_quicklist_ui_data_2012a72c.count) {
            quicklist_ensure_item_visible_4f70a4(g2_quicklist_focus_index_200042c0);
            quicklist_update_and_show_border_to_item_4f9afc(g2_quicklist_focus_index_200042c0);
        }
    } else {
        quicklist_prepare_fade_animation_for_new_item_4f80a0(1u, QL_OP_ADD_UP, added);
    }
    QL_LOG0(4u, 0x111au, fn_add_up, m_up_done, t_up_done);
}

void quicklist_handle_add_down_update_4fa72c(int32_t scroll_y, int32_t focus)
{
    uint16_t added;
    uint16_t removed, n;
    int32_t removed_h = 0;
    int32_t cached = 0;
    int32_t y, i;

    if (g2_quicklist_container_20074e00 == NULL || audio_terminal_ui_object_valid_43e2ea(g2_quicklist_container_20074e00) == 0u)
        return;
    added = g2_quicklist_ui_data_2012a72c.incoming;
    removed = 0;
    if ((uint32_t)g2_quicklist_ui_data_2012a72c.incoming + (uint32_t)g2_quicklist_ui_data_2012a72c.count > QL_MAX_ITEMS)
        removed = (uint16_t)(g2_quicklist_ui_data_2012a72c.incoming + g2_quicklist_ui_data_2012a72c.count - QL_MAX_ITEMS);
    QL_LOG(4u, 0x112du, fn_add_down, m_add_down, t_add_down, 3, (int32_t)g2_quicklist_ui_data_2012a72c.count,
           (int32_t)added, (int32_t)removed);
    if (removed != 0u) {
        /* Rows that fall off the top. */
        n = removed;
        if (g2_quicklist_ui_data_2012a72c.count < removed)
            n = g2_quicklist_ui_data_2012a72c.count;
        for (i = 0; i < (int32_t)n; i++) {
            if (g2_quicklist_rows_2006e370[i].obj[0] != NULL)
                removed_h += ql_item_height(i);
        }
        QL_LOG(4u, 0x1141u, fn_add_down, m_down_removed, t_down_removed, 1, removed_h);
    }
    if (focus < 0) {
        if (focus == QL_FOCUS_LOADING_DOWN && g2_quicklist_loading_20074e08 != NULL &&
            audio_uart_lv_obj_has_flag_43e0e0(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN) == 0u) {
            y = audio_uart_lv_obj_y_43fce0(g2_quicklist_loading_20074e08);
            cached = y - scroll_y;
            QL_LOG(4u, 0x1152u, fn_add_down, m_down_loading, t_down_loading, 3, cached, y, scroll_y);
        }
    } else if (g2_quicklist_rows_2006e370[focus].obj[0] != NULL) {
        y = audio_uart_lv_obj_y_43fce0(g2_quicklist_rows_2006e370[focus].obj[0]);
        cached = y - scroll_y;
        QL_LOG(4u, 0x114au, fn_add_down, m_down_focus, t_down_focus, 4, focus, cached, y, scroll_y);
    }
    quicklist_delete_item_objects_4f92f0();
    audio_quicklist_refresh_pending_4f5596();
    quicklist_create_items_4f9484();
    audio_uart_page_43f66c(g2_quicklist_container_20074e00);
    quicklist_update_focus_item_after_add_down_4f9d84(focus, removed, added);
    quicklist_restore_scroll_position_with_cache_4fa058(scroll_y, focus, cached, QL_OP_ADD_DOWN,
                                                        removed_h, added);
    if (g2_quicklist_loading_20074e08 == NULL ||
        audio_uart_lv_obj_has_flag_43e0e0(g2_quicklist_loading_20074e08, LV_OBJ_FLAG_HIDDEN) != 0u) {
        if (g2_quicklist_focus_index_200042c0 >= 0 && g2_quicklist_focus_index_200042c0 < (int32_t)g2_quicklist_ui_data_2012a72c.count) {
            quicklist_ensure_item_visible_4f70a4(g2_quicklist_focus_index_200042c0);
            quicklist_update_and_show_border_to_item_4f9afc(g2_quicklist_focus_index_200042c0);
        }
    } else {
        quicklist_prepare_fade_animation_for_new_item_4f80a0(0u, QL_OP_ADD_DOWN, added);
    }
    QL_LOG0(4u, 0x117au, fn_add_down, m_down_done, t_down_done);
}

void quicklist_handle_modify_update_4faa44(int32_t scroll_y, int32_t focus)
{
    if (g2_quicklist_container_20074e00 == NULL || audio_terminal_ui_object_valid_43e2ea(g2_quicklist_container_20074e00) == 0u)
        return;
    quicklist_delete_item_objects_4f92f0();
    audio_quicklist_refresh_pending_4f5596();
    quicklist_create_items_4f9484();
    audio_uart_page_43f66c(g2_quicklist_container_20074e00);
    if (focus < 0 || focus >= (int32_t)g2_quicklist_ui_data_2012a72c.count) {
        if (g2_quicklist_ui_data_2012a72c.count != 0u)
            g2_quicklist_focus_index_200042c0 = 0;
    } else {
        g2_quicklist_focus_index_200042c0 = focus;
    }
    quicklist_restore_scroll_position_4fa2a4(scroll_y, focus, QL_OP_MODIFY);
    if (g2_quicklist_focus_index_200042c0 >= 0 && g2_quicklist_focus_index_200042c0 < (int32_t)g2_quicklist_ui_data_2012a72c.count) {
        quicklist_ensure_item_visible_4f70a4(g2_quicklist_focus_index_200042c0);
        quicklist_update_and_show_border_to_item_4f9afc(g2_quicklist_focus_index_200042c0);
    }
    QL_LOG0(4u, 0x11a0u, fn_modify, m_modify, t_modify);
}

/* Dispatches the pending batch after the border has shrunk back onto an item. */
void quicklist_handle_border_shrunk_update_4fab18(void)
{
    int32_t scroll_y = 0;
    int32_t focus = g2_quicklist_focus_index_200042c0;
    uint8_t op;

    if (g2_quicklist_container_20074e00 != NULL)
        scroll_y = audio_uart_lv_obj_y_44e498(g2_quicklist_container_20074e00);
    QL_LOG(4u, 0x11b1u, fn_shrunk, m_shrunk, t_shrunk, 3, (uint32_t)g2_quicklist_ui_data_2012a72c.operation,
           focus, scroll_y);
    op = g2_quicklist_ui_data_2012a72c.operation;
    if (op == QL_OP_FULL) {
        quicklist_handle_full_update_4fa314(scroll_y, focus);
        return;
    }
    if (op != 0u) {
        if (op == QL_OP_ADD_DOWN) {
            if (g2_quicklist_ui_data_2012a72c.incoming == 0u)
                return;
            quicklist_handle_add_down_update_4fa72c(scroll_y, focus);
            return;
        }
        if (op < QL_OP_ADD_DOWN) {
            if (g2_quicklist_ui_data_2012a72c.incoming == 0u)
                return;
            quicklist_handle_add_up_update_4fa404(scroll_y, focus);
            return;
        }
        if (op == QL_OP_MODIFY) {
            if (g2_quicklist_ui_data_2012a72c.incoming == 0u)
                return;
            quicklist_handle_modify_update_4faa44(scroll_y, focus);
            return;
        }
    }
    QL_LOG(2u, 0x11cbu, fn_shrunk, m_unknown_op, t_unknown_op, 1,
           (uint32_t)g2_quicklist_ui_data_2012a72c.operation);
}

/* Builds the expanded page (root, list, border) on first entry; while the
 * border is shown on an item, a pending batch is applied in place instead.
 * Returns -1 for an unknown pending operation. */
int32_t Quicklist_ext_WidgetPage_Create_4fac74(void *parent)
{
    uint8_t create = 0;

    QL_LOG(4u, 0x11d5u, fn_create, m_create, t_create, 2, (int32_t)g2_quicklist_ui_data_2012a72c.count,
           (uint32_t)g2_quicklist_border_state_2007503f);
    if (g2_quicklist_ui_data_2012a72c.count == 0u || g2_quicklist_border_state_2007503f == 0u) {
        audio_quicklist_refresh_pending_4f5596();
        g2_quicklist_focus_index_200042c0 = -1;
        create = 1;
    } else if (g2_quicklist_border_state_2007503f != 0u) {
        if ((uint32_t)(g2_quicklist_ui_data_2012a72c.operation - 1u) > 3u)
            return -1;
        create = 0;
    }
    if (create == 0u) {
        quicklist_handle_border_shrunk_update_4fab18();
        return 0;
    }

    g2_quicklist_root = audio_uart_page_43de82(parent);
    audio_uart_page_43f4c0(g2_quicklist_root, QL_SCREEN_W, QL_SCREEN_H);
    audio_uart_page_43f09a(g2_quicklist_root, -1, -1);
    audio_uart_page_44127e(g2_quicklist_root, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_quicklist_root, 0xffu, 0u);
    audio_uart_page_4412ec(g2_quicklist_root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44131c(g2_quicklist_root, 0, 0u);
    lv_obj_set_style_pad_all_4f5068(g2_quicklist_root, 0, 0u);
    audio_uart_page_44146a(g2_quicklist_root, 0, 0u);
    audio_uart_page_43dfa4(g2_quicklist_root, LV_OBJ_FLAG_SCROLLABLE);

    g2_quicklist_container_20074e00 = audio_uart_page_43de82(g2_quicklist_root);
    audio_uart_page_43f4c0(g2_quicklist_container_20074e00, QL_SCREEN_W, QL_LIST_H);
    audio_uart_page_43f09a(g2_quicklist_container_20074e00, 0, 8);
    audio_uart_page_44120e(g2_quicklist_container_20074e00, 0, 0u);
    audio_uart_page_44121c(g2_quicklist_container_20074e00, 0, 0u);
    audio_uart_page_44122a(g2_quicklist_container_20074e00, 12, 0u);
    audio_uart_page_441238(g2_quicklist_container_20074e00, 18, 0u);
    audio_uart_page_4412ec(g2_quicklist_container_20074e00, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44131c(g2_quicklist_container_20074e00, 0, 0u);
    audio_uart_page_44127e(g2_quicklist_container_20074e00, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_quicklist_container_20074e00, 0xffu, 0u);
    audio_uart_page_44146a(g2_quicklist_container_20074e00, 0, 0u);
    audio_uart_page_43ded4(g2_quicklist_container_20074e00, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e3ca(g2_quicklist_container_20074e00, LV_DIR_VER);
    audio_uart_page_44e368(g2_quicklist_container_20074e00, LV_SCROLLBAR_MODE_AUTO);
    audio_uart_page_44127e(g2_quicklist_container_20074e00, audio_uart_page_44104c(0xffffffu), LV_PART_SCROLLBAR);
    audio_uart_page_44129e(g2_quicklist_container_20074e00, 0u, LV_PART_SCROLLBAR);
    audio_uart_page_441164(g2_quicklist_container_20074e00, 2, LV_PART_SCROLLBAR);

    g2_quicklist_border = audio_uart_page_43de82(g2_quicklist_root);
    audio_uart_page_43f4c0(g2_quicklist_border, QL_SCREEN_W, QL_SCREEN_H);
    audio_uart_page_43f09a(g2_quicklist_border, 0, 0);
    audio_uart_page_44127e(g2_quicklist_border, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_quicklist_border, 0u, 0u);
    audio_uart_page_44146a(g2_quicklist_border, 6, 0u);
    lv_obj_set_style_pad_all_4f5068(g2_quicklist_border, 0, 0u);
    audio_uart_page_44e368(g2_quicklist_border, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_4412ec(g2_quicklist_border, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44131c(g2_quicklist_border, 1, 0u);
    audio_uart_page_43dfa4(g2_quicklist_border, LV_OBJ_FLAG_HIDDEN);

    quicklist_create_items_4f9484();
    if (g2_quicklist_ui_data_2012a72c.count != 0u && g2_quicklist_border_state_2007503f == 0u) {
        audio_uart_page_43f66c(g2_quicklist_root);
        quicklist_border_shrink_to_item_4f7ae4(0);
    }
    return 0;
}

/* Closes the expanded page and returns to the dashboard tile (widget 4). */
void quicklist_ext_widget_deinit_4faf20(void)
{
    int32_t i;
    void *child;

    quicklist_process_completed_items_on_exit_4f8348();
    quicklist_loading_anim_destroy_4f8298();
    for (i = audio_uart_lv_child_count_44ddea(g2_dashboard_focus_frame) - 1; i >= 0; i--) {
        child = audio_uart_lv_child_get_44dce2(g2_dashboard_focus_frame, i);
        if (child != NULL)
            audio_lv_delete_44d7b8(child);
    }
    if (g2_quicklist_event_fifo_20074e14 != NULL) {
        ui_common_api_fn_00509c96(g2_quicklist_event_fifo_20074e14);
        g2_quicklist_event_fifo_20074e14 = NULL;
    }
    g2_quicklist_page_active_20074e1c = 0;
    g2_quicklist_anim_state_20074e20 = 0;
    (void)Quicklist_Page_Reflash_4f8644(NULL, 0u);
    dashboard_focus_frame_shrink_anim_4e92f4();
    (void)page_state_sync_dashboard_main_5000cc((uint32_t)g2_quicklist_tile_index, 4u);
}

int32_t Quicklist_ext_Widget_init_4faf9c(void *parent)
{
    if (g2_quicklist_event_fifo_20074e14 != NULL) {
        ui_common_api_fn_00509c96(g2_quicklist_event_fifo_20074e14);
        g2_quicklist_event_fifo_20074e14 = NULL;
    }
    g2_quicklist_event_fifo_20074e14 = ui_common_api_fn_00509c1c();
    if (g2_quicklist_event_fifo_20074e14 == NULL) {
        QL_LOG0(1u, 0x1251u, fn_init, m_fifo_fail, t_fifo_fail);
        return -1;
    }
    g2_quicklist_border_state_2007503f = 0;
    g2_quicklist_loading_shown_20075040 = 0;
    g2_quicklist_focus_index_200042c0 = -1;
    g2_quicklist_request_tick_200741a8 = 0u;
    g2_quicklist_flag_20075041 = 0;
    g2_quicklist_word_20074e28 = 0;
    g2_quicklist_anim_state_20074e20 = 0;
    (void)Quicklist_ext_WidgetPage_Create_4fac74(parent);
    g2_quicklist_page_active_20074e1c = 1;
    if (g2_quicklist_ui_data_2012a72c.count != 0u)
        (void)page_state_sync_quicklist_expanded_5001d2(0u, NULL, 0, g2_quicklist_ui_data_2012a72c.focused,
                                                        g2_quicklist_ui_data_2012a72c.completed != 0u);
    else
        (void)page_state_sync_quicklist_expanded_5001d2(0u, NULL, 0, 0u, 0u);
    return 0;
}

/* Resets the expanded-page state without touching the LVGL tree. */
int32_t quicklist_widget_deinit_4fb08c(void)
{
    quicklist_process_completed_items_on_exit_4f8348();
    if (g2_quicklist_event_fifo_20074e14 != NULL) {
        ui_common_api_fn_00509c96(g2_quicklist_event_fifo_20074e14);
        g2_quicklist_event_fifo_20074e14 = NULL;
    }
    g2_quicklist_page_active_20074e1c = 0;
    g2_quicklist_anim_state_20074e20 = 0;
    g2_quicklist_border_state_2007503f = 0;
    g2_quicklist_loading_shown_20075040 = 0;
    g2_quicklist_focus_index_200042c0 = -1;
    g2_quicklist_request_tick_200741a8 = 0u;
    g2_quicklist_flag_20075041 = 0;
    g2_quicklist_word_20074e28 = 0;
    g2_quicklist_word_20074df8 = 0u;
    return 0;
}

void quicklist_page_clean_4fb1a4(void *obj, uint8_t stop_loading)
{
    if (stop_loading == 1u)
        quicklist_loading_anim_destroy_4f8298();
    if (obj != NULL)
        audio_uart_page_44d878(obj);
}

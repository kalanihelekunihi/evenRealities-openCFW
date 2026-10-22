/* EvenHub common list container, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_list_container.c (log tag
 * "common_list_container"). Native 0x4dcd92..0x4dd463 and 0x4dd510..0x4dedc1; literal pools
 * 0x4dd464..0x4dd50f, 0x4de140..0x4de17b, 0x4de28c..0x4de353, 0x4dedc4..0x4dee63.
 * The head of the same stock file (get_color_from_index 0x4dcd32, the item-y helper 0x4dcd0a,
 * pad-all 0x4dccd8) is reconstructed separately and called here by address-suffixed name.
 *
 * A list is a fixed-size scroll window (scroll_container) holding a content_container with up to
 * 20 rows of 40 px, each an lv_obj with one label child. Up/down events move a focus highlight;
 * when the list is taller than the window the content scrolls so that the focus stays on the
 * second row from either edge. Moves past the first/last row play a 16 px rubber-band bounce.
 * Each move starts an animation (focus 200 ms timer, scroll 200 ms, bounce 2 x 150 ms); events
 * that arrive meanwhile go to a byte FIFO and are replayed one at a time on completion. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "common_containers_private.h"

static const char cc_tag[] = "common_list_container"; /* ROM 0x775a64 */
static const char cc_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\common_list_container.c"; /* ROM 0x6f1fb8 */
static const char fn_scroll_done[] = "common_list_scroll_anim_complete_cb"; /* ROM 0x7528a4 */
static const char fn_rubber_done[] = "common_list_rubber_band_anim_cb"; /* ROM 0x75e730 */
static const char fn_rubber[] = "common_list_trigger_rubber_band"; /* ROM 0x75e750 */
static const char fn_focus_done[] = "common_list_focus_change_anim_cb"; /* ROM 0x7528c8 */
static const char fn_create[] = "common_list_create"; /* ROM 0x77e938 */
static const char fn_destroy[] = "common_list_destroy"; /* ROM 0x77e94c */
static const char fn_inject[] = "common_list_inject_event"; /* ROM 0x76a0fc */
static const char sd_done[] = "common_list_scroll_anim_complete_cb: scroll animation complete"; /* ROM 0x709b24 */
static const char sd_done_s[] = "[common_list_container]common_list_scroll_anim_complete_cb: scroll animation complete"; /* ROM 0x6e2800 */
static const char sd_cached[] = "common_list_scroll_anim_complete_cb: processing cached event from FIFO"; /* ROM 0x6f8c24 */
static const char sd_cached_s[] = "[common_list_container]common_list_scroll_anim_complete_cb: processing cached event from FIFO"; /* ROM 0x6dcc34 */
static const char sd_reinject[] = "common_list_scroll_anim_complete_cb: re-injecting event %d"; /* ROM 0x712c94 */
static const char sd_reinject_s[] = "[common_list_container]common_list_scroll_anim_complete_cb: re-injecting event %d"; /* ROM 0x6e68bc */
static const char rb_done[] = "common_list_rubber_band_anim_cb: rubber band animation complete"; /* ROM 0x709b64 */
static const char rb_done_s[] = "[common_list_container]common_list_rubber_band_anim_cb: rubber band animation complete"; /* ROM 0x6e2858 */
static const char rb_reset[] = "Resetting content_container Y from %d to 0"; /* ROM 0x73ca30 */
static const char rb_reset_s[] = "[common_list_container]Resetting content_container Y from %d to 0"; /* ROM 0x700c0c */
static const char rb_cached[] = "common_list_rubber_band_anim_cb: processing cached event from FIFO"; /* ROM 0x700c50 */
static const char rb_cached_s[] = "[common_list_container]common_list_rubber_band_anim_cb: processing cached event from FIFO"; /* ROM 0x6df93c */
static const char rb_reinject[] = "common_list_rubber_band_anim_cb: re-injecting event %d"; /* ROM 0x71c930 */
static const char rb_reinject_s[] = "[common_list_container]common_list_rubber_band_anim_cb: re-injecting event %d"; /* ROM 0x6ebb28 */
static const char tr_not_zero[] = "Content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6f8c6c */
static const char tr_not_zero_s[] = "[common_list_container]Content container Y not zero before rubber band: %d, resetting first"; /* ROM 0x6df998 */
static const char tr_top[] = "Triggering TOP rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x71c968 */
static const char tr_top_s[] = "[common_list_container]Triggering TOP rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x6ebb78 */
static const char tr_bottom[] = "Triggering BOTTOM rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x712cd0 */
static const char tr_bottom_s[] = "[common_list_container]Triggering BOTTOM rubber band: normal_y=%d, stretch_y=%d"; /* ROM 0x6ebbc8 */
static const char fc_done[] = "common_list_focus_change_anim_cb: focus change delay complete"; /* ROM 0x709ba4 */
static const char fc_done_s[] = "[common_list_container]common_list_focus_change_anim_cb: focus change delay complete"; /* ROM 0x6e28b0 */
static const char fc_cached[] = "common_list_focus_change_anim_cb: processing cached event from FIFO"; /* ROM 0x700c94 */
static const char fc_cached_s[] = "[common_list_container]common_list_focus_change_anim_cb: processing cached event from FIFO"; /* ROM 0x6df9f4 */
static const char fc_reinject[] = "common_list_focus_change_anim_cb: re-injecting event %d"; /* ROM 0x71c9a0 */
static const char fc_reinject_s[] = "[common_list_container]common_list_focus_change_anim_cb: re-injecting event %d"; /* ROM 0x6ebc18 */
static const char cr_invalid[] = "common_list_create: invalid parameters (parent=%p, config=%p)"; /* ROM 0x709be4 */
static const char cr_invalid_s[] = "[common_list_container]common_list_create: invalid parameters (parent=%p, config=%p)"; /* ROM 0x6e2908 */
static const char cr_count[] = "common_list_create: invalid item_count %d (valid: 1~%d)"; /* ROM 0x71c9d8 */
static const char cr_count_s[] = "[common_list_container]common_list_create: invalid item_count %d (valid: 1~%d)"; /* ROM 0x6ebc68 */
static const char cr_x[] = "common_list_create: x_position %d > 576, clamping to 576"; /* ROM 0x712d0c */
static const char cr_x_s[] = "[common_list_container]common_list_create: x_position %d > 576, clamping to 576"; /* ROM 0x6ebcb8 */
static const char cr_y[] = "common_list_create: y_position %d > 288, clamping to 288"; /* ROM 0x712d48 */
static const char cr_y_s[] = "[common_list_container]common_list_create: y_position %d > 288, clamping to 288"; /* ROM 0x6ebd08 */
static const char cr_w[] = "common_list_create: width %d > 576, clamping to 576"; /* ROM 0x727714 */
static const char cr_w_s[] = "[common_list_container]common_list_create: width %d > 576, clamping to 576"; /* ROM 0x6f2004 */
static const char cr_h[] = "common_list_create: height %d > 288, clamping to 288"; /* ROM 0x71ca10 */
static const char cr_h_s[] = "[common_list_container]common_list_create: height %d > 288, clamping to 288"; /* ROM 0x6f2050 */
static const char cr_bw[] = "common_list_create: border_width %d > 5, clamping to 5"; /* ROM 0x71ca48 */
static const char cr_bw_s[] = "[common_list_container]common_list_create: border_width %d > 5, clamping to 5"; /* ROM 0x6ebd58 */
static const char cr_bc[] = "common_list_create: border_color %d > 16, clamping to 16"; /* ROM 0x712d84 */
static const char cr_bc_s[] = "[common_list_container]common_list_create: border_color %d > 16, clamping to 16"; /* ROM 0x6ebda8 */
static const char cr_br[] = "common_list_create: border_radius %d > 10, clamping to 10"; /* ROM 0x712dc0 */
static const char cr_br_s[] = "[common_list_container]common_list_create: border_radius %d > 10, clamping to 10"; /* ROM 0x6e6910 */
static const char cr_pad[] = "common_list_create: padding %d > 32, clamping to 32"; /* ROM 0x727748 */
static const char cr_pad_s[] = "[common_list_container]common_list_create: padding %d > 32, clamping to 32"; /* ROM 0x6f209c */
static const char cr_items[] = "common_list_create: item_count %d > %d, clamping to %d"; /* ROM 0x71ca80 */
static const char cr_items_s[] = "[common_list_container]common_list_create: item_count %d > %d, clamping to %d"; /* ROM 0x6ebdf8 */
static const char cr_creating[] = "common_list_create: creating list with %d items at pos(%d,%d) size(%dx%d)"; /* ROM 0x6f20e8 */
static const char cr_creating_s[] = "[common_list_container]common_list_create: creating list with %d items at pos(%d,%d) size(%dx%d)"; /* ROM 0x6da28c */
static const char cr_alloc[] = "common_list_create: failed to allocate handle"; /* ROM 0x731fc4 */
static const char cr_alloc_s[] = "[common_list_container]common_list_create: failed to allocate handle"; /* ROM 0x6f8cb4 */
static const char cr_visible[] = "common_list_create: visible_height=%d, visible_item_count=%d, border_en=%d"; /* ROM 0x6f2134 */
static const char cr_visible_s[] = "[common_list_container]common_list_create: visible_height=%d, visible_item_count=%d, border_en=%d"; /* ROM 0x6da2f0 */
static const char cr_fifo[] = "common_list_create: failed to create fifo_handle"; /* ROM 0x72777c */
static const char cr_fifo_s[] = "[common_list_container]common_list_create: failed to create fifo_handle"; /* ROM 0x6f8cfc */
static const char cr_fifo_note[] = "common_list_create: FIFO queue creation not implemented yet"; /* ROM 0x712dfc */
static const char cr_fifo_note_s[] = "[common_list_container]common_list_create: FIFO queue creation not implemented yet"; /* ROM 0x6e6964 */
static const char cr_scroll_fail[] = "common_list_create: failed to create scroll_container"; /* ROM 0x71cab8 */
static const char cr_scroll_fail_s[] = "[common_list_container]common_list_create: failed to create scroll_container"; /* ROM 0x6ebe48 */
static const char cr_border[] = "common_list_create: border enabled (width=%d, color=0x%06X)"; /* ROM 0x712e38 */
static const char cr_border_s[] = "[common_list_container]common_list_create: border enabled (width=%d, color=0x%06X)"; /* ROM 0x6e69b8 */
static const char cr_actual[] = "common_list_create: actual_content=%d, visible_height=%d, total_items=%d"; /* ROM 0x6f2180 */
static const char cr_actual_s[] = "[common_list_container]common_list_create: actual_content=%d, visible_height=%d, total_items=%d"; /* ROM 0x6dcc94 */
static const char cr_no_scroll[] = "common_list_create: no scroll needed (content_height=%d, centered layout)"; /* ROM 0x6f21cc */
static const char cr_no_scroll_s[] = "[common_list_container]common_list_create: no scroll needed (content_height=%d, centered layout)"; /* ROM 0x6da354 */
static const char cr_scroll[] = "common_list_create: scroll enabled (content_height=%d, extra_space=%d)"; /* ROM 0x6f8d44 */
static const char cr_scroll_s[] = "[common_list_container]common_list_create: scroll enabled (content_height=%d, extra_space=%d)"; /* ROM 0x6dccf4 */
static const char cr_content_fail[] = "common_list_create: failed to create content_container"; /* ROM 0x71caf0 */
static const char cr_content_fail_s[] = "[common_list_container]common_list_create: failed to create content_container"; /* ROM 0x6ebe98 */
static const char cr_creating_items[] = "common_list_create: creating %d items..."; /* ROM 0x73ca5c */
static const char cr_creating_items_s[] = "[common_list_container]common_list_create: creating %d items..."; /* ROM 0x709c24 */
static const char cr_item_fail[] = "common_list_create: failed to create item %d"; /* ROM 0x731ff4 */
static const char cr_item_fail_s[] = "[common_list_container]common_list_create: failed to create item %d"; /* ROM 0x700cd8 */
static const char cr_initial[] = "common_list_create: initial selection set to index 0 (border_en=%d)"; /* ROM 0x700d1c */
static const char cr_initial_s[] = "[common_list_container]common_list_create: initial selection set to index 0 (border_en=%d)"; /* ROM 0x6dfa50 */
static const char cr_done[] = "common_list_create: list created successfully with %d items at (%d,%d)"; /* ROM 0x6f8d8c */
static const char cr_done_s[] = "[common_list_container]common_list_create: list created successfully with %d items at (%d,%d)"; /* ROM 0x6dcd54 */
static const char de_null[] = "common_list_destroy: handle is NULL"; /* ROM 0x7528ec */
static const char de_null_s[] = "[common_list_container]common_list_destroy: handle is NULL"; /* ROM 0x712e74 */
static const char de_destroying[] = "common_list_destroy: destroying list with %d items"; /* ROM 0x7277b0 */
static const char de_destroying_s[] = "[common_list_container]common_list_destroy: destroying list with %d items"; /* ROM 0x6f2218 */
static const char de_done[] = "common_list_destroy: list destroyed"; /* ROM 0x752910 */
static const char de_done_s[] = "[common_list_container]common_list_destroy: list destroyed"; /* ROM 0x712eb0 */
static const char ie_null[] = "common_list_inject_event: handle is NULL"; /* ROM 0x73ca88 */
static const char ie_null_s[] = "[common_list_container]common_list_inject_event: handle is NULL"; /* ROM 0x709c64 */
static const char ie_not_init[] = "common_list_inject_event: list not initialized"; /* ROM 0x732024 */
static const char ie_not_init_s[] = "[common_list_container]common_list_inject_event: list not initialized"; /* ROM 0x6f8dd4 */
static const char ie_unknown[] = "common_list_inject_event: unknown event type %d"; /* ROM 0x732054 */
static const char ie_unknown_s[] = "[common_list_container]common_list_inject_event: unknown event type %d"; /* ROM 0x6f8e1c */
static const char ie_busy[] = "common_list_inject_event: animation in progress, push event %d to FIFO"; /* ROM 0x6f8e64 */
static const char ie_busy_s[] = "[common_list_container]common_list_inject_event: animation in progress, push event %d to FIFO"; /* ROM 0x6dcdb4 */
static const char ie_push_fail[] = "common_list_inject_event: FIFO push failed (maybe full)"; /* ROM 0x71cb28 */
static const char ie_push_fail_s[] = "[common_list_container]common_list_inject_event: FIFO push failed (maybe full)"; /* ROM 0x6ebee8 */
static const char ie_no_items[] = "common_list_inject_event: no items in list"; /* ROM 0x73cab4 */
static const char ie_no_items_s[] = "[common_list_container]common_list_inject_event: no items in list"; /* ROM 0x700d60 */
static const char ie_up_ns[] = "COMMON_LIST_EVENT_UP (no scroll needed): index=%d"; /* ROM 0x7277e4 */
static const char ie_up_ns_s[] = "[common_list_container]COMMON_LIST_EVENT_UP (no scroll needed): index=%d"; /* ROM 0x6f2264 */
static const char ie_up_rb[] = "COMMON_LIST_EVENT_UP: At first item, trigger rubber band"; /* ROM 0x712eec */
static const char ie_up_rb_s[] = "[common_list_container]COMMON_LIST_EVENT_UP: At first item, trigger rubber band"; /* ROM 0x6ebf38 */
static const char ie_down_ns[] = "COMMON_LIST_EVENT_DOWN (no scroll needed): index=%d"; /* ROM 0x727818 */
static const char ie_down_ns_s[] = "[common_list_container]COMMON_LIST_EVENT_DOWN (no scroll needed): index=%d"; /* ROM 0x6f22b0 */
static const char ie_down_rb[] = "COMMON_LIST_EVENT_DOWN: At last item, trigger rubber band"; /* ROM 0x712f28 */
static const char ie_down_rb_s[] = "[common_list_container]COMMON_LIST_EVENT_DOWN: At last item, trigger rubber band"; /* ROM 0x6e6a0c */
static const char ie_selected[] = "Item selected: index=%d, name=%s"; /* ROM 0x752934 */
static const char ie_selected_s[] = "[common_list_container]Item selected: index=%d, name=%s"; /* ROM 0x71cb60 */
static const char ie_up[] = "COMMON_LIST_EVENT_UP: index=%d, focus_pos=%d, scroll_offset=%d, visible_count=%d"; /* ROM 0x6e6a60 */
static const char ie_up_s[] = "[common_list_container]COMMON_LIST_EVENT_UP: index=%d, focus_pos=%d, scroll_offset=%d, visible_count=%d"; /* ROM 0x6d8794 */
static const char ie_move[] = "  -> Move focus only: new index=%d"; /* ROM 0x752958 */
static const char ie_move_s[] = "[common_list_container]  -> Move focus only: new index=%d"; /* ROM 0x712f64 */
static const char ie_scroll[] = "  -> Scroll content: new index=%d, scroll_offset=%d, target_scroll=%d"; /* ROM 0x6f8eac */
static const char ie_scroll_s[] = "[common_list_container]  -> Scroll content: new index=%d, scroll_offset=%d, target_scroll=%d"; /* ROM 0x6dce14 */
static const char ie_at_top[] = "  -> At top, move focus: new index=%d"; /* ROM 0x7483cc */
static const char ie_at_top_s[] = "[common_list_container]  -> At top, move focus: new index=%d"; /* ROM 0x709ca4 */
static const char ie_down[] = "COMMON_LIST_EVENT_DOWN: index=%d, focus_pos=%d, scroll_offset=%d, visible_count=%d"; /* ROM 0x6e6ab4 */
static const char ie_down_s[] = "[common_list_container]COMMON_LIST_EVENT_DOWN: index=%d, focus_pos=%d, scroll_offset=%d, visible_count=%d"; /* ROM 0x6a7e34 */
static const char ie_at_bottom[] = "  -> At bottom, move focus: new index=%d"; /* ROM 0x73cae0 */
static const char ie_at_bottom_s[] = "[common_list_container]  -> At bottom, move focus: new index=%d"; /* ROM 0x709ce4 */

/* Neighbours from the same stock file outside this unit (segment a-26). */
extern void list_obj_set_style_pad_all_4dccd8(void *obj, int32_t value, uint32_t selector);
extern int32_t list_item_y_position_4dcd0a(const common_list_t *list, int32_t index);
extern uint32_t get_color_from_index_4dcd32(uint32_t color_index);

void common_list_clear_focus_border_4dcd92(common_list_t *list);
void common_list_update_focus_style_4dcdbe(common_list_t *list);
int32_t common_list_calc_target_scroll_4dceb0(const common_list_t *list, int32_t index);
void common_list_scroll_anim_exec_cb_4dcec8(void *obj, int32_t value);
void common_list_scroll_anim_complete_cb_4dced2(cc_anim_t *anim);
void common_list_start_scroll_anim_4dcfe6(common_list_t *list, int32_t target_y, int32_t duration);
void common_list_rubber_band_anim_exec_cb_4dd052(void *obj, int32_t value);
void common_list_rubber_band_anim_cb_4dd05a(cc_anim_t *anim);
void common_list_trigger_rubber_band_4dd1c4(common_list_t *list, uint8_t is_top);
void common_list_focus_change_anim_exec_cb_4dd31e(void *obj, int32_t value);
void common_list_focus_change_anim_cb_4dd320(cc_anim_t *anim);
void common_list_start_focus_change_anim_4dd414(common_list_t *list);
common_list_t *common_list_container_create_4dd510(void *parent, const common_list_config_t *config,
                                                   common_list_event_cb_t event_cb, void *user_data);
void common_list_destroy_4de17c(common_list_t *list);
int32_t common_list_container_inject_event_4de354(common_list_t *list, uint8_t event);

/* Remove the focus border from the currently focused item. */
void common_list_clear_focus_border_4dcd92(common_list_t *list)
{
    if (list != NULL && list->current_index >= 0 && list->current_index < list->item_count &&
        list->items[list->current_index] != NULL)
        audio_uart_page_44131c(list->items[list->current_index], 0, 0);
}

/* Restyle every item: the focused one gets a dark fill, white text and (border_en) a white
 * 1-pixel border; the others are transparent with grey 0x444444 text. */
void common_list_update_focus_style_4dcdbe(common_list_t *list)
{
    int32_t i;

    if (list == NULL || list->scroll_container == NULL)
        return;
    for (i = 0; i < list->item_count; i++) {
        void *label;

        if (list->items[i] == NULL)
            continue;
        label = audio_uart_lv_child_get_44dce2(list->items[i], 0);
        if (i == list->current_index) {
            audio_uart_page_44129e(list->items[i], 50u, 0);
            audio_uart_page_44127e(list->items[i], audio_uart_page_44104c(0x000000u), 0);
            if (list->border_en == 0u) {
                audio_uart_page_44131c(list->items[i], 0, 0);
            } else {
                audio_uart_page_44131c(list->items[i], 1, 0);
                audio_uart_page_4412ec(list->items[i], audio_uart_page_44104c(0xffffffu), 0);
            }
            if (label != NULL)
                audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0);
        } else {
            audio_uart_page_44129e(list->items[i], 0u, 0);
            audio_uart_page_44131c(list->items[i], 0, 0);
            if (label != NULL)
                audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0);
        }
        audio_uart_display_audio_reset_441488(list->items[i], 0xffu, 0);
    }
}

/* Scroll position that keeps the focused item in the third row. */
int32_t common_list_calc_target_scroll_4dceb0(const common_list_t *list, int32_t index)
{
    int32_t target;

    if (list == NULL)
        return 0;
    target = index * COMMON_LIST_ITEM_HEIGHT - 2 * COMMON_LIST_ITEM_HEIGHT;
    if (target < 0)
        target = 0;
    return target;
}

void common_list_scroll_anim_exec_cb_4dcec8(void *obj, int32_t value)
{
    audio_uart_lv_scroll_to_y_44ea04(obj, value, LV_ANIM_OFF);
}

/* Shared tail of the three animation callbacks: replay one event queued while busy. */
#define CL_REPLAY_CACHED(list, func, line_cached, line_reinject, cached, cached_s, reinject,       \
                         reinject_s)                                                               \
    do {                                                                                           \
        uint8_t event_;                                                                            \
        (list)->anim_busy = 0u;                                                                    \
        if (ui_common_api_fn_00509dfa((list)->fifo) == 0) {                                        \
            CC_LOG(4, (func), (line_cached), 0x10000000u, (cached), (cached_s));                   \
            if (ui_common_api_fn_00509e14((list)->fifo, &event_, 1u) > 0) {                        \
                CC_LOG(4, (func), (line_reinject), 0x10400000u, (reinject), (reinject_s), event_); \
                (void)common_list_container_inject_event_4de354((list), event_);                   \
            }                                                                                      \
        }                                                                                          \
    } while (0)

/* common_list_scroll_anim_complete_cb (no inventory row; completed_cb of the scroll animation). */
void common_list_scroll_anim_complete_cb_4dced2(cc_anim_t *anim)
{
    common_list_t *list = (common_list_t *)anim->user_data;

    CC_LOG(4, fn_scroll_done, 0xfcu, 0x10000000u, sd_done, sd_done_s);
    common_list_update_focus_style_4dcdbe(list);
    CL_REPLAY_CACHED(list, fn_scroll_done, 0x106u, 0x10au, sd_cached, sd_cached_s, sd_reinject,
                     sd_reinject_s);
}

void common_list_start_scroll_anim_4dcfe6(common_list_t *list, int32_t target_y, int32_t duration)
{
    cc_anim_t a;

    if (list == NULL || list->scroll_container == NULL)
        return;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = list->scroll_container;
    audio_uart_lv_anim_values_4506ce(&a, audio_uart_lv_obj_y_44e498(list->scroll_container), target_y);
    a.duration = duration;
    a.exec_cb = common_list_scroll_anim_exec_cb_4dcec8;
    a.path_cb = audio_uart_lv_anim_path_450688;
    a.completed_cb = common_list_scroll_anim_complete_cb_4dced2;
    a.user_data = list;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Rubber-band exec_cb (no inventory row): moves the content container. */
void common_list_rubber_band_anim_exec_cb_4dd052(void *obj, int32_t value)
{
    audio_uart_page_43f142(obj, value);
}

/* common_list_rubber_band_anim_cb (no inventory row). */
void common_list_rubber_band_anim_cb_4dd05a(cc_anim_t *anim)
{
    common_list_t *list = (common_list_t *)anim->user_data;
    int32_t y;

    CC_LOG(4, fn_rubber_done, 0x131u, 0x10000000u, rb_done, rb_done_s);
    if (list->content_container != NULL) {
        y = audio_uart_lv_obj_y_43fce0(list->content_container);
        if (y != 0) {
            CC_LOG(4, fn_rubber_done, 0x137u, 0x10400000u, rb_reset, rb_reset_s, y);
            audio_uart_page_43f142(list->content_container, 0);
        }
    }
    CL_REPLAY_CACHED(list, fn_rubber_done, 0x141u, 0x145u, rb_cached, rb_cached_s, rb_reinject,
                     rb_reinject_s);
}

/* common_list_trigger_rubber_band: bounce the content 16 px past the first/last item and back
 * (150 ms out, 150 ms reverse, ease-out). */
void common_list_trigger_rubber_band_4dd1c4(common_list_t *list, uint8_t is_top)
{
    cc_anim_t a;
    int32_t y;
    int32_t normal_y;
    int32_t stretch_y;

    if (list == NULL || list->scroll_container == NULL || list->content_container == NULL)
        return;
    y = audio_uart_lv_obj_y_43fce0(list->content_container);
    if (y != 0) {
        CC_LOG(2, fn_rubber, 0x156u, 0x8400000u, tr_not_zero, tr_not_zero_s, y);
        audio_uart_page_43f142(list->content_container, 0);
    }
    normal_y = 0;
    if (is_top != 0u) {
        stretch_y = 16;
        CC_LOG(4, fn_rubber, 0x160u, 0x10800000u, tr_top, tr_top_s, normal_y, stretch_y);
    } else {
        stretch_y = -16;
        CC_LOG(4, fn_rubber, 0x164u, 0x10800000u, tr_bottom, tr_bottom_s, normal_y, stretch_y);
    }
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = list->content_container;
    audio_uart_lv_anim_values_4506ce(&a, normal_y, stretch_y);
    a.duration = 150;
    a.exec_cb = common_list_rubber_band_anim_exec_cb_4dd052;
    a.path_cb = audio_uart_lv_anim_path_450672;
    a.reverse_duration = 150u;
    a.reverse_delay = 0u;
    a.completed_cb = common_list_rubber_band_anim_cb_4dd05a;
    a.user_data = list;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* Focus-change delay exec_cb (no inventory row): the animation only times 200 ms. */
void common_list_focus_change_anim_exec_cb_4dd31e(void *obj, int32_t value)
{
    (void)obj;
    (void)value;
}

/* common_list_focus_change_anim_cb */
void common_list_focus_change_anim_cb_4dd320(cc_anim_t *anim)
{
    common_list_t *list = (common_list_t *)anim->user_data;

    CC_LOG(4, fn_focus_done, 0x185u, 0x10000000u, fc_done, fc_done_s);
    CL_REPLAY_CACHED(list, fn_focus_done, 0x18cu, 0x190u, fc_cached, fc_cached_s, fc_reinject,
                     fc_reinject_s);
}

/* Hold off further events for 200 ms after a focus move. */
void common_list_start_focus_change_anim_4dd414(common_list_t *list)
{
    cc_anim_t a;

    if (list == NULL)
        return;
    audio_uart_lv_anim_init_4503d6(&a);
    a.var = list;
    audio_uart_lv_anim_values_4506ce(&a, 0, 1);
    a.duration = 200;
    a.exec_cb = common_list_focus_change_anim_exec_cb_4dd31e;
    a.completed_cb = common_list_focus_change_anim_cb_4dd320;
    a.user_data = list;
    (void)audio_uart_lv_anim_start_450408(&a);
}

/* common_list_create */
common_list_t *common_list_container_create_4dd510(void *parent, const common_list_config_t *config,
                                                   common_list_event_cb_t event_cb, void *user_data)
{
    common_list_config_t cfg;
    common_list_t *list;
    uint32_t color;
    int32_t total_items;
    int32_t actual_content;
    int32_t visible_height;
    int32_t extra_space;
    int32_t i;

    if (parent == NULL || config == NULL) {
        CC_LOG(1, fn_create, 0x1b5u, 0x4800000u, cr_invalid, cr_invalid_s, parent, config);
        return NULL;
    }
    if (config->item_count == 0u || config->item_count > COMMON_LIST_MAX_ITEMS) {
        CC_LOG(1, fn_create, 0x1bbu, 0x4800000u, cr_count, cr_count_s, config->item_count,
               COMMON_LIST_MAX_ITEMS);
        return NULL;
    }
    (void)aeabi_memcpy4_439c04(&cfg, config, sizeof(cfg));
    if (cfg.x > CC_SCREEN_W) {
        CC_LOG(2, fn_create, 0x1c4u, 0x8400000u, cr_x, cr_x_s, cfg.x);
        cfg.x = CC_SCREEN_W;
    }
    if (cfg.y > CC_SCREEN_H) {
        CC_LOG(2, fn_create, 0x1cau, 0x8400000u, cr_y, cr_y_s, cfg.y);
        cfg.y = CC_SCREEN_H;
    }
    if (cfg.width > CC_SCREEN_W) {
        CC_LOG(2, fn_create, 0x1d0u, 0x8400000u, cr_w, cr_w_s, cfg.width);
        cfg.width = CC_SCREEN_W;
    }
    if (cfg.height > CC_SCREEN_H) {
        CC_LOG(2, fn_create, 0x1d6u, 0x8400000u, cr_h, cr_h_s, cfg.height);
        cfg.height = CC_SCREEN_H;
    }
    if (cfg.border_width > CC_MAX_BORDER_WIDTH) {
        CC_LOG(2, fn_create, 0x1dcu, 0x8400000u, cr_bw, cr_bw_s, cfg.border_width);
        cfg.border_width = CC_MAX_BORDER_WIDTH;
    }
    if (cfg.border_color > CC_MAX_BORDER_COLOR) {
        CC_LOG(2, fn_create, 0x1e2u, 0x8400000u, cr_bc, cr_bc_s, cfg.border_color);
        cfg.border_color = CC_MAX_BORDER_COLOR;
    }
    if (cfg.border_radius > CC_MAX_BORDER_RADIUS) {
        CC_LOG(2, fn_create, 0x1e8u, 0x8400000u, cr_br, cr_br_s, cfg.border_radius);
        cfg.border_radius = CC_MAX_BORDER_RADIUS;
    }
    if (cfg.padding > CC_MAX_PADDING) {
        CC_LOG(2, fn_create, 0x1eeu, 0x8400000u, cr_pad, cr_pad_s, cfg.padding);
        cfg.padding = CC_MAX_PADDING;
    }
    if (cfg.item_count > COMMON_LIST_MAX_ITEMS) {
        CC_LOG(2, fn_create, 0x1f5u, 0x8c00000u, cr_items, cr_items_s, cfg.item_count,
               COMMON_LIST_MAX_ITEMS, COMMON_LIST_MAX_ITEMS);
        cfg.item_count = COMMON_LIST_MAX_ITEMS;
    }
    CC_LOG(4, fn_create, 0x1fdu, 0x11400000u, cr_creating, cr_creating_s, cfg.item_count, cfg.x,
           cfg.y, cfg.width, cfg.height);

    list = (common_list_t *)file_heap_allocate(sizeof(common_list_t));
    if (list == NULL) {
        CC_LOG(1, fn_create, 0x205u, 0x4000000u, cr_alloc, cr_alloc_s);
        return NULL;
    }
    (void)aeabi_memset_43c0e4(list, sizeof(common_list_t), 0);
    list->item_count = (int32_t)cfg.item_count;
    list->current_index = 0;
    list->scroll_offset = 0;
    list->anim_busy = 0u;
    list->border_en = cfg.border_en;
    for (uint32_t n = 0; n < cfg.item_count; n++) {
        (void)audio_settings_copy_text(list->names[n], cfg.item_name[n], COMMON_LIST_NAME_LEN - 1u);
        list->names[n][COMMON_LIST_NAME_LEN - 1u] = '\0';
    }
    list->event_cb = event_cb;
    list->user_data = user_data;
    list->visible_height = (int32_t)cfg.height - 2 * (int32_t)cfg.padding;
    list->visible_count = list->visible_height / COMMON_LIST_ITEM_HEIGHT;
    if (list->visible_count < 1)
        list->visible_count = 1;
    CC_LOG(4, fn_create, 0x222u, 0x10c00000u, cr_visible, cr_visible_s, list->visible_height,
           list->visible_count, list->border_en);

    list->fifo = ui_common_api_fn_00509c1c();
    if (list->fifo == NULL) {
        CC_LOG(1, fn_create, 0x227u, 0x4000000u, cr_fifo, cr_fifo_s);
        file_heap_free(list);
        return NULL;
    }
    CC_LOG(4, fn_create, 0x22bu, 0x10000000u, cr_fifo_note, cr_fifo_note_s);

    list->scroll_container = audio_uart_page_43de82(parent);
    if (list->scroll_container == NULL) {
        CC_LOG(1, fn_create, 0x230u, 0x4000000u, cr_scroll_fail, cr_scroll_fail_s);
        ui_common_api_fn_00509c96(list->fifo);
        file_heap_free(list);
        return NULL;
    }
    audio_uart_page_43f506(list->scroll_container, (int32_t)cfg.width);
    audio_uart_page_43f568(list->scroll_container, (int32_t)cfg.height);
    audio_uart_page_43f0e0(list->scroll_container, (int32_t)cfg.x);
    audio_uart_page_43f142(list->scroll_container, (int32_t)cfg.y);
    audio_uart_page_44e368(list->scroll_container, LV_SCROLLBAR_MODE_OFF);
    audio_uart_page_44e3ca(list->scroll_container, LV_DIR_VER);
    audio_uart_page_44129e(list->scroll_container, 0u, 0);
    audio_uart_page_44146a(list->scroll_container, (int32_t)cfg.border_radius, 0);
    if (cfg.border_width == 0u) {
        audio_uart_page_44131c(list->scroll_container, 0, 0);
    } else {
        audio_uart_page_44131c(list->scroll_container, (int32_t)cfg.border_width, 0);
        color = get_color_from_index_4dcd32(cfg.border_color);
        audio_uart_page_4412ec(list->scroll_container, audio_uart_page_44104c(color), 0);
        CC_LOG(4, fn_create, 0x245u, 0x10800000u, cr_border, cr_border_s, cfg.border_width, color);
    }
    audio_uart_page_44120e(list->scroll_container, (int32_t)cfg.padding, 0);
    audio_uart_page_44121c(list->scroll_container, (int32_t)cfg.padding, 0);
    audio_uart_page_44122a(list->scroll_container, (int32_t)cfg.padding, 0);
    audio_uart_page_441238(list->scroll_container, (int32_t)cfg.padding, 0);

    total_items = (int32_t)cfg.item_count;
    actual_content = total_items * COMMON_LIST_ITEM_HEIGHT;
    visible_height = (int32_t)cfg.height - 2 * (int32_t)cfg.padding;
    CC_LOG(4, fn_create, 0x258u, 0x10c00000u, cr_actual, cr_actual_s, actual_content,
           visible_height, total_items);
    if (visible_height >= actual_content) {
        /* Everything fits: items are centered vertically (see common_list_calc_item_y). */
        actual_content = visible_height + 16;
        list->no_scroll = 1u;
        CC_LOG(4, fn_create, 0x25fu, 0x10400000u, cr_no_scroll, cr_no_scroll_s, actual_content);
    } else {
        extra_space = (visible_height < (visible_height / COMMON_LIST_ITEM_HEIGHT) *
                                            COMMON_LIST_ITEM_HEIGHT)
                          ? 44
                          : 0;
        extra_space += 16;
        actual_content = extra_space + actual_content;
        list->no_scroll = 0u;
        CC_LOG(4, fn_create, 0x26au, 0x10800000u, cr_scroll, cr_scroll_s, actual_content,
               extra_space);
    }

    list->content_container = audio_uart_page_43de82(list->scroll_container);
    if (list->content_container == NULL) {
        CC_LOG(1, fn_create, 0x26fu, 0x4000000u, cr_content_fail, cr_content_fail_s);
        audio_uart_page_delete_event_filter_44d7b8(list->scroll_container);
        ui_common_api_fn_00509c96(list->fifo);
        file_heap_free(list);
        return NULL;
    }
    audio_uart_page_43f506(list->content_container, (int32_t)cfg.width);
    audio_uart_page_43f568(list->content_container, actual_content);
    audio_uart_page_43f0e0(list->content_container, 0);
    audio_uart_page_43f142(list->content_container, 0);
    audio_uart_page_44129e(list->content_container, 0u, 0);
    audio_uart_page_44131c(list->content_container, 0, 0);
    list_obj_set_style_pad_all_4dccd8(list->content_container, 0, 0);
    audio_uart_page_43dfa4(list->content_container, LV_OBJ_FLAG_SCROLLABLE);

    CC_LOG(4, fn_create, 0x281u, 0x10400000u, cr_creating_items, cr_creating_items_s, total_items);
    for (i = 0; i < total_items; i++) {
        void *label;

        list->items[i] = audio_uart_page_43de82(list->content_container);
        if (list->items[i] == NULL) {
            CC_LOG(1, fn_create, 0x287u, 0x4400000u, cr_item_fail, cr_item_fail_s, i);
            audio_uart_page_delete_event_filter_44d7b8(list->scroll_container);
            ui_common_api_fn_00509c96(list->fifo);
            file_heap_free(list);
            return NULL;
        }
        audio_uart_page_44122a(list->items[i], 12, 0);
        audio_uart_page_441238(list->items[i], 12, 0);
        if (cfg.item_width == 0)
            audio_uart_page_43f4c0(list->items[i], LV_SIZE_CONTENT, COMMON_LIST_ITEM_HEIGHT);
        else
            audio_uart_page_43f4c0(list->items[i], cfg.item_width, COMMON_LIST_ITEM_HEIGHT);
        audio_uart_page_43f0e0(list->items[i], 0);
        audio_uart_page_43f142(list->items[i], list_item_y_position_4dcd0a(list, i));
        audio_uart_page_44127e(list->items[i], audio_uart_page_44104c(0x000000u), 0);
        audio_uart_page_44129e(list->items[i], 0u, 0);
        audio_uart_page_44146a(list->items[i], 10, 0);
        audio_uart_page_44131c(list->items[i], 0, 0);
        audio_uart_page_43dfa4(list->items[i], LV_OBJ_FLAG_SCROLLABLE);

        label = audio_uart_page_499416(list->items[i]);
        audio_uart_page_49942e(label, cfg.item_name[i]);
        audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0);
        if (cfg.item_width == 0) {
            int32_t max_width = (int32_t)cfg.width - 24;

            audio_uart_page_43f506(label, LV_SIZE_CONTENT);
            audio_uart_page_441180(label, max_width, 0);
            audio_uart_page_499678(label, LV_LABEL_LONG_DOT);
        } else {
            audio_uart_page_43f506(label, cfg.item_width - 24);
            audio_uart_page_43f568(label, LV_SIZE_CONTENT);
            audio_uart_page_4411aa(label, COMMON_LIST_ITEM_HEIGHT, 0);
            audio_uart_page_499678(label, LV_LABEL_LONG_DOT);
        }
        lv_obj_center_4409fa(label);
        if (i == 0)
            audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffffu), 0);
        else
            audio_uart_page_44140e(label, audio_uart_page_44104c(0x444444u), 0);
    }

    audio_uart_page_43f66c(parent);
    audio_uart_lv_scroll_to_y_44ea04(list->scroll_container, 0, LV_ANIM_OFF);
    common_list_update_focus_style_4dcdbe(list);
    CC_LOG(4, fn_create, 0x2dau, 0x10400000u, cr_initial, cr_initial_s, list->border_en);
    CC_LOG(3, fn_create, 0x2ddu, 0xcc00000u, cr_done, cr_done_s, total_items, cfg.x, cfg.y);
    return list;
}

/* common_list_destroy */
void common_list_destroy_4de17c(common_list_t *list)
{
    int32_t i;

    if (list == NULL) {
        CC_LOG(2, fn_destroy, 0x2e7u, 0x8000000u, de_null, de_null_s);
        return;
    }
    CC_LOG(4, fn_destroy, 0x2ebu, 0x10400000u, de_destroying, de_destroying_s, list->item_count);
    if (list->scroll_container != NULL) {
        audio_uart_page_delete_event_filter_44d7b8(list->scroll_container);
        list->scroll_container = NULL;
    }
    for (i = 0; i < (int32_t)COMMON_LIST_MAX_ITEMS; i++)
        list->items[i] = NULL;
    list->content_container = NULL;
    if (list->fifo != NULL) {
        ui_common_api_fn_00509f52(list->fifo);
        ui_common_api_fn_00509c96(list->fifo);
        list->fifo = NULL;
    }
    file_heap_free(list);
    CC_LOG(3, fn_destroy, 0x303u, 0xc000000u, de_done, de_done_s);
}

/* Focus moves that do not scroll: drop the old border, restyle, block input for 200 ms. */
#define CL_MOVE_FOCUS(list, delta, line, text, text_s)                                    \
    do {                                                                                  \
        common_list_clear_focus_border_4dcd92(list);                                      \
        (list)->current_index += (delta);                                                 \
        CC_LOG(4, fn_inject, (line), 0x10400000u, (text), (text_s), (list)->current_index); \
        common_list_update_focus_style_4dcdbe(list);                                      \
        (list)->anim_busy = 1u;                                                           \
        common_list_start_focus_change_anim_4dd414(list);                                 \
    } while (0)

/* Focus moves that scroll the content by one row (200 ms ease-in-out). */
#define CL_SCROLL(list, delta, line)                                                         \
    do {                                                                                     \
        int32_t target_;                                                                     \
        common_list_clear_focus_border_4dcd92(list);                                         \
        (list)->scroll_offset += (delta);                                                    \
        (list)->current_index += (delta);                                                    \
        target_ = common_list_calc_target_scroll_4dceb0((list), (list)->current_index);      \
        CC_LOG(4, fn_inject, (line), 0x10c00000u, ie_scroll, ie_scroll_s,                    \
               (list)->current_index, (list)->scroll_offset, target_);                       \
        (list)->anim_busy = 1u;                                                              \
        common_list_start_scroll_anim_4dcfe6((list), target_, 200);                          \
    } while (0)

/* common_list_inject_event: 0 handled (or queued), -1 error, 1 unknown event. While an
 * animation runs the event is queued in the FIFO and replayed by its completion callback. */
int32_t common_list_container_inject_event_4de354(common_list_t *list, uint8_t event)
{
    int32_t focus_pos;
    int32_t visible;
    int32_t max_scroll;

    if (list == NULL) {
        CC_LOG(1, fn_inject, 0x310u, 0x4000000u, ie_null, ie_null_s);
        return -1;
    }
    if (list->scroll_container == NULL || list->content_container == NULL) {
        CC_LOG(2, fn_inject, 0x315u, 0x8000000u, ie_not_init, ie_not_init_s);
        return -1;
    }
    if (event != COMMON_LIST_EVENT_CLICK && event != COMMON_LIST_EVENT_DOWN &&
        event != COMMON_LIST_EVENT_UP) {
        CC_LOG(2, fn_inject, 0x31bu, 0x8400000u, ie_unknown, ie_unknown_s, event);
        return 1;
    }
    if (list->anim_busy != 0u) {
        CC_LOG(4, fn_inject, 0x321u, 0x10400000u, ie_busy, ie_busy_s, event);
        if (ui_common_api_fn_00509ca2(list->fifo, &event, 1u) != 0) {
            CC_LOG(2, fn_inject, 0x324u, 0x8000000u, ie_push_fail, ie_push_fail_s);
            return -1;
        }
        return 0;
    }
    if (list->item_count < 1) {
        CC_LOG(2, fn_inject, 0x32cu, 0x8000000u, ie_no_items, ie_no_items_s);
        return -1;
    }

    visible = list->visible_count;
    if (list->item_count <= visible) {
        switch (event) {
        case COMMON_LIST_EVENT_UP:
            if (list->current_index > 0) {
                CL_MOVE_FOCUS(list, -1, 0x339u, ie_up_ns, ie_up_ns_s);
            } else {
                CC_LOG(4, fn_inject, 0x33eu, 0x10000000u, ie_up_rb, ie_up_rb_s);
                list->anim_busy = 1u;
                common_list_trigger_rubber_band_4dd1c4(list, 1u);
            }
            break;
        case COMMON_LIST_EVENT_DOWN:
            if (list->current_index < list->item_count - 1) {
                CL_MOVE_FOCUS(list, 1, 0x348u, ie_down_ns, ie_down_ns_s);
            } else {
                CC_LOG(4, fn_inject, 0x34du, 0x10000000u, ie_down_rb, ie_down_rb_s);
                list->anim_busy = 1u;
                common_list_trigger_rubber_band_4dd1c4(list, 0u);
            }
            break;
        case COMMON_LIST_EVENT_CLICK:
            CC_LOG(3, fn_inject, 0x355u, 0xc800000u, ie_selected, ie_selected_s,
                   list->current_index, list->names[list->current_index]);
            if (list->event_cb != NULL)
                (void)list->event_cb(list->current_index, list->names[list->current_index],
                                     list->user_data);
            break;
        default:
            CC_LOG(2, fn_inject, 0x361u, 0x8400000u, ie_unknown, ie_unknown_s, event);
            break;
        }
        return 0;
    }

    /* More items than rows: keep the focus inside the window, scrolling when it reaches the
     * second row from the top / bottom edge. */
    focus_pos = list->current_index - list->scroll_offset;
    switch (event) {
    case COMMON_LIST_EVENT_UP:
        if (list->current_index > 0) {
            CC_LOG(4, fn_inject, 0x375u, 0x11000000u, ie_up, ie_up_s, list->current_index,
                   focus_pos, list->scroll_offset, visible);
            if (focus_pos > 1) {
                CL_MOVE_FOCUS(list, -1, 0x37bu, ie_move, ie_move_s);
            } else if (focus_pos == 1) {
                if (list->scroll_offset > 0)
                    CL_SCROLL(list, -1, 0x388u);
                else
                    CL_MOVE_FOCUS(list, -1, 0x38fu, ie_at_top, ie_at_top_s);
            } else {
                CL_MOVE_FOCUS(list, -1, 0x398u, ie_move, ie_move_s);
            }
        } else {
            CC_LOG(4, fn_inject, 0x39fu, 0x10000000u, ie_up_rb, ie_up_rb_s);
            list->anim_busy = 1u;
            common_list_trigger_rubber_band_4dd1c4(list, 1u);
        }
        break;
    case COMMON_LIST_EVENT_DOWN:
        if (list->current_index < list->item_count - 1) {
            CC_LOG(4, fn_inject, 0x3a9u, 0x11000000u, ie_down, ie_down_s, list->current_index,
                   focus_pos, list->scroll_offset, visible);
            if (focus_pos < visible - 2) {
                CL_MOVE_FOCUS(list, 1, 0x3afu, ie_move, ie_move_s);
            } else if (focus_pos == visible - 2) {
                max_scroll = list->item_count - visible;
                if (max_scroll < 0)
                    max_scroll = 0;
                if (list->scroll_offset < max_scroll)
                    CL_SCROLL(list, 1, 0x3bfu);
                else
                    CL_MOVE_FOCUS(list, 1, 0x3c6u, ie_at_bottom, ie_at_bottom_s);
            } else {
                CL_MOVE_FOCUS(list, 1, 0x3cfu, ie_move, ie_move_s);
            }
        } else {
            CC_LOG(4, fn_inject, 0x3d6u, 0x10000000u, ie_down_rb, ie_down_rb_s);
            list->anim_busy = 1u;
            common_list_trigger_rubber_band_4dd1c4(list, 0u);
        }
        break;
    case COMMON_LIST_EVENT_CLICK:
        CC_LOG(3, fn_inject, 0x3deu, 0xc800000u, ie_selected, ie_selected_s, list->current_index,
               list->names[list->current_index]);
        if (list->event_cb != NULL)
            (void)list->event_cb(list->current_index, list->names[list->current_index],
                                 list->user_data);
        break;
    default:
        CC_LOG(2, fn_inject, 0x3eau, 0x8400000u, ie_unknown, ie_unknown_s, event);
        break;
    }
    return 0;
}

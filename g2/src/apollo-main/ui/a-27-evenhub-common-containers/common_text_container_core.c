/* EvenHub common text container, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\common_text_container.c (log tag
 * "common_text_container"). Native 0x4dee64..0x4df84f and 0x4df858..0x4df965; literal pools
 * 0x4df850..0x4df857, 0x4df968..0x4df97b, 0x4dfa08..0x4dfa2b, 0x4dfb5c..0x4dfb77,
 * 0x4dfc98..0x4dfcb7, 0x4dfe3c..0x4dfe4f, 0x4dffc8..0x4dffef, 0x4e0288..0x4e02af (shared with
 * the scroll/event half of the file, 0x4df97c.., reconstructed separately).
 *
 * A text container is a fixed window (scroll_container, vertical scrollbar on demand) holding a
 * content container of LV_SIZE_CONTENT height with one wrapping label; the handle keeps a copy of
 * the text and the scroll state (scrollable, max_scroll_y, at_top, at_bottom) used by the
 * event-injection code. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "common_containers_private.h"

static const char cc_tag[] = "common_text_container"; /* ROM 0x775a7c */
static const char cc_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\common_text_container.c"; /* ROM 0x6f22fc */
static const char fn_create[] = "common_text_create"; /* ROM 0x77e960 */
static const char fn_destroy[] = "common_text_destroy"; /* ROM 0x77e974 */
static const char fn_color[] = "get_color_from_index"; /* ROM 0x775a94 */
static const char fn_update[] = "common_text_update_scroll_state"; /* ROM 0x75e770 */
static const char cr_invalid[] = "common_text_create: invalid parameters (parent=%p, config=%p)"; /* ROM 0x709d64 */
static const char cr_invalid_s[] = "[common_text_container]common_text_create: invalid parameters (parent=%p, config=%p)"; /* ROM 0x6e2960 */
static const char cr_x[] = "common_text_create: x_position %d > 576, clamping to 576"; /* ROM 0x712fa0 */
static const char cr_x_s[] = "[common_text_container]common_text_create: x_position %d > 576, clamping to 576"; /* ROM 0x6ebf88 */
static const char cr_y[] = "common_text_create: y_position %d > 288, clamping to 288"; /* ROM 0x712fdc */
static const char cr_y_s[] = "[common_text_container]common_text_create: y_position %d > 288, clamping to 288"; /* ROM 0x6ebfd8 */
static const char cr_w[] = "common_text_create: width %d > 576, clamping to 576"; /* ROM 0x72784c */
static const char cr_w_s[] = "[common_text_container]common_text_create: width %d > 576, clamping to 576"; /* ROM 0x6f2348 */
static const char cr_h[] = "common_text_create: height %d > 288, clamping to 288"; /* ROM 0x71cb98 */
static const char cr_h_s[] = "[common_text_container]common_text_create: height %d > 288, clamping to 288"; /* ROM 0x6f2394 */
static const char cr_bw[] = "common_text_create: border_width %d > 5, clamping to 5"; /* ROM 0x71cbd0 */
static const char cr_bw_s[] = "[common_text_container]common_text_create: border_width %d > 5, clamping to 5"; /* ROM 0x6ec028 */
static const char cr_bc[] = "common_text_create: border_color %d > 16, clamping to 16"; /* ROM 0x713018 */
static const char cr_bc_s[] = "[common_text_container]common_text_create: border_color %d > 16, clamping to 16"; /* ROM 0x6ec078 */
static const char cr_br[] = "common_text_create: border_radius %d > 10, clamping to 10"; /* ROM 0x713054 */
static const char cr_br_s[] = "[common_text_container]common_text_create: border_radius %d > 10, clamping to 10"; /* ROM 0x6e6b08 */
static const char cr_pad[] = "common_text_create: padding %d > 32, clamping to 32"; /* ROM 0x727880 */
static const char cr_pad_s[] = "[common_text_container]common_text_create: padding %d > 32, clamping to 32"; /* ROM 0x6f23e0 */
static const char cr_creating[] = "common_text_create: creating text at pos(%d,%d) size(%dx%d)"; /* ROM 0x713090 */
static const char cr_creating_s[] = "[common_text_container]common_text_create: creating text at pos(%d,%d) size(%dx%d)"; /* ROM 0x6e6b5c */
static const char cr_alloc[] = "common_text_create: failed to allocate handle"; /* ROM 0x732084 */
static const char cr_alloc_s[] = "[common_text_container]common_text_create: failed to allocate handle"; /* ROM 0x6f8ef4 */
static const char cr_fifo[] = "common_text_create: failed to create fifo_handle"; /* ROM 0x7278b4 */
static const char cr_fifo_s[] = "[common_text_container]common_text_create: failed to create fifo_handle"; /* ROM 0x6f8f3c */
static const char cr_fifo_ok[] = "common_text_create: FIFO queue created"; /* ROM 0x7483f4 */
static const char cr_fifo_ok_s[] = "[common_text_container]common_text_create: FIFO queue created"; /* ROM 0x709da4 */
static const char cr_scroll_fail[] = "common_text_create: failed to create scroll_container"; /* ROM 0x71cc08 */
static const char cr_scroll_fail_s[] = "[common_text_container]common_text_create: failed to create scroll_container"; /* ROM 0x6ec0c8 */
static const char cr_border[] = "common_text_create: border enabled (width=%d, color=0x%06X)"; /* ROM 0x7130cc */
static const char cr_border_s[] = "[common_text_container]common_text_create: border enabled (width=%d, color=0x%06X)"; /* ROM 0x6e6bb0 */
static const char cr_content_fail[] = "common_text_create: failed to create content_container"; /* ROM 0x71cc40 */
static const char cr_content_fail_s[] = "[common_text_container]common_text_create: failed to create content_container"; /* ROM 0x6ec118 */
static const char cr_label_fail[] = "common_text_create: failed to create text_label"; /* ROM 0x7320b4 */
static const char cr_label_fail_s[] = "[common_text_container]common_text_create: failed to create text_label"; /* ROM 0x6f8f84 */
static const char cr_done[] = "common_text_create: text created successfully at (%d,%d)"; /* ROM 0x713108 */
static const char cr_done_s[] = "[common_text_container]common_text_create: text created successfully at (%d,%d)"; /* ROM 0x6ec168 */
static const char de_null[] = "common_text_destroy: handle is NULL"; /* ROM 0x75297c */
static const char de_null_s[] = "[common_text_container]common_text_destroy: handle is NULL"; /* ROM 0x713144 */
static const char de_destroying[] = "common_text_destroy: destroying text container"; /* ROM 0x7320e4 */
static const char de_destroying_s[] = "[common_text_container]common_text_destroy: destroying text container"; /* ROM 0x6f8fcc */
static const char de_done[] = "common_text_destroy: text destroyed"; /* ROM 0x7529a0 */
static const char de_done_s[] = "[common_text_container]common_text_destroy: text destroyed"; /* ROM 0x713180 */
static const char co_invalid[] = "get_color_from_index: invalid color_index %d, using white"; /* ROM 0x7131bc */
static const char co_invalid_s[] = "[common_text_container]get_color_from_index: invalid color_index %d, using white"; /* ROM 0x6e6c04 */
static const char us_invalid[] = "common_text_update_scroll_state: scroll_container is invalid"; /* ROM 0x709de4 */
static const char us_invalid_s[] = "[common_text_container]common_text_update_scroll_state: scroll_container is invalid"; /* ROM 0x6e6c58 */
static const char us_state[] = "common_text_update_scroll_state: scrollable=%d, max_scroll_y=%d, at_top=%d, at_bottom=%d"; /* ROM 0x6dfaac */
static const char us_state_s[] = "[common_text_container]common_text_update_scroll_state: scrollable=%d, max_scroll_y=%d, at_top=%d, at_bottom=%d"; /* ROM 0x6d6cc0 */

/* Border grey levels, index 0..15 (ROM 0x709f24; the list file keeps its own copy at 0x709d24). */
static const uint32_t text_color_table[16] = {
    0x000000u, 0x111111u, 0x222222u, 0x333333u, 0x444444u, 0x555555u, 0x666666u, 0x777777u,
    0x888888u, 0x999999u, 0xaaaaaau, 0xbbbbbbu, 0xccccccu, 0xddddddu, 0xeeeeeeu, 0xffffffu,
};

void common_text_set_style_pad_all_4dee64(void *obj, int32_t value, uint32_t selector);
common_text_t *common_text_container_create_4dee96(void *parent, const common_text_config_t *config,
                                                   common_text_event_cb_t event_cb, void *user_data);
void common_text_destroy_4df6ee(common_text_t *text);
uint32_t common_text_get_color_from_index_4df7f2(uint32_t color_index);
void common_text_update_scroll_state_4df858(common_text_t *text);

void common_text_set_style_pad_all_4dee64(void *obj, int32_t value, uint32_t selector)
{
    audio_uart_page_44122a(obj, value, selector);
    audio_uart_page_441238(obj, value, selector);
    audio_uart_page_44120e(obj, value, selector);
    audio_uart_page_44121c(obj, value, selector);
}

/* common_text_create: a scrollable window (scrollbar on demand, 4 px white scrollbar at 180 opa)
 * holding a content container with one wrapping label. */
common_text_t *common_text_container_create_4dee96(void *parent, const common_text_config_t *config,
                                                   common_text_event_cb_t event_cb, void *user_data)
{
    common_text_config_t cfg;
    common_text_t *text;
    uint32_t color;

    if (parent == NULL || config == NULL) {
        CC_LOG(1, fn_create, 0x6du, 0x4800000u, cr_invalid, cr_invalid_s, parent, config);
        return NULL;
    }
    (void)aeabi_memcpy4_439c04(&cfg, config, sizeof(cfg));
    if (cfg.x > CC_SCREEN_W) {
        CC_LOG(2, fn_create, 0x76u, 0x8400000u, cr_x, cr_x_s, (int32_t)cfg.x);
        cfg.x = CC_SCREEN_W;
    }
    if (cfg.y > CC_SCREEN_H) {
        CC_LOG(2, fn_create, 0x7cu, 0x8400000u, cr_y, cr_y_s, (int32_t)cfg.y);
        cfg.y = CC_SCREEN_H;
    }
    if (cfg.width > CC_SCREEN_W) {
        CC_LOG(2, fn_create, 0x82u, 0x8400000u, cr_w, cr_w_s, (int32_t)cfg.width);
        cfg.width = CC_SCREEN_W;
    }
    if (cfg.height > CC_SCREEN_H) {
        CC_LOG(2, fn_create, 0x88u, 0x8400000u, cr_h, cr_h_s, (int32_t)cfg.height);
        cfg.height = CC_SCREEN_H;
    }
    if (cfg.border_width > CC_MAX_BORDER_WIDTH) {
        CC_LOG(2, fn_create, 0x8eu, 0x8400000u, cr_bw, cr_bw_s, cfg.border_width);
        cfg.border_width = CC_MAX_BORDER_WIDTH;
    }
    if (cfg.border_color > CC_MAX_BORDER_COLOR) {
        CC_LOG(2, fn_create, 0x94u, 0x8400000u, cr_bc, cr_bc_s, cfg.border_color);
        cfg.border_color = CC_MAX_BORDER_COLOR;
    }
    if (cfg.border_radius > CC_MAX_BORDER_RADIUS) {
        CC_LOG(2, fn_create, 0x9au, 0x8400000u, cr_br, cr_br_s, cfg.border_radius);
        cfg.border_radius = CC_MAX_BORDER_RADIUS;
    }
    if (cfg.padding > CC_MAX_PADDING) {
        CC_LOG(2, fn_create, 0xa0u, 0x8400000u, cr_pad, cr_pad_s, cfg.padding);
        cfg.padding = CC_MAX_PADDING;
    }
    CC_LOG(4, fn_create, 0xa6u, 0x11000000u, cr_creating, cr_creating_s, (int32_t)cfg.x,
           (int32_t)cfg.y, (int32_t)cfg.width, (int32_t)cfg.height);

    text = (common_text_t *)file_heap_allocate(sizeof(common_text_t));
    if (text == NULL) {
        CC_LOG(1, fn_create, 0xaeu, 0x4000000u, cr_alloc, cr_alloc_s);
        return NULL;
    }
    (void)aeabi_memset_43c0e4(text, sizeof(common_text_t), 0);
    text->anim_busy = 0u;
    text->anim_target = NULL;
    text->visible_height = (int32_t)cfg.height - 2 * (int32_t)cfg.padding;
    text->event_cb = event_cb;
    text->user_data = user_data;
    text->fifo = ui_common_api_fn_00509c1c();
    if (text->fifo == NULL) {
        CC_LOG(1, fn_create, 0xbfu, 0x4000000u, cr_fifo, cr_fifo_s);
        file_heap_free(text);
        return NULL;
    }
    CC_LOG(4, fn_create, 0xc3u, 0x10000000u, cr_fifo_ok, cr_fifo_ok_s);

    text->scroll_container = audio_uart_page_43de82(parent);
    if (text->scroll_container == NULL) {
        CC_LOG(1, fn_create, 0xc8u, 0x4000000u, cr_scroll_fail, cr_scroll_fail_s);
        ui_common_api_fn_00509c96(text->fifo);
        file_heap_free(text);
        return NULL;
    }
    audio_uart_page_43f506(text->scroll_container, cfg.width);
    audio_uart_page_43f568(text->scroll_container, cfg.height);
    audio_uart_page_43f0e0(text->scroll_container, cfg.x);
    audio_uart_page_43f142(text->scroll_container, cfg.y);
    audio_uart_page_44e368(text->scroll_container, LV_SCROLLBAR_MODE_AUTO);
    audio_uart_page_44e3ca(text->scroll_container, LV_DIR_VER);
    audio_uart_page_44129e(text->scroll_container, 0u, 0);
    audio_uart_page_44146a(text->scroll_container, cfg.border_radius, 0);
    if (cfg.border_width == 0u) {
        audio_uart_page_44131c(text->scroll_container, 0, 0);
    } else {
        audio_uart_page_44131c(text->scroll_container, cfg.border_width, 0);
        color = common_text_get_color_from_index_4df7f2(cfg.border_color);
        audio_uart_page_4412ec(text->scroll_container, audio_uart_page_44104c(color), 0);
        CC_LOG(4, fn_create, 0xddu, 0x10800000u, cr_border, cr_border_s, cfg.border_width, color);
    }
    audio_uart_page_44120e(text->scroll_container, cfg.padding, 0);
    audio_uart_page_44121c(text->scroll_container, cfg.padding, 0);
    audio_uart_page_44122a(text->scroll_container, cfg.padding, 0);
    audio_uart_page_441238(text->scroll_container, cfg.padding, 0);
    audio_uart_page_44127e(text->scroll_container, audio_uart_page_44104c(0xffffffu),
                           LV_PART_SCROLLBAR);
    audio_uart_page_44129e(text->scroll_container, 0xb4u, LV_PART_SCROLLBAR);
    audio_uart_page_441164(text->scroll_container, 4, LV_PART_SCROLLBAR);

    text->content_container = audio_uart_page_43de82(text->scroll_container);
    if (text->content_container == NULL) {
        CC_LOG(1, fn_create, 0xf0u, 0x4000000u, cr_content_fail, cr_content_fail_s);
        audio_uart_page_delete_event_filter_44d7b8(text->scroll_container);
        ui_common_api_fn_00509c96(text->fifo);
        file_heap_free(text);
        return NULL;
    }
    audio_uart_page_43f506(text->content_container, cfg.width - 2 * (int32_t)cfg.padding);
    audio_uart_page_43f568(text->content_container, LV_SIZE_CONTENT);
    audio_uart_page_43f0e0(text->content_container, 0);
    audio_uart_page_43f142(text->content_container, 0);
    audio_uart_page_44129e(text->content_container, 0u, 0);
    audio_uart_page_44131c(text->content_container, 0, 0);
    common_text_set_style_pad_all_4dee64(text->content_container, 0, 0);
    audio_uart_page_43dfa4(text->content_container, LV_OBJ_FLAG_SCROLLABLE);

    text->text_label = audio_uart_page_499416(text->content_container);
    if (text->text_label == NULL) {
        CC_LOG(1, fn_create, 0x103u, 0x4000000u, cr_label_fail, cr_label_fail_s);
        audio_uart_page_delete_event_filter_44d7b8(text->scroll_container);
        ui_common_api_fn_00509c96(text->fifo);
        file_heap_free(text);
        return NULL;
    }
    audio_uart_page_49942e(text->text_label, cfg.content);
    audio_uart_page_43f506(text->text_label, cfg.width - 2 * (int32_t)cfg.padding);
    audio_uart_page_499678(text->text_label, LV_LABEL_LONG_WRAP);
    audio_uart_page_44143e(text->text_label, audio_uart_ring_primary_head_cell, 0);
    audio_uart_page_44140e(text->text_label, audio_uart_page_44104c(cfg.text_color), 0);
    audio_uart_page_44145a(text->text_label, cfg.text_align, 0);
    (void)audio_settings_copy_text(text->text, cfg.content, COMMON_TEXT_LEN - 1u);
    text->text[COMMON_TEXT_LEN - 1u] = '\0';

    audio_uart_page_43f66c(parent);
    common_text_update_scroll_state_4df858(text);
    audio_uart_lv_scroll_to_y_44ea04(text->scroll_container, 0, LV_ANIM_OFF);
    CC_LOG(3, fn_create, 0x11fu, 0xc800000u, cr_done, cr_done_s, (int32_t)cfg.x, (int32_t)cfg.y);
    return text;
}

/* common_text_destroy (the label and content pointers are left as they are, unlike the list). */
void common_text_destroy_4df6ee(common_text_t *text)
{
    if (text == NULL) {
        CC_LOG(2, fn_destroy, 0x129u, 0x8000000u, de_null, de_null_s);
        return;
    }
    CC_LOG(4, fn_destroy, 0x12du, 0x10000000u, de_destroying, de_destroying_s);
    if (text->scroll_container != NULL) {
        audio_uart_page_delete_event_filter_44d7b8(text->scroll_container);
        text->scroll_container = NULL;
    }
    if (text->fifo != NULL) {
        ui_common_api_fn_00509f52(text->fifo);
        ui_common_api_fn_00509c96(text->fifo);
        text->fifo = NULL;
    }
    file_heap_free(text);
    CC_LOG(3, fn_destroy, 0x13fu, 0xc000000u, de_done, de_done_s);
}

/* get_color_from_index: grey level 0..15, anything else (including 16) is white. */
uint32_t common_text_get_color_from_index_4df7f2(uint32_t color_index)
{
    if (color_index < 16u)
        return text_color_table[color_index];
    CC_LOG(2, fn_color, 0x176u, 0x8400000u, co_invalid, co_invalid_s, color_index);
    return 0xffffffu;
}

/* common_text_update_scroll_state: at_top / at_bottom use a 3 px tolerance. */
void common_text_update_scroll_state_4df858(common_text_t *text)
{
    int32_t scroll_top;
    int32_t scroll_bottom;
    int32_t height;

    if (text == NULL || text->scroll_container == NULL)
        return;
    if (audio_terminal_ui_object_valid_43e2ea(text->scroll_container) == 0u) {
        CC_LOG(2, fn_update, 0x184u, 0x8000000u, us_invalid, us_invalid_s);
        return;
    }
    audio_uart_page_43f66c(text->scroll_container);
    scroll_top = audio_uart_lv_scroll_top_44e4aa(text->scroll_container);
    scroll_bottom = audio_uart_lv_scroll_bottom_44e4bc(text->scroll_container);
    height = audio_uart_lv_obj_height_43fdda(text->scroll_container);
    text->scrollable = (scroll_bottom + (scroll_top + height)) > height;
    text->max_scroll_y = scroll_bottom + scroll_top;
    text->at_top = audio_uart_lv_obj_y_44e498(text->scroll_container) < 3;
    text->at_bottom = scroll_bottom < 3;
    CC_LOG(4, fn_update, 0x19fu, 0x11000000u, us_state, us_state_s, text->scrollable,
           text->max_scroll_y, text->at_top, text->at_bottom);
}

/* Conversate tag (AI cue) extend page, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui_tag_page.c.
 * Native 0x5b5d5e..0x5b5de3, 0x5b5de4..0x5b5ed1, 0x5b5f1a..0x5b5f43,
 * 0x5b5f44..0x5b63d3, 0x5b660e..0x5b664b, 0x5b664c..0x5b6687 and
 * 0x5b6688..0x5b68d5 (literal pool 0x5b6944..0x5b69d0; animation templates
 * ROM 0x75303c / 0x753060).
 *
 * Inventory names in this range are shifted against the stock __func__
 * strings: 0x5b5d5e logs as conversate_calculate_auto_duration_by_label
 * (inventory: ..._menu_page_scroll_down, which is 0x5b5bf0) and 0x5b6688 logs
 * as conversate_ui_action_tag_to_main_page (inventory: ..._tag_manual_shrink);
 * 0x5b660e is the fade-in completion of the auto-pop close path. 0x5b5f44 and
 * 0x5b6688 keep the names the action matrix (conversate_ui_action_matrix_686920.c)
 * already links against. */
#include <stdint.h>
#include <stddef.h>
#include "conversate_ui_context.h"

#define LOG_MODULE module
#define LOG_PATH path

/* expand_anim.c configuration (0x24 bytes) consumed by 0x5b7704. */
typedef struct {
    uint16_t duration; /* +0x00 ms, 0 = 250 */
    uint16_t delay;    /* +0x02 ms */
    int32_t x_from;    /* +0x04 */
    int32_t x_to;      /* +0x08 */
    int32_t y_from;    /* +0x0c */
    int32_t y_to;      /* +0x10 */
    int32_t w_from;    /* +0x14 */
    int32_t w_to;      /* +0x18 */
    int32_t h_from;    /* +0x1c */
    int32_t h_to;      /* +0x20 */
} g2_expand_anim_cfg_t;
_Static_assert(sizeof(g2_expand_anim_cfg_t) == 0x24u, "expand animation config");

typedef struct {
    int32_t x1, y1, x2, y2;
} g2_lv_area_t;

/* Conversate tag node (0x1c bytes, see conversate_tag_get_by_index_5964e2.c). */
typedef struct {
    uint8_t kind;         /* +0x00 icon type */
    uint8_t pad[3];
    const char *title;    /* +0x04 */
    const char *body;     /* +0x08 */
    uint32_t unk_0c;      /* +0x0c */
    uint32_t tag_id;      /* +0x10 */
    void *prev, *next;    /* +0x14, +0x18 */
} g2_conversate_tag_t;
_Static_assert(sizeof(g2_conversate_tag_t) == 0x1cu, "tag node");

#define LV_SIZE_CONTENT 0x3fffffffu
#define LV_OBJ_FLAG_HIDDEN 0x1u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_SCROLL_MASK 0x360u /* elastic | momentum | chain */
#define LV_ALIGN_TOP_MID 1u
#define LV_ALIGN_LEFT_MID 7u
#define LV_ALIGN_RIGHT_MID 8u
#define LV_ALIGN_OUT_BOTTOM_LEFT 13u
#define LV_ALIGN_OUT_RIGHT_MID 20u
#define LINE_HEIGHT 28

typedef void (*g2_anim_done_cb_t)(void);

extern uint32_t audio_conversate_ui_app_id_200743a0;   /* RAM 0x200743a0: Conversate screen object */
extern uint32_t audio_uart_ring_primary_head_cell;     /* RAM 0x200746dc: active lv_font_t * */

extern g2_conversate_tag_t *audio_conversate_tag_get_by_index_5964e2(uint32_t index);
extern g2_conversate_tag_t *conversate_tag_get_data_by_auto_disp_node_prev_596930(void);
extern uint32_t audio_conversate_tag_icon_get_5b0af6(uint32_t type);
extern void audio_conversate_tag_unselect_5969a4(void);
extern uint32_t audio_conversate_tag_ai_cue_enabled_5967bc(void);
extern void audio_conversate_report_5b02e4(uint32_t event, uint32_t value);
extern void conversate_timer_mgr_set_auto_extend_countdown_reset_5b3c2a(void);
extern void conversate_ui_menu_apply_base_style(void *obj, int32_t value, uint32_t selector);
extern uint32_t APP_PbConversateTxEncodeTagTrackingData(const g2_conversate_tag_tracking_t *tracking);
extern void audio_conversate_expand_animation_5b7704(void *object, const g2_expand_anim_cfg_t *cfg,
                                                     g2_anim_done_cb_t complete);
extern void audio_uart_page_58c238(void *object, uint32_t duration, uint32_t completed_cb); /* common_fade_in_animation */
extern void audio_terminal_fade_out_58c426(void *object, uint32_t duration, g2_anim_done_cb_t complete);
extern void common_fade_in_animation_with_delay_58c328(void *object, uint32_t duration, uint32_t delay,
                                                       g2_anim_done_cb_t complete);
extern int32_t common_ui_get_scroll_y_5546be(void *obj, int32_t offset, int32_t speed, int32_t step);
extern uint32_t osKernelGetTickCount(void);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);

/* LVGL 9 (core at 0x43xxxx..0x49xxxx). */
extern void *audio_uart_page_43de82(void *parent);                          /* lv_obj_create */
extern void audio_uart_page_44d878(void *object);                           /* lv_obj_clean */
extern void audio_conversate_lv_object_delete_44d90e(void *object);         /* lv_obj_delete */
extern void audio_uart_page_43ded4(void *object, uint32_t flags);           /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *object, uint32_t flags);           /* lv_obj_remove_flag */
extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);        /* lv_obj_is_valid */
extern void audio_uart_page_43f4c0(void *object, uint32_t w, uint32_t h);   /* lv_obj_set_size */
extern void audio_uart_page_43f66c(void *object);                           /* lv_obj_update_layout */
extern void audio_uart_page_43f6ac(void *object, uint32_t align);           /* lv_obj_set_align */
extern void audio_uart_page_43f6b8(void *object, uint32_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *object, void *base, uint32_t align, int32_t x,
                                   int32_t y);                              /* lv_obj_align_to */
extern void audio_uart_lv_obj_coords_43fc2a(const void *object, g2_lv_area_t *area); /* lv_obj_get_coords */
extern int32_t audio_uart_lv_obj_height_43fdda(void *object);               /* lv_obj_get_height */
extern void *audio_uart_lv_child_get_44dce2(void *object, int32_t index);   /* lv_obj_get_child */
extern int32_t audio_uart_lv_obj_y_44e498(void *object);                    /* lv_obj_get_scroll_y */
extern void audio_uart_page_44e368(void *object, uint32_t mode);            /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *object, uint32_t dir);             /* lv_obj_set_scroll_dir */
extern int32_t audio_uart_lv_area_width_451598(const g2_lv_area_t *area);
extern int32_t audio_uart_lv_area_height_4515a4(const g2_lv_area_t *area);
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                       /* lv_color_hex */
extern void audio_uart_page_441180(void *obj, uint32_t v, uint32_t sel);    /* style max_width */
extern void audio_uart_page_4411aa(void *obj, uint32_t v, uint32_t sel);    /* style max_height */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);     /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);     /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);     /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);     /* style pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel);    /* style bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* style border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t v, uint32_t sel);    /* style border_opa */
extern void audio_uart_page_44131c(void *obj, uint32_t v, uint32_t sel);    /* style border_width */
extern void audio_uart_page_4413ce(void *obj, uint32_t v, uint32_t sel);    /* style image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* style text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel); /* style text_font */
extern void audio_uart_page_44144c(void *obj, int32_t v, uint32_t sel);     /* style text_line_space */
extern void audio_uart_page_44145a(void *obj, uint32_t v, uint32_t sel);    /* style text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);     /* style radius */
extern void audio_uart_display_audio_reset_441488(void *obj, uint32_t opa, uint32_t sel); /* style opa */
extern void *audio_uart_page_498668(void *parent);                          /* lv_image_create */
extern void audio_uart_page_498680(void *object, const void *source);       /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                          /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text);   /* lv_label_set_text */
extern uint32_t audio_lv_label_set_text_fmt_49954c(void *label, const char *format, ...);
extern void *audio_uart_page_layout_499678(void *label, uint32_t mode);     /* lv_label_set_long_mode */
extern uint32_t audio_uart_page_460084(const char *key);                    /* i18n index lookup */
extern const char *audio_uart_page_45fffe(const char *fallback, uint32_t index); /* i18n text */

static const char module[] = "conversate.ui"; /* ROM 0x7858a0 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_tag_page.c"; /* ROM 0x6ec708 */
static const char duration_fn[] = "conversate_calculate_auto_duration_by_label"; /* ROM 0x73d320 */
static const char input_fn[] = "conversate_tag_extend_page_input_event_handler"; /* ROM 0x732924 */
static const char show_fn[] = "conversate_ui_action_tag_show"; /* ROM 0x75edd0 */
static const char to_main_fn[] = "conversate_ui_action_tag_to_main_page"; /* ROM 0x748afc */
static const char no_label[] = "Label is NULL, using default timeout"; /* ROM 0x748ad4 */
static const char no_label_c[] = "[conversate.ui]Label is NULL, using default timeout"; /* ROM 0x7280a0 */
static const char in_anim[] = "tag input ignored while animating, code=%d"; /* ROM 0x73d34c */
static const char in_anim_c[] = "[conversate.ui]tag input ignored while animating, code=%d"; /* ROM 0x71384c */
static const char close_key[] = "ID_CONVERSATE_CLOSE_IN_X_SEC"; /* ROM 0x75edf0 */
static const char expand_src[] = "tag expand source: rel(%d,%d,%d,%d) abs[(%d,%d)-(%d,%d)]"; /* ROM 0x713888 */
static const char expand_src_c[] =
    "[conversate.ui]tag expand source: rel(%d,%d,%d,%d) abs[(%d,%d)-(%d,%d)]"; /* ROM 0x6f968c */
static const char tracking_msg[] =
    "tracking data send: tag_id: %d, open_type: %d, close_type: %d, duration_time_ms: %d"; /* ROM 0x6e6f4c */
static const char tracking_c[] =
    "[conversate.ui]tracking data send: tag_id: %d, open_type: %d, close_type: %d, duration_time_ms: %d"; /* ROM 0x6da480 */
static const char shrink_null[] = "tag manual shrink failed: current_button is NULL"; /* ROM 0x7280d4 */
static const char shrink_null_c[] = "[conversate.ui]tag manual shrink failed: current_button is NULL"; /* ROM 0x70a5a4 */
static const char shrink_dst[] = "tag shrink target: rel(%d,%d,%d,%d) abs[(%d,%d)-(%d,%d)]"; /* ROM 0x7138c4 */
static const char shrink_dst_c[] =
    "[conversate.ui]tag shrink target: rel(%d,%d,%d,%d) abs[(%d,%d)-(%d,%d)]"; /* ROM 0x6f96d4 */
static const char shrink_go[] = "tag manual shrink animation started"; /* ROM 0x753018 */
static const char shrink_go_c[] = "[conversate.ui]tag manual shrink animation started"; /* ROM 0x728108 */

/* ROM 0x75303c: grow from the list button to the full-width overlay. */
static const g2_expand_anim_cfg_t expand_template = {
    .duration = 300u, .delay = 0u, .w_to = 0x240,
};
/* ROM 0x753060: shrink the overlay back onto the list button. */
static const g2_expand_anim_cfg_t shrink_template = {
    .duration = 300u, .delay = 200u, .w_from = 0x240,
};

void conversate_tag_close_timer_callback(void);
void conversate_tag_page_deinit(void);
void conversate_tag_shrink_complete_cb_5b660e(void);

static void *font(void)
{
    return (void *)(uintptr_t)audio_uart_ring_primary_head_cell;
}

/* Auto-close seconds from the wrapped height of the body label (28 px lines). */
uint8_t conversate_calculate_auto_duration_by_label_5b5d5e(void *label)
{
    if (label == NULL) {
        CONV_LOG0(2u, duration_fn, 0x15u, 0x08000000u, no_label, no_label_c);
        return 5u;
    }
    audio_uart_page_43f66c(label);
    const uint32_t lines = (uint32_t)((audio_uart_lv_obj_height_43fdda(label) + LINE_HEIGHT - 1) / LINE_HEIGHT);
    if (lines < 2u)
        return 3u;
    if (lines == 2u)
        return 5u;
    if (lines == 3u)
        return 7u;
    if (lines == 4u)
        return 9u;
    return 11u;
}

void conversate_tag_extend_page_input_event_handler(uint32_t code, const g2_conversate_input_t *event)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;

    if (ui->overlay_root == NULL)
        return;
    if (ui->animating != 0u) {
        CONV_LOG(3u, input_fn, 0x31u, 0x0c400000u, in_anim, in_anim_c, code);
        return;
    }
    conversate_timer_mgr_set_auto_extend_countdown_reset_5b3c2a();
    void *const body = audio_uart_lv_child_get_44dce2(ui->overlay_root, 1);
    if (code == CONV_INPUT_CLICK) {
        if (ui->tracking.open_type == 1u)
            audio_conversate_report_5b02e4(0x0au, 0u);
    } else if (code == CONV_INPUT_DOUBLE_CLICK) {
        audio_conversate_report_5b02e4(0x0au, 1u);
    } else if (code == CONV_INPUT_SCROLL_UP) {
        const int32_t y = common_ui_get_scroll_y_5546be(body, -event->motion[1], event->motion[0], LINE_HEIGHT);
        if (y != audio_uart_lv_obj_y_44e498(body))
            audio_conversate_report_5b02e4(0x0eu, (uint32_t)y);
    } else if (code == CONV_INPUT_SCROLL_DOWN) {
        const int32_t y = common_ui_get_scroll_y_5546be(body, event->motion[1], event->motion[0], LINE_HEIGHT);
        if (y != audio_uart_lv_obj_y_44e498(body))
            audio_conversate_report_5b02e4(0x0fu, (uint32_t)y);
    }
}

/* Expand animation finished: reveal and fade in the body. */
void conversate_tag_close_timer_callback(void)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    void *const body = audio_uart_lv_child_get_44dce2(ui->overlay_root, 1);

    audio_uart_page_43dfa4(body, LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_58c238(body, 200u, 0u);
    ui->animating = 0u;
}

/* Level-3 log of an animation endpoint: rel(x, y, w, h) abs[(x1, y1)-(x2, y2)]. */
static void log_area(const char *fn, uint32_t line, const char *full, const char *compact, int32_t w,
                     int32_t h, const g2_lv_area_t *area)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, fn, line, full, area->x1,
                           area->y1, w, h, area->x1, area->y1, area->x2, area->y2);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0e000000u, compact, compact, area->x1, area->y1, w, h, area->x1,
                                  area->y1, area->x2, area->y2);
}

/* conversate_ui_action_tag_show(action, auto_pop): build the overlay for the
 * selected (or auto-popped) tag and grow it out of the current list button. */
uint32_t audio_conversate_ui_route_5b5f44(uint32_t action, uint32_t auto_pop)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    const g2_conversate_tag_t *tag;
    (void)action;

    if (auto_pop != 0u)
        tag = conversate_tag_get_data_by_auto_disp_node_prev_596930();
    else
        tag = audio_conversate_tag_get_by_index_5964e2((uint16_t)ui->current_index);
    if (tag == NULL)
        return UINT32_MAX;

    ui->tracking.tag_id = tag->tag_id;
    ui->tracking.open_type = auto_pop != 0u;
    ui->tracking.duration_ms = osKernelGetTickCount();

    if (ui->overlay_root == NULL)
        ui->overlay_root = audio_uart_page_43de82((void *)(uintptr_t)audio_conversate_ui_app_id_200743a0);
    else
        audio_uart_page_44d878(ui->overlay_root);
    void *const root = ui->overlay_root;
    audio_uart_page_43f4c0(root, 0x240u, LV_SIZE_CONTENT);
    audio_uart_page_43f6ac(root, LV_ALIGN_TOP_MID);
    audio_uart_page_4411aa(root, (uint32_t)ui->overlay_max_height, 0u);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 1u, 0u);
    audio_uart_page_44130c(root, 0xffu, 0u);
    audio_uart_page_4412ec(root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44146a(root, 6, 0u);
    audio_uart_page_44122a(root, 12, 0u);
    audio_uart_page_441238(root, 0, 0u);
    audio_uart_page_44120e(root, 6, 0u);
    audio_uart_page_44121c(root, 6, 0u);
    audio_uart_page_43dfa4(root, LV_OBJ_FLAG_SCROLLABLE);

    /* Header row: tag icon and title. */
    void *const header = audio_uart_page_43de82(root);
    audio_uart_page_43f4c0(header, 0x228u, LINE_HEIGHT);
    audio_uart_page_43f6ac(header, LV_ALIGN_TOP_MID);
    audio_uart_page_44129e(header, 0u, 0u);
    audio_uart_page_44131c(header, 0u, 0u);
    audio_uart_page_44146a(header, 0, 0u);
    conversate_ui_menu_apply_base_style(header, 0, 0u);
    audio_uart_page_43dfa4(header, LV_OBJ_FLAG_SCROLLABLE);

    void *const icon = audio_uart_page_498668(header);
    audio_uart_page_498680(icon, (const void *)(uintptr_t)audio_conversate_tag_icon_get_5b0af6(tag->kind));
    audio_uart_page_44127e(icon, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(icon, 0xffu, 0u);
    audio_uart_page_4413ce(icon, 0xffu, 0u);
    audio_uart_page_43f6ac(icon, LV_ALIGN_LEFT_MID);

    void *const title = audio_uart_page_499416(header);
    audio_uart_page_49942e(title, tag->title);
    audio_uart_page_44143e(title, (uint32_t)(uintptr_t)font(), 0u);
    audio_uart_page_441180(title, 0x1feu, 0u);
    audio_uart_page_4411aa(title, LINE_HEIGHT, 0u);
    audio_uart_page_layout_499678(title, 1u);
    audio_uart_page_44145a(title, 1u, 0u);
    audio_uart_page_44140e(title, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43f6d6(title, icon, LV_ALIGN_OUT_RIGHT_MID, 8, -1);

    /* Scrollable body below the header, a whole number of lines high. */
    void *const body = audio_uart_page_43de82(root);
    audio_uart_page_43f4c0(body, 0x20au, LV_SIZE_CONTENT);
    audio_uart_page_43f6d6(body, title, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 10);
    audio_uart_page_44129e(body, 0u, 0u);
    audio_uart_page_44131c(body, 0u, 0u);
    audio_uart_page_44130c(body, 0u, 0u);
    audio_uart_page_44146a(body, 0, 0u);
    conversate_ui_menu_apply_base_style(body, 0, 0u);
    audio_uart_page_44e368(body, 3u);
    audio_uart_page_43ded4(body, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_44e3ca(body, 0x0cu);
    audio_uart_page_43dfa4(body, LV_OBJ_FLAG_SCROLL_MASK);
    audio_uart_page_4411aa(body, (uint32_t)(((ui->overlay_max_height - 0x26) / LINE_HEIGHT) * LINE_HEIGHT), 0u);

    void *const text = audio_uart_page_499416(body);
    audio_uart_page_43f4c0(text, 0x1feu, LV_SIZE_CONTENT);
    audio_uart_page_44144c(text, LINE_HEIGHT - *(const int32_t *)((const uint8_t *)font() + 0xc), 0u);
    audio_uart_page_43f6b8(text, LV_ALIGN_TOP_MID, 0, 0);
    audio_uart_page_layout_499678(text, 0u);
    audio_uart_page_44140e(text, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44143e(text, (uint32_t)(uintptr_t)font(), 0u);
    audio_uart_page_44145a(text, 1u, 0u);
    audio_uart_page_49942e(text, tag->body);
    ui->animating = 1u;

    if (auto_pop != 0u) {
        ui->auto_close_seconds = ui->auto_close_fixed != 0u
                                     ? ui->auto_close_fixed
                                     : conversate_calculate_auto_duration_by_label_5b5d5e(text);
        void *const hint = audio_uart_page_499416(header);
        audio_lv_label_set_text_fmt_49954c(hint, audio_uart_page_45fffe(close_key, audio_uart_page_460084(close_key)),
                                           ui->auto_close_seconds);
        audio_uart_page_44143e(hint, (uint32_t)(uintptr_t)font(), 0u);
        audio_uart_page_43f4c0(hint, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
        audio_uart_page_44140e(hint, audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44145a(hint, 1u, 0u);
        audio_uart_page_43f6b8(hint, LV_ALIGN_RIGHT_MID, -10, 0);
        audio_uart_page_441180(title, 400u, 0u);
    }

    audio_terminal_fade_out_58c426(ui->main_root, 200u, NULL);
    audio_uart_page_43f66c(root);

    g2_lv_area_t area;
    aeabi_memset_43c0e4(&area, sizeof(area), 0);
    audio_uart_lv_obj_coords_43fc2a(ui->current_button, &area);
    const int32_t w = audio_uart_lv_area_width_451598(&area);
    const int32_t h = audio_uart_lv_area_height_4515a4(&area);
    log_area(show_fn, 0xebu, expand_src, expand_src_c, w, h, &area);

    g2_expand_anim_cfg_t cfg;
    aeabi_memcpy4_439c04(&cfg, &expand_template, sizeof(cfg));
    cfg.x_from = area.x1;
    cfg.y_from = area.y1;
    cfg.w_from = w;
    cfg.h_from = h;
    cfg.h_to = audio_uart_lv_obj_height_43fdda(root);
    if (auto_pop != 0u) {
        audio_uart_page_58c238(root, 200u, 0u);
        cfg.delay = 500u;
    } else {
        cfg.delay = 200u;
    }
    audio_uart_page_43ded4(body, LV_OBJ_FLAG_HIDDEN);
    audio_conversate_expand_animation_5b7704(root, &cfg, conversate_tag_close_timer_callback);
    return 0u;
}

/* Fade-in of the main page finished after an auto-popped tag closed. */
void conversate_tag_shrink_complete_cb_5b660e(void)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;

    audio_uart_page_43dfa4(ui->main_root, LV_OBJ_FLAG_HIDDEN);
    audio_conversate_lv_object_delete_44d90e(ui->overlay_root);
    ui->overlay_root = NULL;
    ui->animating = 0u;
    if (ui->state == 2u && ui->selected == 0u && audio_conversate_tag_ai_cue_enabled_5967bc() == 1u)
        audio_conversate_report_5b02e4(8u, 1u);
}

/* Shrink animation finished: restore the list button and drop the overlay. */
void conversate_tag_page_deinit(void)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;

    if (ui->shrink_button != NULL && audio_terminal_ui_object_valid_43e2ea(ui->shrink_button) != 0u)
        audio_uart_display_audio_reset_441488(ui->shrink_button, 0xffu, 0u);
    ui->shrink_button = NULL;
    audio_conversate_lv_object_delete_44d90e(ui->overlay_root);
    ui->overlay_root = NULL;
    ui->animating = 0u;
}

/* conversate_ui_action_tag_to_main_page(action, close_route): send the
 * tracking record, then either cross-fade (auto-popped tag) or shrink the
 * overlay back onto the current list button. */
uint32_t audio_conversate_ui_route_5b6688(uint32_t action, uint32_t close_route)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    (void)action;

    if (ui->overlay_root == NULL)
        return UINT32_MAX;
    if (close_route == 1u)
        audio_conversate_tag_unselect_5969a4();
    ui->tracking.close_type = close_route == 2u;
    ui->tracking.duration_ms = osKernelGetTickCount() - ui->tracking.duration_ms;
    (void)APP_PbConversateTxEncodeTagTrackingData(&ui->tracking);
    CONV_LOG(3u, to_main_fn, 0x198u, 0x0d000000u, tracking_msg, tracking_c, ui->tracking.tag_id,
             ui->tracking.open_type, ui->tracking.close_type, ui->tracking.duration_ms);
    ui->animating = 1u;

    if (ui->tracking.open_type == 1u) {
        audio_terminal_fade_out_58c426(ui->overlay_root, 300u, NULL);
        audio_uart_page_58c238(ui->main_root, 300u,
                               (uint32_t)(uintptr_t)conversate_tag_shrink_complete_cb_5b660e);
        return 0u;
    }

    audio_terminal_fade_out_58c426(audio_uart_lv_child_get_44dce2(ui->overlay_root, 1), 200u, NULL);
    common_fade_in_animation_with_delay_58c328(ui->main_root, 300u, 200u, NULL);
    if (ui->current_button == NULL) {
        CONV_LOG0(1u, to_main_fn, 0x1a7u, 0x04000000u, shrink_null, shrink_null_c);
        return UINT32_MAX;
    }
    ui->shrink_button = ui->current_button;
    audio_uart_display_audio_reset_441488(ui->current_button, 0u, 0u);

    g2_lv_area_t area;
    aeabi_memset_43c0e4(&area, sizeof(area), 0);
    audio_uart_lv_obj_coords_43fc2a(ui->current_button, &area);
    const int32_t w = audio_uart_lv_area_width_451598(&area);
    const int32_t h = audio_uart_lv_area_height_4515a4(&area);
    log_area(to_main_fn, 0x1b6u, shrink_dst, shrink_dst_c, w, h, &area);

    g2_expand_anim_cfg_t cfg;
    aeabi_memcpy4_439c04(&cfg, &shrink_template, sizeof(cfg));
    cfg.x_to = area.x1;
    cfg.y_to = area.y1;
    cfg.w_to = w;
    cfg.h_from = audio_uart_lv_obj_height_43fdda(ui->overlay_root);
    cfg.h_to = h;
    audio_conversate_expand_animation_5b7704(ui->overlay_root, &cfg, conversate_tag_page_deinit);
    CONV_LOG0(3u, to_main_fn, 0x1c5u, 0x0c000000u, shrink_go, shrink_go_c);
    return 0u;
}

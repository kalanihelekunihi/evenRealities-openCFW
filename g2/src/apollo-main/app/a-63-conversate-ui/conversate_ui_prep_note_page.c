/* Conversate prep-note extend page, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui_prep_note_page.c.
 * Native 0x5b6a52..0x5b6a7d, 0x5b6a7e..0x5b6abf, 0x5b6c48..0x5b6cc9,
 * 0x5b7060..0x5b7115, 0x5b7116..0x5b7137 and 0x5b7138..0x5b74b9
 * (literal pool 0x5b7604..0x5b7670).
 *
 * The prep-note text scrolls in whole 28 px lines; scroll inputs are turned
 * into a target offset that is reported to the Conversate action machine
 * (0x0e up / 0x0f down), which later scrolls the page. 0x5b7138 keeps the
 * name the action matrix (conversate_ui_action_matrix_686920.c) links against. */
#include <stdint.h>
#include <stddef.h>
#include "conversate_ui_context.h"

#define LOG_MODULE module
#define LOG_PATH path

typedef struct {
    uint16_t duration; /* +0x00 */
    uint16_t delay;    /* +0x02 */
    int32_t x_from, x_to, y_from, y_to, w_from, w_to, h_from, h_to; /* +0x04..+0x23 */
} g2_expand_anim_cfg_t;
_Static_assert(sizeof(g2_expand_anim_cfg_t) == 0x24u, "expand animation config");

typedef struct {
    int32_t x, y;
} g2_lv_point_t;

#define LV_SIZE_CONTENT 0x3fffffffu
#define LV_OBJ_FLAG_HIDDEN 0x1u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_SCROLL_MASK 0x360u
#define LV_PART_SCROLLBAR 0x10000u
#define LV_PART_SCROLLBAR_SCROLLED 0x10040u
#define LV_ALIGN_LEFT_MID 7u
#define LV_ALIGN_OUT_BOTTOM_LEFT 13u
#define LV_ALIGN_OUT_RIGHT_MID 20u
#define LINE_HEIGHT 28

typedef void (*g2_anim_done_cb_t)(void);

extern uint32_t audio_conversate_ui_app_id_200743a0;   /* RAM 0x200743a0: Conversate screen object */
extern uint32_t audio_uart_ring_primary_head_cell;     /* RAM 0x200746dc: active lv_font_t * */
extern const uint8_t audio_conversate_prep_icon_76a47c[]; /* ROM 0x76a47c lv_image_dsc_t */

extern int32_t audio_conversate_prep_scroll_clamp_5b6a3a(int32_t requested);
extern void audio_conversate_prep_note_pool_show_5b6b58(int32_t requested_scroll);
extern uint32_t audio_conversate_prep_note_refresh_5b6cd0(uint32_t animate);
extern void audio_conversate_prep_note_style_5b69d4(void *object, uint32_t value, uint32_t selector); /* pad_all */
extern void audio_conversate_report_5b02e4(uint32_t event, uint32_t value);
extern void audio_conversate_expand_animation_5b7704(void *object, const g2_expand_anim_cfg_t *cfg,
                                                     g2_anim_done_cb_t complete);
extern void audio_terminal_fade_out_58c426(void *object, uint32_t duration, g2_anim_done_cb_t complete);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);

/* LVGL 9. */
extern void *audio_uart_page_43de82(void *parent);                          /* lv_obj_create */
extern void audio_uart_page_44d878(void *object);                           /* lv_obj_clean */
extern void audio_uart_page_43ded4(void *object, uint32_t flags);           /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *object, uint32_t flags);           /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *object, int32_t x, int32_t y);     /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *object, int32_t x);                /* lv_obj_set_x */
extern void audio_uart_page_43f4c0(void *object, uint32_t w, uint32_t h);   /* lv_obj_set_size */
extern void audio_uart_page_43f6ac(void *object, uint32_t align);           /* lv_obj_set_align */
extern void audio_uart_page_43f6d6(void *object, void *base, uint32_t align, int32_t x,
                                   int32_t y);                              /* lv_obj_align_to */
extern int32_t audio_uart_lv_obj_width_43fd9e(void *object);                /* lv_obj_get_width */
extern int32_t audio_uart_lv_obj_height_43fdda(void *object);               /* lv_obj_get_height */
extern int32_t audio_uart_lv_obj_content_width_43fe16(void *object);        /* lv_obj_get_content_width */
extern int32_t audio_uart_lv_obj_y_44e498(void *object);                    /* lv_obj_get_scroll_y */
extern void lv_obj_get_scroll_end_44e75e(void *obj, g2_lv_point_t *point);
extern void audio_uart_page_44e368(void *object, uint32_t mode);            /* lv_obj_set_scrollbar_mode */
extern void audio_uart_page_44e3ca(void *object, uint32_t dir);             /* lv_obj_set_scroll_dir */
extern uint32_t audio_uart_page_event_code_450286(const void *event);       /* lv_event_get_code */
extern void *audio_uart_page_451740(void *object, void (*callback)(const void *), uint32_t filter,
                                    void *user_data);                       /* lv_obj_add_event_cb */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                       /* lv_color_hex */
extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel);     /* style pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel);     /* style pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel);     /* style pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel);     /* style pad_right */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* style bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t v, uint32_t sel);    /* style bg_opa */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* style border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t v, uint32_t sel);    /* style border_opa */
extern void audio_uart_page_44131c(void *obj, uint32_t v, uint32_t sel);    /* style border_width */
extern void audio_uart_page_4413be(void *obj, uint32_t v, uint32_t sel);    /* style opa (scrollbar) */
extern void audio_uart_page_4413ce(void *obj, uint32_t v, uint32_t sel);    /* style image_opa */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* style text_color */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel); /* style text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t v, uint32_t sel);    /* style text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);     /* style radius */
extern void *audio_uart_page_498668(void *parent);                          /* lv_image_create */
extern void audio_uart_page_498680(void *object, const void *source);       /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                          /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text);   /* lv_label_set_text */
extern void *audio_uart_page_layout_499678(void *label, uint32_t mode);     /* lv_label_set_long_mode */
extern uint32_t audio_uart_page_460084(const char *key);                    /* i18n index lookup */
extern const char *audio_uart_page_45fffe(const char *fallback, uint32_t index); /* i18n text */

static const char module[] = "conversate.prep"; /* ROM 0x785890 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_ui_prep_note_page.c"; /* ROM 0x6e2c78 */
static const char scroll_fn[] = "conversate_ui_prep_note_scroll_event_cb"; /* ROM 0x748a5c */
static const char input_fn[] = "conversate_prep_note_extend_page_input_event_handler"; /* ROM 0x71d298 */
static const char scroll_end[] = "prep scroll end y=%d"; /* ROM 0x775fa4 */
static const char scroll_end_c[] = "[conversate.prep]prep scroll end y=%d"; /* ROM 0x748a84 */
static const char in_anim[] = "prep note input ignored while animating, code=%d"; /* ROM 0x72806c */
static const char in_anim_c[] = "[conversate.prep]prep note input ignored while animating, code=%d"; /* ROM 0x70159c */
static const char title_key[] = "ID_CONVERSATE_PREP_NOTES"; /* ROM 0x76a7fc */

void conversate_ui_prep_note_scroll_event_cb_5b6c48(const void *event);
void conversate_prep_note_expand_done_cb_5b7116(void);

/* Current scroll end of the prep-note page, clamped to the text extent. */
int32_t conversate_prep_note_scroll_end_get_5b6a52(void)
{
    const g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    g2_lv_point_t end;

    aeabi_memset_43c0e4(&end, sizeof(end), 0);
    if (ui->prep_text == NULL)
        return 0;
    lv_obj_get_scroll_end_44e75e(ui->prep_content, &end);
    return audio_conversate_prep_scroll_clamp_5b6a3a(end.y);
}

/* Scroll target for a swipe of `delta` px: doubled for fast swipes
 * (speed > 100) and snapped outward to whole lines. */
int32_t conversate_prep_note_scroll_target_5b6a7e(int32_t delta, int32_t speed)
{
    const int32_t current = conversate_prep_note_scroll_end_get_5b6a52();
    int32_t target = current;

    if (speed > 100)
        delta *= 2;
    if (delta > 0)
        target = ((delta + current + LINE_HEIGHT - 1) / LINE_HEIGHT) * LINE_HEIGHT;
    else if (delta < 0)
        target = ((delta + current) / LINE_HEIGHT) * LINE_HEIGHT;
    return audio_conversate_prep_scroll_clamp_5b6a3a(target);
}

void conversate_ui_prep_note_scroll_event_cb_5b6c48(const void *event)
{
    const g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    const uint32_t code = audio_uart_page_event_code_450286(event);

    if (ui->prep_content == NULL)
        return;
    const int32_t y = audio_conversate_prep_scroll_clamp_5b6a3a(audio_uart_lv_obj_y_44e498(ui->prep_content));
    if (code == 0x0fu || code == 0x0cu) {
        audio_conversate_prep_note_pool_show_5b6b58(y);
    } else if (code == 0x0eu) {
        audio_conversate_prep_note_pool_show_5b6b58(y);
        CONV_LOG(3u, scroll_fn, 0xc2u, 0x0c400000u, scroll_end, scroll_end_c, y);
    }
}

void conversate_prep_note_extend_page_input_event_handler_5b7060(uint32_t code,
                                                                 const g2_conversate_input_t *event)
{
    const g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;

    if (ui->animating != 0u) {
        CONV_LOG(3u, input_fn, 0x132u, 0x0c400000u, in_anim, in_anim_c, code);
        return;
    }
    if (code == CONV_INPUT_CLICK)
        return;
    if (code == CONV_INPUT_DOUBLE_CLICK) {
        audio_conversate_report_5b02e4(0x0au, 0u);
    } else if ((code == CONV_INPUT_SCROLL_UP || code == CONV_INPUT_SCROLL_DOWN) && ui->prep_text != NULL) {
        int32_t delta = event->motion[1];
        if (code == CONV_INPUT_SCROLL_UP)
            delta = -delta;
        const int32_t target = conversate_prep_note_scroll_target_5b6a7e(delta, event->motion[0]);
        if (target != conversate_prep_note_scroll_end_get_5b6a52())
            audio_conversate_report_5b02e4(code == CONV_INPUT_SCROLL_UP ? 0x0eu : 0x0fu, (uint32_t)target);
    }
}

/* Expand animation finished: fill the page. */
void conversate_prep_note_expand_done_cb_5b7116(void)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;

    ui->animating = 0u;
    if (ui->prep_content != NULL && ui->prep_scrollbar != NULL)
        (void)audio_conversate_prep_note_refresh_5b6cd0(1u);
}

/* Prep-note page show: build the overlay (title row, scroll container,
 * scrollbar) and grow it out of the prep-note button. */
uint32_t audio_conversate_ui_route_5b7138(uint32_t action, uint32_t value)
{
    g2_conversate_ui_t *const ui = G2_CONVERSATE_UI;
    g2_expand_anim_cfg_t cfg;
    (void)action;
    (void)value;

    aeabi_memset_43c0e4(&cfg, sizeof(cfg), 0);
    ui->prep_content = NULL;
    ui->prep_text = NULL;
    ui->prep_scrollbar = NULL;
    ui->prep_line = 0u;
    aeabi_memset_43c0e4(ui->prep_cache, sizeof(ui->prep_cache), 0);

    if (ui->overlay_root == NULL)
        ui->overlay_root = audio_uart_page_43de82((void *)(uintptr_t)audio_conversate_ui_app_id_200743a0);
    else
        audio_uart_page_44d878(ui->overlay_root);
    void *const root = ui->overlay_root;
    audio_uart_page_43f09a(root, 0, 0);
    audio_uart_page_44129e(root, 0u, 0u);
    audio_uart_page_44131c(root, 1u, 0u);
    audio_uart_page_44130c(root, 0xffu, 0u);
    audio_uart_page_4412ec(root, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44146a(root, 6, 0u);
    audio_uart_page_44122a(root, 12, 0u);
    audio_uart_page_441238(root, 0, 0u);
    audio_uart_page_44120e(root, 0, 0u);
    audio_uart_page_44121c(root, 6, 0u);
    audio_uart_page_43dfa4(root, LV_OBJ_FLAG_SCROLLABLE);

    /* Title row: prep-note icon and localized title. */
    void *const header = audio_uart_page_43de82(root);
    audio_uart_page_43f4c0(header, 0x228u, 0x28u);
    audio_uart_page_43f09a(header, 0, 0);
    audio_uart_page_44129e(header, 0u, 0u);
    audio_uart_page_44131c(header, 0u, 0u);
    audio_uart_page_44146a(header, 0, 0u);
    audio_conversate_prep_note_style_5b69d4(header, 0u, 0u);
    audio_uart_page_43dfa4(header, LV_OBJ_FLAG_SCROLLABLE);

    void *const icon = audio_uart_page_498668(header);
    audio_uart_page_498680(icon, audio_conversate_prep_icon_76a47c);
    audio_uart_page_44127e(icon, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(icon, 0xffu, 0u);
    audio_uart_page_4413ce(icon, 0xffu, 0u);
    audio_uart_page_43f6ac(icon, LV_ALIGN_LEFT_MID);

    void *const title = audio_uart_page_499416(header);
    audio_uart_page_49942e(title, audio_uart_page_45fffe(title_key, audio_uart_page_460084(title_key)));
    audio_uart_page_44143e(title, audio_uart_ring_primary_head_cell, 0u);
    audio_uart_page_43f4c0(title, 0x1e6u, LV_SIZE_CONTENT);
    audio_uart_page_layout_499678(title, 1u);
    audio_uart_page_44145a(title, 1u, 0u);
    audio_uart_page_44140e(title, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_43f6d6(title, icon, LV_ALIGN_OUT_RIGHT_MID, 8, -1);

    /* Scroll container; the text itself is created by the refresh. */
    ui->prep_content = audio_uart_page_43de82(root);
    void *const content = ui->prep_content;
    audio_uart_page_43f6d6(content, header, LV_ALIGN_OUT_BOTTOM_LEFT, 0, 10);
    audio_uart_page_43f4c0(content, 0x220u, 0xe0u);
    audio_uart_page_44129e(content, 0u, 0u);
    audio_uart_page_44131c(content, 0u, 0u);
    audio_uart_page_44130c(content, 0u, 0u);
    audio_uart_page_44146a(content, 0, 0u);
    audio_conversate_prep_note_style_5b69d4(content, 0u, 0u);
    audio_uart_page_44e3ca(content, 0x0cu);
    audio_uart_page_43dfa4(content, LV_OBJ_FLAG_SCROLL_MASK);
    audio_uart_page_44e368(content, 0u);
    audio_uart_page_44129e(content, 0u, LV_PART_SCROLLBAR);
    audio_uart_page_44130c(content, 0u, LV_PART_SCROLLBAR);
    audio_uart_page_4413be(content, 0u, LV_PART_SCROLLBAR);
    audio_uart_page_44129e(content, 0u, LV_PART_SCROLLBAR_SCROLLED);
    audio_uart_page_44130c(content, 0u, LV_PART_SCROLLBAR_SCROLLED);
    audio_uart_page_4413be(content, 0u, LV_PART_SCROLLBAR_SCROLLED);
    audio_uart_page_451740(content, conversate_ui_prep_note_scroll_event_cb_5b6c48, 0x0cu, NULL);
    audio_uart_page_451740(content, conversate_ui_prep_note_scroll_event_cb_5b6c48, 0x0fu, NULL);
    audio_uart_page_451740(content, conversate_ui_prep_note_scroll_event_cb_5b6c48, 0x0eu, NULL);

    /* 2 px custom scrollbar at the right edge. */
    ui->prep_scrollbar = audio_uart_page_43de82(root);
    void *const bar = ui->prep_scrollbar;
    audio_uart_page_43f4c0(bar, 2u, LINE_HEIGHT);
    audio_uart_page_43f0e0(bar, audio_uart_lv_obj_content_width_43fe16(root) - 10);
    audio_uart_page_44127e(bar, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44129e(bar, 0xffu, 0u);
    audio_uart_page_44131c(bar, 0u, 0u);
    audio_uart_page_44146a(bar, 0, 0u);
    audio_conversate_prep_note_style_5b69d4(bar, 0u, 0u);
    audio_uart_page_43dfa4(bar, LV_OBJ_FLAG_SCROLLABLE);

    audio_uart_page_43ded4(ui->prep_content, LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(ui->prep_scrollbar, LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43ded4(ui->top_button, LV_OBJ_FLAG_HIDDEN);
    audio_terminal_fade_out_58c426(ui->main_root, 200u, NULL);
    audio_uart_page_43ded4(ui->title_row, LV_OBJ_FLAG_HIDDEN);
    audio_uart_page_43dfa4(root, LV_OBJ_FLAG_HIDDEN);

    cfg.duration = 300u;
    cfg.x_from = 0;
    cfg.x_to = 0;
    cfg.y_from = 0;
    cfg.y_to = 0;
    cfg.w_from = audio_uart_lv_obj_width_43fd9e(ui->top_button);
    cfg.w_to = 0x240;
    cfg.h_from = audio_uart_lv_obj_height_43fdda(ui->top_button);
    cfg.h_to = 0x120;
    ui->animating = 1u;
    audio_conversate_expand_animation_5b7704(root, &cfg, conversate_prep_note_expand_done_cb_5b7116);
    return 0u;
}

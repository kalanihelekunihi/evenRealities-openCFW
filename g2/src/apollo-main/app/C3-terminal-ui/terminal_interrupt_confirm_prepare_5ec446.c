/* Terminal "Stop Agent response?" confirmation dialog constructor,
 * firmware 2.2.6.10.
 * Stock ranges:
 *   0x5ec30c..0x5ec33d  pad left/right/top/bottom helper (TU-local copy of the
 *                       lv_obj_set_style_pad_all pattern; single caller 0x5ec52e)
 *   0x5ec446..0x5ec73b  audio_terminal_interrupt_confirm_prepare_5ec446
 * Literal pool 0x5ec7d0..0x5ec7ef ("Yes" is stored in-pool at 0x5ec7d0).
 *
 * The dialog root is kept in the terminal UI state cluster (RAM 0x2006e0d0):
 *   +0x230 dialog root, +0x234 title label, +0x238 option box,
 *   +0x23c selection icon, +0x278 selected option (0 = Yes). */
#include <stdint.h>

typedef struct _lv_obj_t lv_obj_t;
typedef struct _lv_font_t lv_font_t;
typedef struct {
    uint8_t blue;
    uint8_t green;
    uint8_t red;
} lv_color_t; /* LVGL 9.3 lv_color_t */

#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_IGNORE_LAYOUT 0x20000u
#define LV_FLEX_FLOW_COLUMN 1u
#define LV_FLEX_ALIGN_START 0u
#define LV_LABEL_LONG_WRAP 0u
#define LV_TEXT_ALIGN_LEFT 1u
#define LV_BORDER_SIDE_TOP 2u
#define LV_SIZE_CONTENT 0x3fffffff

/* LVGL 9.3 core and label widget, compiled from third-party/upstream/lvgl. */
extern lv_obj_t *lv_obj_create(lv_obj_t *parent);                         /* 0x43de82 */
extern void lv_obj_add_flag(lv_obj_t *obj, uint32_t f);                   /* 0x43ded4 */
extern void lv_obj_remove_flag(lv_obj_t *obj, uint32_t f);                /* 0x43dfa4 */
extern void lv_obj_set_pos(lv_obj_t *obj, int32_t x, int32_t y);          /* 0x43f09a */
extern void lv_obj_set_size(lv_obj_t *obj, int32_t w, int32_t h);         /* 0x43f4c0 */
extern void lv_obj_set_width(lv_obj_t *obj, int32_t w);                   /* 0x43f506 */
extern void lv_obj_set_height(lv_obj_t *obj, int32_t h);                  /* 0x43f568 */
extern void lv_obj_update_layout(const lv_obj_t *obj);                    /* 0x43f66c */
extern lv_color_t lv_color_hex(uint32_t c);                               /* 0x44104c */
extern void lv_obj_set_style_min_height(lv_obj_t *obj, int32_t v, uint32_t sel); /* 0x44119c */
extern void lv_obj_set_style_pad_top(lv_obj_t *obj, int32_t v, uint32_t sel);    /* 0x44120e */
extern void lv_obj_set_style_pad_bottom(lv_obj_t *obj, int32_t v, uint32_t sel); /* 0x44121c */
extern void lv_obj_set_style_pad_left(lv_obj_t *obj, int32_t v, uint32_t sel);   /* 0x44122a */
extern void lv_obj_set_style_pad_right(lv_obj_t *obj, int32_t v, uint32_t sel);  /* 0x441238 */
extern void lv_obj_set_style_pad_row(lv_obj_t *obj, int32_t v, uint32_t sel);    /* 0x441246 */
extern void lv_obj_set_style_margin_bottom(lv_obj_t *obj, int32_t v, uint32_t sel); /* 0x441262 */
extern void lv_obj_set_style_margin_left(lv_obj_t *obj, int32_t v, uint32_t sel);   /* 0x441270 */
extern void lv_obj_set_style_bg_opa(lv_obj_t *obj, uint8_t v, uint32_t sel);  /* 0x44129e */
extern void lv_obj_set_style_border_color(lv_obj_t *obj, lv_color_t v, uint32_t sel); /* 0x4412ec */
extern void lv_obj_set_style_border_width(lv_obj_t *obj, int32_t v, uint32_t sel); /* 0x44131c */
extern void lv_obj_set_style_border_side(lv_obj_t *obj, uint32_t v, uint32_t sel); /* 0x44132a */
extern void lv_obj_set_style_text_color(lv_obj_t *obj, lv_color_t v, uint32_t sel); /* 0x44140e */
extern void lv_obj_set_style_text_font(lv_obj_t *obj, const lv_font_t *v, uint32_t sel); /* 0x44143e */
extern void lv_obj_set_style_text_align(lv_obj_t *obj, uint32_t v, uint32_t sel); /* 0x44145a */
extern void lv_obj_set_style_radius(lv_obj_t *obj, int32_t v, uint32_t sel); /* 0x44146a */
extern void lv_obj_set_style_opa(lv_obj_t *obj, uint8_t v, uint32_t sel); /* 0x441488 */
extern void lv_obj_set_flex_flow(lv_obj_t *obj, uint32_t flow);           /* 0x48ba78 */
extern void lv_obj_set_flex_align(lv_obj_t *obj, uint32_t main_place, uint32_t cross_place,
                                  uint32_t track_cross_place);            /* 0x48ba92 */
extern lv_obj_t *lv_label_create(lv_obj_t *parent);                       /* 0x499416 */
extern void lv_label_set_text(lv_obj_t *obj, const char *text);           /* 0x49942e */
extern void lv_label_set_long_mode(lv_obj_t *obj, uint32_t long_mode);    /* 0x499678 */

/* Product helpers already reconstructed in g2/src. */
extern void *audio_uart_page_498668(void *parent);                        /* 0x498668 lv_image_create */
extern void audio_uart_page_498680(void *object, const void *source);     /* 0x498680 lv_image_set_src */
extern uint32_t audio_terminal_counter_b_get_5973dc(void);                /* 0x5973dc */
extern void *audio_terminal_query_root_5e4f54(void *parent, uint32_t mode); /* 0x5e4f54 */
extern void audio_terminal_ui_event_5e5484(uint32_t state, uint32_t session,
                                           uint32_t overlay);             /* 0x5e5484 */
extern void audio_terminal_status_apply_list_5ec3c0(uint32_t state);      /* 0x5ec3c0 */

extern uint8_t audio_terminal_ui_state_base[0x2a0];        /* RAM 0x2006e0d0 */
extern uint32_t audio_terminal_display_queue_handle;       /* RAM 0x20074a90, page parent */
extern uint32_t audio_uart_ring_secondary_head_cell;       /* RAM 0x200746e0, font pointer */
extern const uint8_t audio_terminal_result_icon_773258;    /* ROM 0x773258 image descriptor */

static const char title_text[] = "Stop Agent response?"; /* ROM 0x77c8a4 */
static const char yes_text[] = "Yes";                    /* ROM 0x5ec7d0 */
static const char cancel_text[] = "Cancel";              /* ROM 0x78eb54 */

#define SLOT(off) (*(lv_obj_t **)(void *)(audio_terminal_ui_state_base + (off)))

/* Stock 0x005EC30C (terminal dialog pad helper) */
void audio_terminal_pad_all_5ec30c(lv_obj_t *obj, int32_t value, uint32_t selector)
{
    lv_obj_set_style_pad_left(obj, value, selector);
    lv_obj_set_style_pad_right(obj, value, selector);
    lv_obj_set_style_pad_top(obj, value, selector);
    lv_obj_set_style_pad_bottom(obj, value, selector);
}

/* Stock 0x005EC446 (audio_terminal_interrupt_confirm_prepare_5ec446) */
void audio_terminal_interrupt_confirm_prepare_5ec446(void)
{
    lv_obj_t *title_box;
    lv_obj_t *yes;
    lv_obj_t *cancel;
    int32_t line_height;

    if (audio_terminal_display_queue_handle == 0u || SLOT(0x230u) != 0)
        return;

    if (SLOT(0x00u) != 0)
        lv_obj_set_style_opa(SLOT(0x00u), 0x33u, 0u);

    SLOT(0x230u) = audio_terminal_query_root_5e4f54(
        (void *)(uintptr_t)audio_terminal_display_queue_handle, 0u);
    lv_obj_set_size(SLOT(0x230u), 0x22c, LV_SIZE_CONTENT);
    lv_obj_set_style_min_height(SLOT(0x230u), 0x78, 0u);
    lv_obj_set_style_pad_top(SLOT(0x230u), 8, 0u);
    lv_obj_set_style_pad_left(SLOT(0x230u), 8, 0u);
    lv_obj_set_style_pad_right(SLOT(0x230u), 8, 0u);
    lv_obj_set_style_pad_bottom(SLOT(0x230u), 8, 0u);
    lv_obj_set_style_pad_row(SLOT(0x230u), 4, 0u);
    lv_obj_set_flex_flow(SLOT(0x230u), LV_FLEX_FLOW_COLUMN);
    lv_obj_set_flex_align(SLOT(0x230u), LV_FLEX_ALIGN_START, LV_FLEX_ALIGN_START,
                          LV_FLEX_ALIGN_START);
    lv_obj_remove_flag(SLOT(0x230u), LV_OBJ_FLAG_SCROLLABLE);

    /* Title. */
    title_box = lv_obj_create(SLOT(0x230u));
    lv_obj_set_size(title_box, 0x208, LV_SIZE_CONTENT);
    lv_obj_remove_flag(title_box, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_opa(title_box, 0u, 0u);
    lv_obj_set_style_border_width(title_box, 0, 0u);
    audio_terminal_pad_all_5ec30c(title_box, 0, 0u);
    lv_obj_set_style_margin_left(title_box, 0x14, 0u);
    lv_obj_set_style_margin_bottom(title_box, 6, 0u);

    SLOT(0x234u) = lv_label_create(title_box);
    lv_obj_set_width(SLOT(0x234u), 0x208);
    lv_label_set_text(SLOT(0x234u), title_text);
    lv_label_set_long_mode(SLOT(0x234u), LV_LABEL_LONG_WRAP);
    lv_obj_set_style_text_color(SLOT(0x234u), lv_color_hex(0x00ffffffu), 0u);
    lv_obj_set_style_text_align(SLOT(0x234u), LV_TEXT_ALIGN_LEFT, 0u);
    lv_obj_set_style_text_font(SLOT(0x234u),
                               (const lv_font_t *)(uintptr_t)audio_uart_ring_secondary_head_cell, 0u);

    /* Option box with the two choices. */
    SLOT(0x238u) = lv_obj_create(SLOT(0x230u));
    lv_obj_set_size(SLOT(0x238u), 0x208, LV_SIZE_CONTENT);
    lv_obj_remove_flag(SLOT(0x238u), LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_opa(SLOT(0x238u), 0u, 0u);
    lv_obj_set_style_border_width(SLOT(0x238u), 1, 0u);
    lv_obj_set_style_border_color(SLOT(0x238u), lv_color_hex(0x00ffffffu), 0u);
    lv_obj_set_style_border_side(SLOT(0x238u), LV_BORDER_SIDE_TOP, 0u);
    lv_obj_set_style_radius(SLOT(0x238u), 0, 0u);
    lv_obj_set_style_pad_top(SLOT(0x238u), 0, 0u);
    lv_obj_set_style_pad_bottom(SLOT(0x238u), 0, 0u);
    lv_obj_set_style_pad_left(SLOT(0x238u), 0, 0u);
    lv_obj_set_style_pad_right(SLOT(0x238u), 0, 0u);
    lv_obj_set_style_pad_row(SLOT(0x238u), 0, 0u);
    lv_obj_set_style_margin_left(SLOT(0x238u), 0x14, 0u);
    /* lv_font_t.line_height (+0x0c) of the dialog font. */
    line_height = *(const int32_t *)(const void *)(uintptr_t)(audio_uart_ring_secondary_head_cell + 0x0cu);
    lv_obj_set_height(SLOT(0x238u), line_height * 2 + 18);

    yes = lv_label_create(SLOT(0x238u));
    lv_obj_set_width(yes, 0x208);
    lv_label_set_long_mode(yes, LV_LABEL_LONG_WRAP);
    lv_label_set_text(yes, yes_text);
    lv_obj_set_pos(yes, 0, 8);
    lv_obj_set_style_text_color(yes, lv_color_hex(0x00ffffffu), 0u);
    lv_obj_set_style_text_font(yes,
                               (const lv_font_t *)(uintptr_t)audio_uart_ring_secondary_head_cell, 0u);

    cancel = lv_label_create(SLOT(0x238u));
    lv_obj_set_width(cancel, 0x208);
    lv_label_set_long_mode(cancel, LV_LABEL_LONG_WRAP);
    lv_label_set_text(cancel, cancel_text);
    lv_obj_set_pos(cancel, 0, line_height + 10);
    lv_obj_set_style_text_color(cancel, lv_color_hex(0x00333333u), 0u);
    lv_obj_set_style_text_font(cancel,
                               (const lv_font_t *)(uintptr_t)audio_uart_ring_secondary_head_cell, 0u);

    /* Selection marker, positioned outside the flex layout. */
    SLOT(0x23cu) = audio_uart_page_498668(SLOT(0x230u));
    audio_uart_page_498680(SLOT(0x23cu), &audio_terminal_result_icon_773258);
    lv_obj_add_flag(SLOT(0x23cu), LV_OBJ_FLAG_IGNORE_LAYOUT);
    audio_terminal_ui_state_base[0x278u] = 0u;
    lv_obj_update_layout(SLOT(0x230u));
    audio_terminal_status_apply_list_5ec3c0((uint32_t)(uintptr_t)audio_terminal_ui_state_base);
    audio_terminal_ui_event_5e5484(4u, audio_terminal_counter_b_get_5973dc(), 1u);
}

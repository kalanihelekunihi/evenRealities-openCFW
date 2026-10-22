/* Terminal agent-result page constructor, firmware 2.2.6.10.
 * Stock ranges:
 *   0x5ea96e..0x5ea991  scroll event callback (address-taken, pool 0x5eb298)
 *   0x5eae3a..0x5eae93  cursor/row container factory (single caller 0x5eb032)
 *   0x5eae94..0x5eb283  audio_terminal_fsm_prepare_5eae94
 * Literal pool 0x5eb284..0x5eb2a7 (0x5eb290 is the empty string used for the
 * three labels).
 *
 * The page lives under the terminal display parent (RAM 0x20074a90) and its
 * object handles are kept in the terminal UI state cluster (RAM 0x2006e0d0):
 *   +0x000 frame, +0x004 scroll view, +0x008 row column, +0x00c..+0x03b 12 rows,
 *   +0x1cc footer, +0x1d0 footer icon, +0x1d4/+0x1d8/+0x1dc footer labels,
 *   +0x28c "rows built" flag. */
#include <stdint.h>

typedef struct _lv_obj_t lv_obj_t;
typedef struct _lv_event_t lv_event_t;
typedef struct _lv_font_t lv_font_t;
typedef struct {
    uint8_t blue;
    uint8_t green;
    uint8_t red;
} lv_color_t; /* LVGL 9.3 lv_color_t */
typedef void (*lv_event_cb_t)(lv_event_t *e);

#define LV_OBJ_FLAG_HIDDEN 0x01u
#define LV_OBJ_FLAG_SCROLLABLE 0x10u
#define LV_OBJ_FLAG_SCROLL_EFFECTS 0x360u /* ELASTIC|MOMENTUM|CHAIN_HOR|CHAIN_VER */
#define LV_DIR_VER 0x0cu
#define LV_SCROLLBAR_MODE_AUTO 3u
#define LV_EVENT_SCROLL_END 14u
#define LV_EVENT_SCROLL 15u
#define LV_ALIGN_BOTTOM_MID 5u
#define LV_ALIGN_LEFT_MID 7u
#define LV_ALIGN_RIGHT_MID 8u
#define LV_TEXT_ALIGN_CENTER 2u
#define LV_BORDER_SIDE_TOP 2u
#define LV_SIZE_CONTENT 0x3fffffff
#define LV_PCT_100 0x20000064

/* LVGL 9.3 core, compiled from third-party/upstream/lvgl. */
extern lv_obj_t *lv_obj_create(lv_obj_t *parent);                         /* 0x43de82 */
extern void lv_obj_add_flag(lv_obj_t *obj, uint32_t f);                   /* 0x43ded4 */
extern void lv_obj_remove_flag(lv_obj_t *obj, uint32_t f);                /* 0x43dfa4 */
extern _Bool lv_obj_is_valid(const lv_obj_t *obj);                        /* 0x43e2ea */
extern void lv_obj_set_pos(lv_obj_t *obj, int32_t x, int32_t y);          /* 0x43f09a */
extern void lv_obj_set_size(lv_obj_t *obj, int32_t w, int32_t h);         /* 0x43f4c0 */
extern void lv_obj_align(lv_obj_t *obj, uint32_t align, int32_t x, int32_t y); /* 0x43f6b8 */
extern lv_color_t lv_color_hex(uint32_t c);                               /* 0x44104c */
extern void lv_obj_set_style_bg_opa(lv_obj_t *obj, uint8_t v, uint32_t sel);  /* 0x44129e */
extern void lv_obj_set_style_border_color(lv_obj_t *obj, lv_color_t v, uint32_t sel); /* 0x4412ec */
extern void lv_obj_set_style_border_width(lv_obj_t *obj, int32_t v, uint32_t sel); /* 0x44131c */
extern void lv_obj_set_style_border_side(lv_obj_t *obj, uint32_t v, uint32_t sel); /* 0x44132a */
extern void lv_obj_set_style_text_color(lv_obj_t *obj, lv_color_t v, uint32_t sel); /* 0x44140e */
extern void lv_obj_set_style_text_font(lv_obj_t *obj, const lv_font_t *v, uint32_t sel); /* 0x44143e */
extern void lv_obj_set_style_text_align(lv_obj_t *obj, uint32_t v, uint32_t sel); /* 0x44145a */
extern void lv_obj_set_style_radius(lv_obj_t *obj, int32_t v, uint32_t sel); /* 0x44146a */
extern void lv_obj_delete(lv_obj_t *obj);                                 /* 0x44d7b8 */
extern void lv_obj_set_scrollbar_mode(lv_obj_t *obj, uint32_t mode);      /* 0x44e368 */
extern void lv_obj_set_scroll_dir(lv_obj_t *obj, uint32_t dir);           /* 0x44e3ca */
extern int32_t lv_obj_get_scroll_y(const lv_obj_t *obj);                  /* 0x44e498 */
extern uint32_t lv_event_get_code(lv_event_t *e);                         /* 0x450286 */
extern void *lv_obj_add_event_cb(lv_obj_t *obj, lv_event_cb_t cb, uint32_t filter,
                                 void *user_data);                        /* 0x451740 */
extern lv_obj_t *lv_label_create(lv_obj_t *parent);                       /* 0x499416 */
extern void lv_label_set_text(lv_obj_t *obj, const char *text);           /* 0x49942e */

/* Product helpers already reconstructed in g2/src. */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void audio_uart_page_498680(void *object, const void *source);     /* 0x498680 lv_image_set_src */
extern void *audio_terminal_voice_anim_create_597e90(void *parent);       /* 0x597e90 */
extern void audio_terminal_lv_style_four_5ea224(uint32_t object, uint32_t value,
                                                uint32_t selector);       /* 0x5ea224 pad all */
extern void audio_terminal_view_position_5ea926(uint32_t position);       /* 0x5ea926 */
extern void audio_terminal_reset_mode_5eae2c(uint32_t mode);              /* 0x5eae2c */

extern uint8_t audio_terminal_ui_state_base[0x2a0];        /* RAM 0x2006e0d0 */
extern uint32_t audio_terminal_display_queue_handle;       /* RAM 0x20074a90, page parent */
extern uint32_t audio_uart_ring_primary_head_cell;         /* RAM 0x200746dc, font pointer */
extern const uint8_t audio_terminal_asset_7733a8;          /* ROM 0x7733a8 image descriptor */

static const char empty_text[] = ""; /* ROM 0x5eb290 */

#define SLOT(off) (*(lv_obj_t **)(void *)(audio_terminal_ui_state_base + (off)))
#define U32(off) (*(uint32_t *)(void *)(audio_terminal_ui_state_base + (off)))
#define U16(off) (*(uint16_t *)(void *)(audio_terminal_ui_state_base + (off)))

static void pad_all(lv_obj_t *obj)
{
    audio_terminal_lv_style_four_5ea224((uint32_t)(uintptr_t)obj, 0u, 0u);
}

static const lv_font_t *page_font(void)
{
    return (const lv_font_t *)(uintptr_t)audio_uart_ring_primary_head_cell;
}

/* Stock 0x005EA96E (terminal result scroll event callback) */
void audio_terminal_scroll_event_cb_5ea96e(lv_event_t *e)
{
    uint32_t code = lv_event_get_code(e);
    if ((code == LV_EVENT_SCROLL || code == LV_EVENT_SCROLL_END) && SLOT(0x04u) != 0)
        audio_terminal_view_position_5ea926((uint32_t)lv_obj_get_scroll_y(SLOT(0x04u)));
}

/* Stock 0x005EAE3A (terminal result row factory) */
lv_obj_t *audio_terminal_row_create_5eae3a(lv_obj_t *parent)
{
    lv_obj_t *row = lv_obj_create(parent);
    lv_obj_set_size(row, 0x240, 0x1c);
    lv_obj_set_pos(row, 0, 0);
    lv_obj_remove_flag(row, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_opa(row, 0u, 0u);
    lv_obj_set_style_border_width(row, 0, 0u);
    pad_all(row);
    lv_obj_set_style_radius(row, 0, 0u);
    lv_obj_add_flag(row, LV_OBJ_FLAG_HIDDEN);
    return row;
}

/* Stock 0x005EAE94 (audio_terminal_fsm_prepare_5eae94) */
void audio_terminal_fsm_prepare_5eae94(void)
{
    lv_obj_t *box;
    uint32_t i;

    if (audio_terminal_display_queue_handle == 0u)
        return;

    if (SLOT(0x00u) != 0 && lv_obj_is_valid(SLOT(0x00u))) {
        lv_obj_delete(SLOT(0x00u));
        SLOT(0x00u) = 0;
    }
    audio_uart_buffer_zero(audio_terminal_ui_state_base + 0x0cu, 0x30u, 0u);
    U32(0x08u) = 0u;
    U16(0x1c0u) = 0u;
    audio_terminal_ui_state_base[0x1c2u] = 0u;
    U16(0x1c4u) = 0u;
    U32(0x1c8u) = 0u;
    audio_uart_buffer_zero(audio_terminal_ui_state_base + 0x3cu, 0x80u, 0u);
    audio_uart_buffer_zero(audio_terminal_ui_state_base + 0xbcu, 0x104u, 0u);

    /* Frame. */
    SLOT(0x00u) = lv_obj_create((lv_obj_t *)(uintptr_t)audio_terminal_display_queue_handle);
    lv_obj_set_size(SLOT(0x00u), 0x240, 0x120);
    lv_obj_set_pos(SLOT(0x00u), 0, 0);
    lv_obj_remove_flag(SLOT(0x00u), LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_opa(SLOT(0x00u), 0u, 0u);
    lv_obj_set_style_border_width(SLOT(0x00u), 1, 0u);
    lv_obj_set_style_border_color(SLOT(0x00u), lv_color_hex(0x00ffffffu), 0u);
    pad_all(SLOT(0x00u));
    lv_obj_set_style_radius(SLOT(0x00u), 6, 0u);
    lv_obj_add_flag(SLOT(0x00u), LV_OBJ_FLAG_HIDDEN);

    /* Vertical scroll view. */
    SLOT(0x04u) = lv_obj_create(SLOT(0x00u));
    lv_obj_set_pos(SLOT(0x04u), 0, 0x10);
    lv_obj_set_size(SLOT(0x04u), 0x240, 0xe0);
    lv_obj_set_style_radius(SLOT(0x04u), 0, 0u);
    lv_obj_set_style_border_width(SLOT(0x04u), 0, 0u);
    lv_obj_set_style_bg_opa(SLOT(0x04u), 0u, 0u);
    pad_all(SLOT(0x04u));
    lv_obj_add_flag(SLOT(0x04u), LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_scroll_dir(SLOT(0x04u), LV_DIR_VER);
    lv_obj_set_scrollbar_mode(SLOT(0x04u), LV_SCROLLBAR_MODE_AUTO);
    lv_obj_remove_flag(SLOT(0x04u), LV_OBJ_FLAG_SCROLL_EFFECTS);

    /* Row column and its twelve rows. */
    SLOT(0x08u) = lv_obj_create(SLOT(0x04u));
    lv_obj_set_pos(SLOT(0x08u), 0, 0);
    lv_obj_set_size(SLOT(0x08u), 0x240, 0);
    lv_obj_remove_flag(SLOT(0x08u), LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_opa(SLOT(0x08u), 0u, 0u);
    lv_obj_set_style_border_width(SLOT(0x08u), 0, 0u);
    pad_all(SLOT(0x08u));
    lv_obj_set_style_radius(SLOT(0x08u), 0, 0u);
    for (i = 0u; i < 12u; i++)
        SLOT(0x0cu + i * 4u) = audio_terminal_row_create_5eae3a(SLOT(0x08u));

    lv_obj_add_event_cb(SLOT(0x04u), audio_terminal_scroll_event_cb_5ea96e, LV_EVENT_SCROLL, 0);
    lv_obj_add_event_cb(SLOT(0x04u), audio_terminal_scroll_event_cb_5ea96e, LV_EVENT_SCROLL_END, 0);
    audio_terminal_ui_state_base[0x28cu] = 1u;
    audio_terminal_reset_mode_5eae2c(1u);

    /* Footer bar. */
    SLOT(0x1ccu) = lv_obj_create(SLOT(0x00u));
    lv_obj_align(SLOT(0x1ccu), LV_ALIGN_BOTTOM_MID, 0, 0);
    lv_obj_set_size(SLOT(0x1ccu), 0x240, 0x28);
    lv_obj_remove_flag(SLOT(0x1ccu), LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_radius(SLOT(0x1ccu), 0, 0u);
    lv_obj_set_style_border_width(SLOT(0x1ccu), 0, 0u);
    lv_obj_set_style_bg_opa(SLOT(0x1ccu), 0u, 0u);
    pad_all(SLOT(0x1ccu));

    SLOT(0x1d0u) = audio_terminal_voice_anim_create_597e90(SLOT(0x1ccu));
    audio_uart_page_498680(SLOT(0x1d0u), &audio_terminal_asset_7733a8);
    lv_obj_set_size(SLOT(0x1d0u), LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_obj_align(SLOT(0x1d0u), LV_ALIGN_LEFT_MID, 6, 0);

    box = lv_obj_create(SLOT(0x1ccu));
    lv_obj_set_size(box, 0x21c, LV_PCT_100);
    lv_obj_align(box, LV_ALIGN_LEFT_MID, 0x1c, 0);
    lv_obj_set_style_bg_opa(box, 0u, 0u);
    lv_obj_set_style_border_width(box, 1, 0u);
    lv_obj_set_style_border_color(box, lv_color_hex(0x00ffffffu), 0u);
    lv_obj_set_style_border_side(box, LV_BORDER_SIDE_TOP, 0u);
    lv_obj_set_style_radius(box, 0, 0u);
    pad_all(box);

    SLOT(0x1d4u) = lv_label_create(box);
    lv_obj_align(SLOT(0x1d4u), LV_ALIGN_LEFT_MID, 0, 0);
    lv_obj_set_size(SLOT(0x1d4u), LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_label_set_text(SLOT(0x1d4u), empty_text);
    lv_obj_set_style_text_color(SLOT(0x1d4u), lv_color_hex(0x00ffffffu), 0u);
    lv_obj_set_style_text_align(SLOT(0x1d4u), LV_TEXT_ALIGN_CENTER, 0u);
    lv_obj_set_style_text_font(SLOT(0x1d4u), page_font(), 0u);

    SLOT(0x1d8u) = lv_label_create(box);
    lv_obj_align(SLOT(0x1d8u), LV_ALIGN_RIGHT_MID, -262, 0);
    lv_obj_set_size(SLOT(0x1d8u), LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_label_set_text(SLOT(0x1d8u), empty_text);
    lv_obj_add_flag(SLOT(0x1d8u), LV_OBJ_FLAG_HIDDEN);
    lv_obj_set_style_text_color(SLOT(0x1d8u), lv_color_hex(0x00ffffffu), 0u);
    lv_obj_set_style_text_align(SLOT(0x1d8u), LV_TEXT_ALIGN_CENTER, 0u);
    lv_obj_set_style_text_font(SLOT(0x1d8u), page_font(), 0u);

    SLOT(0x1dcu) = lv_label_create(box);
    lv_obj_align(SLOT(0x1dcu), LV_ALIGN_RIGHT_MID, 0, 0);
    lv_obj_set_size(SLOT(0x1dcu), LV_SIZE_CONTENT, LV_SIZE_CONTENT);
    lv_label_set_text(SLOT(0x1dcu), empty_text);
    lv_obj_set_style_text_color(SLOT(0x1dcu), lv_color_hex(0x00333333u), 0u);
    lv_obj_set_style_text_align(SLOT(0x1dcu), LV_TEXT_ALIGN_CENTER, 0u);
    lv_obj_set_style_text_font(SLOT(0x1dcu), page_font(), 0u);
}

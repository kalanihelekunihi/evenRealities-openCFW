/* Dashboard main screen layout helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c
 * (log tag "dashborad.ui"). Native 0x4e75b0..0x4e75e1 (static pad_all copy),
 * 0x4e75e2..0x4e7711 (dashboard_layout_apply_geo) and 0x4e7712..0x4e772b
 * (state reset); literal pools 0x4e7fd8..0x4e7ff7, 0x4e8134 and 0x4e835c
 * shared with ui/a-30-dashboard-main-screen and ui/a-31-dashboard-main-screen.
 *
 * The layout record is {base_pos, widget_count, widget_type[]}. Without
 * widgets the watchface is placed by base_pos (0 -> x 0, 1 -> 0xbc,
 * 2 -> 0x178); with widgets the watchface sits right (x 0x178, widget column
 * at 0, frame aligned 1, indicator x 0x16c) when base_pos is 2 and left
 * otherwise (x 0, widget column 0xe0, indicator 0xe0 - 16). */
#include <stdint.h>

#define DASH_WIDGET_COUNT 5u

#define LV_ALIGN_TOP_LEFT  1u
#define LV_ALIGN_TOP_RIGHT 3u

/* Ext page / watchface geometry (RAM 0x2000420c, initialised data). */
typedef struct {
    int32_t watchface_x;      /* +0x00 */
    int32_t widget_col_x;     /* +0x04 */
    uint8_t align;            /* +0x08 lv_align_t */
    uint8_t pad09[3];
    int32_t indicator_x;      /* +0x0c */
    int32_t width_scale;      /* +0x10 */
    int32_t has_widget;       /* +0x14 */
} g2_dashboard_ext_cfg_t;
_Static_assert(sizeof(g2_dashboard_ext_cfg_t) == 0x18u, "ext cfg");

typedef struct {
    uint8_t base_pos;
    uint8_t widget_count;
    uint8_t widget_type[];
} g2_dashboard_layout_t;

extern g2_dashboard_ext_cfg_t g2_dashboard_ext_cfg_2000420c;            /* RAM 0x2000420c */
extern uint8_t g2_dashboard_widget_types_20004224[DASH_WIDGET_COUNT];  /* RAM 0x20004224 */
extern int32_t g2_dashboard_tile_index_20074bac;                       /* RAM 0x20074bac */
extern uint32_t g2_dashboard_ext_index_20074bb0;                       /* RAM 0x20074bb0 */
extern int32_t g2_dashboard_last_saved_tile;                           /* RAM 0x20074bb4 */

extern void audio_uart_page_44120e(void *obj, int32_t v, uint32_t sel); /* pad_top */
extern void audio_uart_page_44121c(void *obj, int32_t v, uint32_t sel); /* pad_bottom */
extern void audio_uart_page_44122a(void *obj, int32_t v, uint32_t sel); /* pad_left */
extern void audio_uart_page_441238(void *obj, int32_t v, uint32_t sel); /* pad_right */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void dashboard_obj_set_style_pad_all_4e75b0(void *obj, int32_t v, uint32_t sel);
void dashboard_apply_layout_4e75e2(const g2_dashboard_layout_t *layout);
void dashboard_main_screen_reset_4e7712(void);

static const char module_tag[] = "dashborad.ui"; /* ROM 0x789d20 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\screens\\ui_DashBaord_Main_Screen.c"; /* ROM 0x6e1d2c */
static const char fn_apply_geo[] = "dashboard_layout_apply_geo"; /* ROM 0x773dd4 */
static const char geo_text[] =
    "apply geo: base_pos=%d widget_count=%u has_widget=%d watchface_x=%d widget_col_x=%d"; /* ROM 0x6ea8b8 */
static const char geo_short[] =
    "[dashborad.ui]apply geo: base_pos=%d widget_count=%u has_widget=%d watchface_x=%d widget_col_x=%d"; /* ROM 0x6dbc54 */

/* lv_obj_set_style_pad_all, inlined copy in this file. */
void dashboard_obj_set_style_pad_all_4e75b0(void *obj, int32_t v, uint32_t sel)
{
    audio_uart_page_44122a(obj, v, sel);
    audio_uart_page_441238(obj, v, sel);
    audio_uart_page_44120e(obj, v, sel);
    audio_uart_page_44121c(obj, v, sel);
}

void dashboard_apply_layout_4e75e2(const g2_dashboard_layout_t *layout)
{
    g2_dashboard_ext_cfg_t *const cfg = &g2_dashboard_ext_cfg_2000420c;
    uint8_t i;

    if (layout->widget_count == 0u) {
        cfg->has_widget = 0;
        cfg->widget_col_x = 0;
        cfg->align = LV_ALIGN_TOP_RIGHT;
        cfg->indicator_x = 0;
        cfg->width_scale = -1;
        switch (layout->base_pos) {
        case 0u:
            cfg->watchface_x = 0;
            break;
        case 1u:
            cfg->watchface_x = 0xbc;
            break;
        case 2u:
            cfg->watchface_x = 0x178;
            break;
        default:
            cfg->watchface_x = 0;
            break;
        }
    } else {
        cfg->has_widget = 1;
        if (layout->base_pos == 2u) {
            cfg->watchface_x = 0x178;
            cfg->widget_col_x = 0;
            cfg->align = LV_ALIGN_TOP_LEFT;
            cfg->indicator_x = 0x16c;
            cfg->width_scale = 1;
        } else {
            cfg->watchface_x = 0;
            cfg->widget_col_x = 0xe0;
            cfg->align = LV_ALIGN_TOP_RIGHT;
            cfg->indicator_x = cfg->widget_col_x - 16;
            cfg->width_scale = -1;
        }
    }

    (void)aeabi_memset_43c0e4(g2_dashboard_widget_types_20004224, DASH_WIDGET_COUNT, 0);
    for (i = 0u; i < layout->widget_count; i++)
        g2_dashboard_widget_types_20004224[i] = layout->widget_type[i];

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module_tag, source_file, fn_apply_geo, 173u, geo_text,
                           (uint32_t)layout->base_pos, (uint32_t)layout->widget_count,
                           cfg->has_widget, cfg->watchface_x, cfg->widget_col_x);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0d400000u, geo_short, geo_short, (uint32_t)layout->base_pos,
                                  (uint32_t)layout->widget_count, cfg->has_widget,
                                  cfg->watchface_x, cfg->widget_col_x);
}

void dashboard_main_screen_reset_4e7712(void)
{
    g2_dashboard_last_saved_tile = 0;
    g2_dashboard_tile_index_20074bac = 0;
    g2_dashboard_ext_index_20074bb0 = 0u;
}

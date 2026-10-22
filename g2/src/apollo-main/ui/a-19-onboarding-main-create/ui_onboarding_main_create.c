/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c
 * (page create code following the handlers in ui/a-18-onboarding-main-page).
 * Native 0x4AAB90..0x4AAE1F (welcome view) and 0x4AB08C..0x4AB6B5 (main
 * view); literal pools 0x4AB554..0x4AB55B ("0 9", "5 3"), 0x4AB6B8..0x4AB6BF
 * ("21*", "10"), 0x4AB6C8..0x4AB6E3, 0x4ABA4C..0x4ABA57, 0x4ABB9C and
 * 0x4ABC04..0x4ABC6B. The layout helper 0x4AB004 is in ui/u-02-onboarding.
 *
 * LVGL 9.3 fork APIs are reached through the shared audio_uart_page_<addr>
 * names. Align ids: 1 TOP_LEFT, 3 TOP_RIGHT, 5 BOTTOM_MID, 7 LEFT_MID,
 * 15 OUT_BOTTOM_RIGHT, 17 OUT_LEFT_MID, 20 OUT_RIGHT_MID. Object flags:
 * 0x1 HIDDEN, 0x2 CLICKABLE, 0x10 SCROLLABLE, 0x10000 (fork flag set on the
 * status-bar icons). Selector 0x40000 is LV_PART_SELECTED. */
#include <stdint.h>

#define LV_SIZE_CONTENT          0x3fffffff
#define LV_PART_SELECTED         0x40000u
#define LV_DIR_VER               0x0cu
#define LV_GRAD_DIR_VER          1u
#define LV_TEXT_ALIGN_LEFT       1u
#define LV_ROLLER_MODE_INFINITE  1u
#define LV_OBJ_FLAG_HIDDEN       0x1u
#define LV_OBJ_FLAG_CLICKABLE    0x2u
#define LV_OBJ_FLAG_SCROLLABLE   0x10u
#define LV_OBJ_FLAG_ICON_10000   0x10000u
#define ONB_ALIGN_TOP_LEFT       1u
#define ONB_ALIGN_TOP_RIGHT      3u
#define ONB_ALIGN_BOTTOM_MID     5u
#define ONB_ALIGN_LEFT_MID       7u
#define ONB_ALIGN_OUT_BOTTOM_RIGHT 15u
#define ONB_ALIGN_OUT_LEFT_MID   17u
#define ONB_ALIGN_OUT_RIGHT_MID  20u
#define ONB_PAGE_WIDE            576 /* 0x240 */
#define ONB_PAGE_HEIGHT          288 /* 0x120 */
#define ONB_TILE_WIDTH           352 /* 0x160 */
#define ONB_TILE_PITCH           304 /* 0x130 */
#define ONB_TILE_LIST_X          224 /* 0xe0 */
#define ONB_ICON_SIZE            24

typedef struct {
    uint32_t header[3];
    uint32_t data_size;
    const void *data;
    const void *reserved[2];
} g2_lv_image_dsc_t;
_Static_assert(sizeof(g2_lv_image_dsc_t) == 0x1cu, "LVGL 9 image descriptor");

/* RAM state shared with ui/a-18-onboarding-main-page. */
extern void *g2_onboarding_root_obj;                   /* RAM 0x20074834 */
extern void *g2_onboarding_main_obj_20074ce0;          /* RAM 0x20074ce0 scrolling tile list (tileview) */
extern int32_t g2_onboarding_feature_page_open;        /* RAM 0x20074ce4 */
extern void *g2_onboarding_main_obj_20074ce8;          /* RAM 0x20074ce8 feature page container (tileview) */
extern void *g2_onboarding_main_obj_20074cec;          /* RAM 0x20074cec welcome container */
extern void *g2_onboarding_main_obj_20074cf0;          /* RAM 0x20074cf0 welcome image */
extern void *g2_onboarding_main_obj_20074cf4;          /* RAM 0x20074cf4 welcome lv_roller */
extern void *g2_onboarding_main_obj_20074cf8;          /* RAM 0x20074cf8 status label */
extern void *g2_onboarding_main_obj_20074d0c;          /* RAM 0x20074d0c main view container */
extern void *g2_onboarding_main_obj_20074d10;          /* RAM 0x20074d10 hour label */
extern void *g2_onboarding_main_obj_20074d14;          /* RAM 0x20074d14 minute label */
extern void *g2_onboarding_main_obj_20074d18;          /* RAM 0x20074d18 weather icon */
extern void *g2_onboarding_main_obj_20074d1c;          /* RAM 0x20074d1c temperature label */
extern void *g2_onboarding_main_obj_20074d20;          /* RAM 0x20074d20 icon left of the battery label */
extern void *g2_onboarding_main_obj_20074d24;          /* RAM 0x20074d24 battery label */
extern void *g2_onboarding_main_obj_20074d28;          /* RAM 0x20074d28 battery icon */
extern void *g2_onboarding_main_obj_20074d2c;          /* RAM 0x20074d2c date label */
extern void *g2_onboarding_indicator_objs[];           /* RAM 0x20073c68 */
extern void *g2_onboarding_tile_list[6][2];            /* RAM 0x200734ec {tile, frame} */
extern int32_t g2_onboarding_indicator_count;          /* RAM 0x200042b4 (.data) */
extern const char *g2_onboarding_weekday_keys[];       /* RAM 0x20004294 (.data); [3] used */
extern uint32_t audio_uart_ring_secondary_head_cell;   /* RAM 0x200746e0, current lv_font_t * */

/* ROM objects. */
extern const g2_lv_image_dsc_t g2_onboarding_welcome_img_76b6dc;
extern const g2_lv_image_dsc_t g2_onboarding_weather_img_7748e0;
extern const g2_lv_image_dsc_t g2_onboarding_battery_img_769e24; /* > 80 % */
extern const g2_lv_image_dsc_t g2_onboarding_status_img_76e7f8;
extern const uint8_t g2_onboarding_time_font_754824[];  /* lv_font_t */
extern const uint8_t g2_translate_lang_pair_font[];     /* ROM 0x7547b8 lv_font_t */
extern const int32_t g2_onboarding_indicator_x_78f504;      /* 206 */
extern const int32_t g2_onboarding_indicator_y0_78f508;     /* 114 */
extern const int32_t g2_onboarding_indicator_size_78f50c;   /* 6 */
extern const int32_t g2_onboarding_indicator_pitch_78f510;  /* 16 */

/* LVGL. */
extern void *audio_uart_page_43de82(void *parent);                      /* lv_obj_create */
extern void audio_uart_page_43ded4(void *obj, uint32_t flags);          /* lv_obj_add_flag */
extern void audio_uart_page_43dfa4(void *obj, uint32_t flags);          /* lv_obj_remove_flag */
extern void audio_uart_page_43f09a(void *obj, int32_t x, int32_t y);    /* lv_obj_set_pos */
extern void audio_uart_page_43f0e0(void *obj, int32_t x);               /* lv_obj_set_x */
extern void audio_uart_page_43f142(void *obj, int32_t y);               /* lv_obj_set_y */
extern void audio_uart_page_43f4c0(void *obj, int32_t w, int32_t h);    /* lv_obj_set_size */
extern void audio_uart_page_43f506(void *obj, int32_t width);           /* lv_obj_set_width */
extern void audio_uart_page_43f568(void *obj, int32_t height);          /* lv_obj_set_height */
extern void lv_obj_align_43f6b8(void *obj, uint8_t align, int32_t x, int32_t y); /* lv_obj_align */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                          /* lv_obj_align_to */
extern uint32_t audio_uart_page_44104c(uint32_t rgb);                   /* lv_color_hex */
extern void audio_uart_page_44127e(void *obj, uint32_t color, uint32_t sel); /* bg_color */
extern void audio_uart_page_44129e(void *obj, uint32_t opa, uint32_t sel);   /* bg_opa */
extern void audio_uart_page_4412ae(void *obj, uint32_t color, uint32_t sel); /* bg_grad_color */
extern void audio_uart_page_4412ce(void *obj, uint32_t dir, uint32_t sel);   /* bg_grad_dir */
extern void audio_uart_page_4412ec(void *obj, uint32_t color, uint32_t sel); /* border_color */
extern void audio_uart_page_44130c(void *obj, uint32_t opa, uint32_t sel);   /* border_opa */
extern void audio_uart_page_44131c(void *obj, int32_t v, uint32_t sel);      /* border_width */
extern void audio_uart_page_44133a(void *obj, int32_t v, uint32_t sel);      /* outline_width */
extern void audio_uart_page_441378(void *obj, int32_t v, uint32_t sel);      /* outline_pad */
extern void audio_uart_page_441386(void *obj, int32_t v, uint32_t sel);      /* shadow_width */
extern void audio_uart_page_441394(void *obj, int32_t v, uint32_t sel);      /* shadow_offset_x */
extern void audio_uart_page_4413a2(void *obj, int32_t v, uint32_t sel);      /* shadow_offset_y */
extern void audio_uart_page_4413b0(void *obj, int32_t v, uint32_t sel);      /* shadow_spread */
extern void audio_uart_page_44140e(void *obj, uint32_t color, uint32_t sel); /* text_color */
extern void audio_uart_page_44142e(void *obj, uint32_t opa, uint32_t sel);   /* text_opa */
extern void audio_uart_page_44143e(void *obj, uint32_t font, uint32_t sel);  /* text_font */
extern void audio_uart_page_44145a(void *obj, uint32_t align, uint32_t sel); /* text_align */
extern void audio_uart_page_44146a(void *obj, int32_t v, uint32_t sel);      /* radius */
extern void ui_onboarding_main_sub_004A856C(void *obj, int32_t v, uint32_t sel); /* lv_obj_set_style_pad_all copy */
extern uint32_t audio_uart_page_44e368(void *obj, uint32_t mode);       /* lv_obj_set_scrollbar_mode */
extern void *audio_uart_page_498668(void *parent);                      /* lv_image_create */
extern void audio_uart_page_498680(void *image, const void *src);       /* lv_image_set_src */
extern void *audio_uart_page_499416(void *parent);                      /* lv_label_create */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern void *lv_roller_create_50ea10(void *parent);
extern void lv_roller_set_options_50ea28(void *roller, const char *options, uint32_t mode);
extern void *lv_tileview_create_50fef8(void *parent);
extern void *lv_tileview_add_tile_50ff0e(void *tileview, uint8_t col, uint8_t row, uint32_t dir);

/* Product helpers. */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);    /* memset 0x43c0e4 */
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern uint32_t audio_uart_page_460084(const char *key);                        /* i18n index of key */
extern const char *audio_uart_page_45fffe(const char *key, uint32_t index);    /* localized text */
extern int32_t ui_common_api_fn_00509f7a(int32_t *x, int32_t *y);               /* page offset */
extern void ui_onboarding_main_sub_004A9D70(void);                              /* tile list from columns */
extern void onboarding_news_data_reset_50a07e(void);                            /* clears 0xa8-byte news state */
extern int32_t onboarding_news_page_show_50a47e(uint32_t index);
extern void ui_onboarding_stock_sub_0050DCBC(uint32_t first);

static const char s_setting_up[] = "ID_ONBOARDING_SETTING_UP"; /* ROM 0x774138 */
static const char s_welcome_lines[] = /* ROM 0x6d0df4 */
    "Setup your glasses using the Even Realities app.\n"
    "Richten Sie Ihre Brille mit der Even Realities App ein.\n"
    "Configura tus gafas con la aplicaci\xc3\xb3n Even Realities.\n"
    "Configura i tuoi occhiali con l\xe2\x80\x99" "app Even Realities.";
static const char s_hour_digits[] = "0 9";   /* ROM 0x4ab554 */
static const char s_minute_digits[] = "5 3"; /* ROM 0x4ab558 */
static const char s_temperature[] = "21*";   /* ROM 0x4ab6b8, '*' is the degree glyph */
static const char s_battery[] = "10";        /* ROM 0x4ab6bc */
static const char s_date_fmt[] = "%s 9/12";  /* ROM 0x78ed54 */

#define ONB_TR(key) audio_uart_page_45fffe((key), audio_uart_page_460084(key))

/* Clears border, outline, shadow and padding of a plain container and makes
 * its background transparent black. */
static void onb_plain_container(void *obj, int32_t pad)
{
    audio_uart_page_44127e(obj, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(obj, 0u, 0u);
    audio_uart_page_44131c(obj, 0, 0u);
    audio_uart_page_4412ec(obj, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44133a(obj, 0, 0u);
    audio_uart_page_441378(obj, 0, 0u);
    audio_uart_page_441386(obj, 0, 0u);
    audio_uart_page_4413b0(obj, 0, 0u);
    audio_uart_page_441394(obj, 0, 0u);
    audio_uart_page_4413a2(obj, 0, 0u);
    ui_onboarding_main_sub_004A856C(obj, pad, 0u);
    audio_uart_page_44146a(obj, 0, 0u);
    audio_uart_page_44140e(obj, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44142e(obj, 0xffu, 0u);
}

/* Welcome view (process 0/1): logo image on the left, rotating four-language
 * roller and the hidden "setting up" label. Called with the page root by the
 * page create code (bl at 0x4ABB72, not an inventory row). */
void ui_onboarding_main_welcome_create_4aab90(void *parent)
{
    g2_onboarding_main_obj_20074cec = audio_uart_page_43de82(parent);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074cec, ONB_PAGE_WIDE);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074cec, LV_SIZE_CONTENT);
    lv_obj_align_43f6b8(g2_onboarding_main_obj_20074cec, ONB_ALIGN_BOTTOM_MID, 0, 0);
    onb_plain_container(g2_onboarding_main_obj_20074cec, 12);

    g2_onboarding_main_obj_20074cf0 = audio_uart_page_498668(g2_onboarding_main_obj_20074cec);
    audio_uart_page_498680(g2_onboarding_main_obj_20074cf0, &g2_onboarding_welcome_img_76b6dc);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074cf0, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074cf0, LV_SIZE_CONTENT);
    lv_obj_align_43f6b8(g2_onboarding_main_obj_20074cf0, ONB_ALIGN_LEFT_MID, 0, 0);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cf0, LV_OBJ_FLAG_SCROLLABLE);

    g2_onboarding_main_obj_20074cf4 = lv_roller_create_50ea10(g2_onboarding_main_obj_20074cec);
    lv_roller_set_options_50ea28(g2_onboarding_main_obj_20074cf4, s_welcome_lines, LV_ROLLER_MODE_INFINITE);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074cf4, 0x204);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074cf4, 0x1e);
    lv_obj_align_43f6b8(g2_onboarding_main_obj_20074cf4, ONB_ALIGN_LEFT_MID, 0x24, 0);
    audio_uart_page_44145a(g2_onboarding_main_obj_20074cf4, LV_TEXT_ALIGN_LEFT, 0u);
    audio_uart_page_44143e(g2_onboarding_main_obj_20074cf4, audio_uart_ring_secondary_head_cell, 0u);
    audio_uart_page_44140e(g2_onboarding_main_obj_20074cf4, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074cf4, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_main_obj_20074cf4, 0xffu, 0u);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074cf4, 0, 0u);
    audio_uart_page_4412ae(g2_onboarding_main_obj_20074cf4, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_4412ce(g2_onboarding_main_obj_20074cf4, LV_GRAD_DIR_VER, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074cf4, 0, 0u);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074cf4, audio_uart_page_44104c(0x000000u), LV_PART_SELECTED);
    audio_uart_page_44129e(g2_onboarding_main_obj_20074cf4, 0xffu, LV_PART_SELECTED);
    audio_uart_page_44140e(g2_onboarding_main_obj_20074cf4, audio_uart_page_44104c(0xffffffu), LV_PART_SELECTED);

    g2_onboarding_main_obj_20074cf8 = audio_uart_page_499416(g2_onboarding_main_obj_20074cec);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074cf8, 0x204);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074cf8, LV_SIZE_CONTENT);
    lv_obj_align_43f6b8(g2_onboarding_main_obj_20074cf8, ONB_ALIGN_LEFT_MID, 0x24, 0);
    audio_uart_page_49942e(g2_onboarding_main_obj_20074cf8, ONB_TR(s_setting_up));
    audio_uart_page_44143e(g2_onboarding_main_obj_20074cf8, audio_uart_ring_secondary_head_cell, 0u);
    audio_uart_page_44140e(g2_onboarding_main_obj_20074cf8, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074cf8, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_44129e(g2_onboarding_main_obj_20074cf8, 0xffu, 0u);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074cf8, 0, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074cf8, 0, 0u);
    audio_uart_page_44146a(g2_onboarding_main_obj_20074cf8, 0, 0u);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074cf8, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074cf8, LV_OBJ_FLAG_HIDDEN);
}

static void *onb_status_label(void *parent, const char *text, const void *font)
{
    void *label = audio_uart_page_499416(parent);
    audio_uart_page_43f506(label, LV_SIZE_CONTENT);
    audio_uart_page_43f568(label, LV_SIZE_CONTENT);
    audio_uart_page_49942e(label, text);
    audio_uart_page_44143e(label, (uint32_t)(uintptr_t)font, 0u);
    return label;
}

static void *onb_status_icon(void *parent, const g2_lv_image_dsc_t *src)
{
    void *icon = audio_uart_page_498668(parent);
    audio_uart_page_498680(icon, src);
    audio_uart_page_43f506(icon, ONB_ICON_SIZE);
    audio_uart_page_43f568(icon, ONB_ICON_SIZE);
    return icon;
}

/* Main view (process 2..4): clock, date and status bar on the left, the
 * page-indicator dots, the vertical tile list of feature cards on the right
 * and the hidden feature page container (bl at 0x4ABB78). */
void ui_onboarding_main_view_create_4ab08c(void *parent)
{
    (void)parent; /* the caller passes the page root; stock reloads it from RAM */
    int32_t page_x = 0;
    int32_t page_y = 0;
    char date[32];

    (void)ui_common_api_fn_00509f7a(&page_x, &page_y);

    g2_onboarding_main_obj_20074d0c = audio_uart_page_43de82(g2_onboarding_root_obj);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d0c, ONB_PAGE_WIDE);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d0c, ONB_PAGE_HEIGHT);
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074d0c, page_x, page_y);
    onb_plain_container(g2_onboarding_main_obj_20074d0c, 0);

    g2_onboarding_main_obj_20074d10 = audio_uart_page_499416(g2_onboarding_main_obj_20074d0c);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d10, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d10, LV_SIZE_CONTENT);
    audio_uart_page_43f0e0(g2_onboarding_main_obj_20074d10, 0x2a);
    audio_uart_page_43f142(g2_onboarding_main_obj_20074d10, 0x46);
    audio_uart_page_44143e(g2_onboarding_main_obj_20074d10, (uint32_t)(uintptr_t)g2_onboarding_time_font_754824, 0u);
    audio_uart_page_49942e(g2_onboarding_main_obj_20074d10, s_hour_digits);

    g2_onboarding_main_obj_20074d14 = audio_uart_page_499416(g2_onboarding_main_obj_20074d0c);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d14, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d14, LV_SIZE_CONTENT);
    audio_uart_page_43f0e0(g2_onboarding_main_obj_20074d14, 0x2a);
    audio_uart_page_43f142(g2_onboarding_main_obj_20074d14, 0x9c);
    audio_uart_page_44143e(g2_onboarding_main_obj_20074d14, (uint32_t)(uintptr_t)g2_onboarding_time_font_754824, 0u);
    audio_uart_page_49942e(g2_onboarding_main_obj_20074d14, s_minute_digits);

    g2_onboarding_main_obj_20074d2c = audio_uart_page_499416(g2_onboarding_main_obj_20074d0c);
    audio_uart_page_43f506(g2_onboarding_main_obj_20074d2c, LV_SIZE_CONTENT);
    audio_uart_page_43f568(g2_onboarding_main_obj_20074d2c, LV_SIZE_CONTENT);
    audio_uart_page_43f0e0(g2_onboarding_main_obj_20074d2c, 0);
    audio_uart_page_43f142(g2_onboarding_main_obj_20074d2c, 3);
    audio_uart_buffer_zero(date, sizeof(date), 0u);
    (void)audio_ble_format_to_buffer(date, s_date_fmt, ONB_TR(g2_onboarding_weekday_keys[3]));
    audio_uart_page_49942e(g2_onboarding_main_obj_20074d2c, date);
    audio_uart_page_44143e(g2_onboarding_main_obj_20074d2c, (uint32_t)(uintptr_t)g2_translate_lang_pair_font, 0u);

    g2_onboarding_main_obj_20074d18 = onb_status_icon(g2_onboarding_main_obj_20074d0c, &g2_onboarding_weather_img_7748e0);
    audio_uart_page_43f0e0(g2_onboarding_main_obj_20074d18, 0);
    audio_uart_page_43f142(g2_onboarding_main_obj_20074d18, 0x106);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d18, LV_OBJ_FLAG_ICON_10000);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d18, LV_OBJ_FLAG_SCROLLABLE);

    g2_onboarding_main_obj_20074d1c = onb_status_label(g2_onboarding_main_obj_20074d0c, s_temperature,
                                                       g2_translate_lang_pair_font);
    audio_uart_page_43f6d6(g2_onboarding_main_obj_20074d1c, g2_onboarding_main_obj_20074d18,
                           ONB_ALIGN_OUT_RIGHT_MID, 8, 0);

    g2_onboarding_main_obj_20074d28 = onb_status_icon(g2_onboarding_main_obj_20074d0c, &g2_onboarding_battery_img_769e24);
    audio_uart_page_43f0e0(g2_onboarding_main_obj_20074d28, 0xae);
    audio_uart_page_43f142(g2_onboarding_main_obj_20074d28, 2);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d28, LV_OBJ_FLAG_ICON_10000);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d28, LV_OBJ_FLAG_SCROLLABLE);

    g2_onboarding_main_obj_20074d24 = onb_status_label(g2_onboarding_main_obj_20074d0c, s_battery,
                                                       g2_translate_lang_pair_font);
    audio_uart_page_43f6d6(g2_onboarding_main_obj_20074d24, g2_onboarding_main_obj_20074d28,
                           ONB_ALIGN_OUT_BOTTOM_RIGHT, 0, 237);

    g2_onboarding_main_obj_20074d20 = onb_status_icon(g2_onboarding_main_obj_20074d0c, &g2_onboarding_status_img_76e7f8);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074d20, LV_OBJ_FLAG_ICON_10000);
    audio_uart_page_43dfa4(g2_onboarding_main_obj_20074d20, LV_OBJ_FLAG_SCROLLABLE);
    audio_uart_page_43f6d6(g2_onboarding_main_obj_20074d20, g2_onboarding_main_obj_20074d24,
                           ONB_ALIGN_OUT_LEFT_MID, -8, 0);

    /* Page indicator: first dot white, the rest dark grey. */
    g2_onboarding_indicator_count = 2;
    for (int32_t i = 0; i < g2_onboarding_indicator_count; i++) {
        g2_onboarding_indicator_objs[i] = audio_uart_page_43de82(g2_onboarding_main_obj_20074d0c);
        audio_uart_page_43f4c0(g2_onboarding_indicator_objs[i], g2_onboarding_indicator_size_78f50c,
                               g2_onboarding_indicator_size_78f50c);
        audio_uart_page_44131c(g2_onboarding_indicator_objs[i], 0, 0u);
        audio_uart_page_44146a(g2_onboarding_indicator_objs[i], 0, 0u);
        audio_uart_page_44130c(g2_onboarding_indicator_objs[i], 0u, 0u);
        audio_uart_page_43f09a(g2_onboarding_indicator_objs[i], g2_onboarding_indicator_x_78f504,
                               g2_onboarding_indicator_pitch_78f510 * i + g2_onboarding_indicator_y0_78f508);
        audio_uart_page_44131c(g2_onboarding_indicator_objs[i], 0, 0u);
        if (i == 0)
            audio_uart_page_44127e(g2_onboarding_indicator_objs[0], audio_uart_page_44104c(0xffffffu), 0u);
        else
            audio_uart_page_44127e(g2_onboarding_indicator_objs[i], audio_uart_page_44104c(0x222222u), 0u);
        audio_uart_page_44129e(g2_onboarding_indicator_objs[i], 0xffu, 0u);
        audio_uart_page_43dfa4(g2_onboarding_indicator_objs[i], LV_OBJ_FLAG_CLICKABLE);
    }

    /* Vertical tile list, one 352x288 framed card per tile. */
    g2_onboarding_main_obj_20074ce0 = lv_tileview_create_50fef8(g2_onboarding_root_obj);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074ce0, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_43f4c0(g2_onboarding_main_obj_20074ce0, ONB_TILE_WIDTH, ONB_TILE_PITCH);
    audio_uart_page_43f09a(g2_onboarding_main_obj_20074ce0, ONB_TILE_LIST_X, page_y);
    (void)audio_uart_page_44e368(g2_onboarding_main_obj_20074ce0, 0u);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074ce0, 0, 0u);
    audio_uart_page_44146a(g2_onboarding_main_obj_20074ce0, 0, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074ce0, 0, 0u);
    ui_onboarding_main_sub_004A9D70();
    onboarding_news_data_reset_50a07e();
    for (uint32_t i = 0u; (int32_t)i < g2_onboarding_indicator_count; i++) {
        g2_onboarding_tile_list[i][0] =
            lv_tileview_add_tile_50ff0e(g2_onboarding_main_obj_20074ce0, 0u, (uint8_t)i, LV_DIR_VER);
        ui_onboarding_main_sub_004A856C(g2_onboarding_tile_list[i][0], 0, 0u);
        g2_onboarding_tile_list[i][1] = audio_uart_page_43de82(g2_onboarding_tile_list[i][0]);
        audio_uart_page_43f4c0(g2_onboarding_tile_list[i][1], ONB_TILE_WIDTH, ONB_PAGE_HEIGHT);
        audio_uart_page_43f6d6(g2_onboarding_tile_list[i][1], g2_onboarding_tile_list[i][0],
                               ONB_ALIGN_TOP_LEFT, 0, 0);
        audio_uart_page_44129e(g2_onboarding_tile_list[i][1], 0u, 0u);
        audio_uart_page_44131c(g2_onboarding_tile_list[i][1], 1, 0u);
        audio_uart_page_4412ec(g2_onboarding_tile_list[i][1], audio_uart_page_44104c(0xffffffu), 0u);
        audio_uart_page_44146a(g2_onboarding_tile_list[i][1], 6, 0u);
        audio_uart_page_44130c(g2_onboarding_tile_list[i][1], 0xffu, 0u);
        ui_onboarding_main_sub_004A856C(g2_onboarding_tile_list[i][1], 0, 0u);
        audio_uart_page_43dfa4(g2_onboarding_tile_list[i][1], LV_OBJ_FLAG_CLICKABLE);
    }
    (void)onboarding_news_page_show_50a47e(0u);
    ui_onboarding_stock_sub_0050DCBC(1u);

    /* Feature page container (news / stock), hidden until a tile is opened. */
    g2_onboarding_feature_page_open = 0;
    g2_onboarding_main_obj_20074ce8 = lv_tileview_create_50fef8(g2_onboarding_root_obj);
    audio_uart_page_44127e(g2_onboarding_main_obj_20074ce8, audio_uart_page_44104c(0x000000u), 0u);
    audio_uart_page_43f4c0(g2_onboarding_main_obj_20074ce8, ONB_TILE_WIDTH, ONB_PAGE_HEIGHT);
    audio_uart_page_44146a(g2_onboarding_main_obj_20074ce8, 6, 0u);
    ui_onboarding_main_sub_004A856C(g2_onboarding_main_obj_20074ce8, 0, 0u);
    audio_uart_page_43f6d6(g2_onboarding_main_obj_20074ce8, g2_onboarding_root_obj, ONB_ALIGN_TOP_RIGHT, 0, 0);
    (void)audio_uart_page_44e368(g2_onboarding_main_obj_20074ce8, 0u);
    audio_uart_page_4412ec(g2_onboarding_main_obj_20074ce8, audio_uart_page_44104c(0xffffffu), 0u);
    audio_uart_page_44131c(g2_onboarding_main_obj_20074ce8, 1, 0u);
    audio_uart_page_43ded4(g2_onboarding_main_obj_20074ce8, LV_OBJ_FLAG_HIDDEN);
}

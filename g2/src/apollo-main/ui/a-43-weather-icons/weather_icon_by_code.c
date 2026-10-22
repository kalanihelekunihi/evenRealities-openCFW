/* Weather-code -> 24x24 icon lookup used by the dashboard watchface slots
 * (0x5b84dc, 0x5b8d3a) and the onboarding weather row (0x4a9452).
 * Native 0x50f810..0x50f889; literal pool 0x50f88c..0x50f8cb.
 * Stock source path unknown (no log strings); the function is its own unit
 * between the LVGL lv_roller.c code and app\gui\onboarding\onboarding_animation.c.
 *
 * Every target is an LVGL 9.3 lv_image_dsc_t in ROM: magic 0x19, colour format
 * 6 (L8), 24x24, stride 24, 576 data bytes. The descriptors are laid out in
 * string order of their names (1, 10..16, 2..9), i.e. the asset generator
 * named them by weather code. Codes 0, 1 and anything above 16 give icon 1. */
#include <stdint.h>

/* lv_image_dsc_t (LVGL 9.3). */
typedef struct {
    uint32_t header_word0; /* +0x00 magic [7:0], cf [15:8], flags [31:16] */
    uint32_t header_size;  /* +0x04 w [15:0], h [31:16] */
    uint32_t header_stride; /* +0x08 stride [15:0] */
    uint32_t data_size;    /* +0x0c */
    const uint8_t *data;   /* +0x10 */
    const void *reserved;  /* +0x14 */
    const void *reserved_2; /* +0x18 */
} g2_lv_image_dsc_t;
_Static_assert(sizeof(g2_lv_image_dsc_t) == 0x1c, "lv_image_dsc_t is 28 bytes");

extern const g2_lv_image_dsc_t g2_weather_icon_1;  /* ROM 0x77481c */
extern const g2_lv_image_dsc_t g2_weather_icon_10; /* ROM 0x774838 */
extern const g2_lv_image_dsc_t g2_weather_icon_11; /* ROM 0x774854 */
extern const g2_lv_image_dsc_t g2_weather_icon_12; /* ROM 0x774870 */
extern const g2_lv_image_dsc_t g2_weather_icon_13; /* ROM 0x77488c */
extern const g2_lv_image_dsc_t g2_weather_icon_14; /* ROM 0x7748a8 */
extern const g2_lv_image_dsc_t g2_weather_icon_15; /* ROM 0x7748c4 */
extern const g2_lv_image_dsc_t g2_weather_icon_16; /* ROM 0x7748e0 */
extern const g2_lv_image_dsc_t g2_weather_icon_2;  /* ROM 0x7748fc */
extern const g2_lv_image_dsc_t g2_weather_icon_3;  /* ROM 0x774918 */
extern const g2_lv_image_dsc_t g2_weather_icon_4;  /* ROM 0x774934 */
extern const g2_lv_image_dsc_t g2_weather_icon_5;  /* ROM 0x774950 */
extern const g2_lv_image_dsc_t g2_weather_icon_6;  /* ROM 0x77496c */
extern const g2_lv_image_dsc_t g2_weather_icon_7;  /* ROM 0x774988 */
extern const g2_lv_image_dsc_t g2_weather_icon_8;  /* ROM 0x7749a4 */
extern const g2_lv_image_dsc_t g2_weather_icon_9;  /* ROM 0x7749c0 */

const void *dashboard_icon_src_by_code_50f810(uint32_t code)
{
    switch (code) {
    case 1u:  return &g2_weather_icon_1;
    case 2u:  return &g2_weather_icon_2;
    case 3u:  return &g2_weather_icon_3;
    case 4u:  return &g2_weather_icon_4;
    case 5u:  return &g2_weather_icon_5;
    case 6u:  return &g2_weather_icon_6;
    case 7u:  return &g2_weather_icon_7;
    case 8u:  return &g2_weather_icon_8;
    case 9u:  return &g2_weather_icon_9;
    case 10u: return &g2_weather_icon_10;
    case 11u: return &g2_weather_icon_11;
    case 12u: return &g2_weather_icon_12;
    case 13u: return &g2_weather_icon_13;
    case 14u: return &g2_weather_icon_14;
    case 15u: return &g2_weather_icon_15;
    case 16u: return &g2_weather_icon_16;
    default:  return &g2_weather_icon_1;
    }
}

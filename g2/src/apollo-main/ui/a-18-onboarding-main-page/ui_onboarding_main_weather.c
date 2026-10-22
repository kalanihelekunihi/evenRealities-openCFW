/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c
 * Native 0x4A93B0..0x4A95E5 with its local constant pool 0x4A96C0..0x4A96DB
 * ("--", "%s", 1.8, 32.0, "%d"). Split from ui_onboarding_main_page.c only
 * because it needs the double-precision FPU (vcvt.f64.f32 / vmla.f64):
 * build with profile g2-apollo-main-20.
 *
 * Status bar of the onboarding main page: record type 1 carries a 0x38-byte
 * weather snapshot from the phone; the temperature is shown in Celsius
 * ("%.0f*") or Fahrenheit ("%.0f#", c * 1.8 + 32; '*' and '#' are degree
 * glyphs in the page font), next to the weather icon, and the battery label
 * and 24x24 battery icon are refreshed from the battery service. */
#include <stdint.h>
#include <stddef.h>

/* Weather snapshot (scratch copy RAM 0x20120308, kept copy RAM 0x200f47c8). */
typedef struct {
    uint32_t head[2];       /* +0x00 copied as one 8-byte block */
    uint16_t field_08;      /* +0x08 */
    uint16_t list_count;    /* +0x0a clamped to 6 */
    uint16_t list[6];       /* +0x0c */
    uint16_t byte_count;    /* +0x18 clamped to 6 */
    uint8_t bytes[6];       /* +0x1a */
    uint8_t temp_valid;     /* +0x20 0 shows "--" */
    uint8_t reserved_21[3];
    float temperature_c;    /* +0x24 */
    uint16_t unit;          /* +0x28 1 Celsius, otherwise Fahrenheit */
    uint16_t icon_code;     /* +0x2a dashboard weather icon code */
    uint8_t tail[0x0c];     /* +0x2c */
} g2_onboarding_weather_t;
_Static_assert(sizeof(g2_onboarding_weather_t) == 0x38u, "stock weather record");

typedef struct {
    uint32_t header[3];
    uint32_t data_size;
    const void *data;
    const void *reserved[2];
} g2_lv_image_dsc_t;
_Static_assert(sizeof(g2_lv_image_dsc_t) == 0x1cu, "LVGL 9 image descriptor");

extern g2_onboarding_weather_t g2_onboarding_weather_rx;   /* RAM 0x20120308 */
extern g2_onboarding_weather_t g2_onboarding_weather;      /* RAM 0x200f47c8 */
extern void *g2_onboarding_mutex;                          /* RAM 0x20074830, osMutexId_t */
extern void *g2_onboarding_main_obj_20074d18;              /* RAM 0x20074d18 weather icon */
extern void *g2_onboarding_main_obj_20074d1c;              /* RAM 0x20074d1c temperature label */
extern void *g2_onboarding_main_obj_20074d20;              /* RAM 0x20074d20 */
extern void *g2_onboarding_main_obj_20074d24;              /* RAM 0x20074d24 battery label */
extern void *g2_onboarding_main_obj_20074d28;              /* RAM 0x20074d28 battery icon */
/* 24x24 L8 battery icons, ROM 0x769db4 + n * 0x1c. */
extern const g2_lv_image_dsc_t g2_onboarding_battery_img_769db4; /* < 11 % */
extern const g2_lv_image_dsc_t g2_onboarding_battery_img_769dd0; /* 11..30 % */
extern const g2_lv_image_dsc_t g2_onboarding_battery_img_769dec; /* 31..50 % */
extern const g2_lv_image_dsc_t g2_onboarding_battery_img_769e08; /* 51..80 % */
extern const g2_lv_image_dsc_t g2_onboarding_battery_img_769e24; /* > 80 % */

extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* memset 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void *aeabi_memcpy4_439c04(void *dst, const void *src, uint32_t len);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern int32_t audio_ble_format_to_buffer(char *dst, const char *format, ...); /* sprintf 0x4b4728 */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                   /* 0x44981c */
extern const void *dashboard_icon_src_by_code_50f810(uint32_t code);
extern void audio_uart_page_498680(void *image, const void *src);   /* lv_image_set_src */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern void audio_uart_page_43f6d6(void *obj, void *base, uint32_t align, int32_t x,
                                   int32_t y);                      /* lv_obj_align_to */
extern int32_t ui_common_api_fn_00509f86(void);  /* battery percent for the label */
extern uint8_t ui_common_api_fn_00509f8e(void);  /* battery percent for the icon */

void ui_onboarding_main_sub_004A93B0(const uint8_t *data, uint32_t len);

static const char no_value[] = "--";          /* ROM 0x4a96c0 */
static const char fmt_string[] = "%s";        /* ROM 0x4a96c4 */
static const char fmt_celsius[] = "%.0f*";    /* ROM 0x78ed3c */
static const char fmt_fahrenheit[] = "%.0f#"; /* ROM 0x78ed44 */
static const char fmt_percent[] = "%d";       /* ROM 0x4a96d8 */

#define ONB_ALIGN_OUT_BOTTOM_RIGHT 15u
#define ONB_ALIGN_OUT_LEFT_MID     17u
#define ONB_ALIGN_OUT_RIGHT_MID    20u

void ui_onboarding_main_sub_004A93B0(const uint8_t *data, uint32_t len)
{
    char temp_text[12];
    char battery_text[12];
    const void *icon;
    uint8_t level;

    if (len != 0u) {
        g2_onboarding_weather_t *rx = &g2_onboarding_weather_rx;
        g2_onboarding_weather_t *dst = &g2_onboarding_weather;
        audio_uart_buffer_zero(rx, sizeof *rx, 0u);
        (void)audio_queue_copy_bytes(rx, data, sizeof *rx);
        dst->head[0] = rx->head[0];
        dst->head[1] = rx->head[1];
        dst->field_08 = rx->field_08;
        dst->list_count = rx->list_count;
        if (dst->list_count > 6u)
            dst->list_count = 6u;
        for (int32_t i = 0; i < (int32_t)dst->list_count; i++)
            dst->list[i] = rx->list[i];
        dst->byte_count = rx->byte_count;
        if (dst->byte_count > 6u)
            dst->byte_count = 6u;
        for (int32_t i = 0; i < (int32_t)dst->byte_count; i++)
            dst->bytes[i] = rx->bytes[i];
        (void)aeabi_memcpy4_439c04(&dst->temp_valid, &rx->temp_valid, 0x18u);
    }

    (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
    icon = dashboard_icon_src_by_code_50f810(g2_onboarding_weather.icon_code);
    (void)osMutexRelease(g2_onboarding_mutex);
    if (icon != NULL)
        audio_uart_page_498680(g2_onboarding_main_obj_20074d18, icon);

    audio_uart_buffer_zero(temp_text, 10u, 0u);
    (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
    if (g2_onboarding_weather.temp_valid == 0u)
        (void)g2_audio_dump_snprintf(temp_text, 10u, fmt_string, no_value);
    else if (g2_onboarding_weather.unit == 1u)
        (void)audio_ble_format_to_buffer(temp_text, fmt_celsius,
                                         (double)g2_onboarding_weather.temperature_c);
    else
        (void)audio_ble_format_to_buffer(temp_text, fmt_fahrenheit,
                                         (double)g2_onboarding_weather.temperature_c * 1.8 + 32.0);
    (void)osMutexRelease(g2_onboarding_mutex);
    if (g2_onboarding_main_obj_20074d1c != NULL) {
        (void)audio_uart_page_49942e(g2_onboarding_main_obj_20074d1c, temp_text);
        audio_uart_page_43f6d6(g2_onboarding_main_obj_20074d1c, g2_onboarding_main_obj_20074d18,
                               ONB_ALIGN_OUT_RIGHT_MID, 8, 0);
    }

    audio_uart_buffer_zero(battery_text, 10u, 0u);
    (void)g2_audio_dump_snprintf(battery_text, 10u, fmt_percent, ui_common_api_fn_00509f86());
    if (g2_onboarding_main_obj_20074d24 != NULL) {
        (void)audio_uart_page_49942e(g2_onboarding_main_obj_20074d24, battery_text);
        audio_uart_page_43f6d6(g2_onboarding_main_obj_20074d24, g2_onboarding_main_obj_20074d28,
                               ONB_ALIGN_OUT_BOTTOM_RIGHT, 0, 234);
        if (g2_onboarding_main_obj_20074d20 != NULL)
            audio_uart_page_43f6d6(g2_onboarding_main_obj_20074d20, g2_onboarding_main_obj_20074d24,
                                   ONB_ALIGN_OUT_LEFT_MID, -8, 0);
    }

    level = ui_common_api_fn_00509f8e();
    if (level < 11u)
        audio_uart_page_498680(g2_onboarding_main_obj_20074d28, &g2_onboarding_battery_img_769db4);
    else if ((uint32_t)(level - 11u) < 20u)
        audio_uart_page_498680(g2_onboarding_main_obj_20074d28, &g2_onboarding_battery_img_769dd0);
    else if ((uint32_t)(level - 31u) < 20u)
        audio_uart_page_498680(g2_onboarding_main_obj_20074d28, &g2_onboarding_battery_img_769dec);
    else if ((uint32_t)(level - 51u) < 30u)
        audio_uart_page_498680(g2_onboarding_main_obj_20074d28, &g2_onboarding_battery_img_769e08);
    else if (level >= 81u)
        audio_uart_page_498680(g2_onboarding_main_obj_20074d28, &g2_onboarding_battery_img_769e24);
}

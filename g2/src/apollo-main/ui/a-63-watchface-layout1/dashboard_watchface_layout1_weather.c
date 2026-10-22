/* Dashboard watchface layout1 weather complication, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_watchface_layout1.c.
 * Native 0x5b84ac..0x5b8561 and 0x5b856c..0x5b8589 (double constants 1.8 and
 * 32.0 at 0x5b87dc / 0x5b87e4, "-" at 0x5b87d8, "%d\u2103" 0x78d32c,
 * "%d\u2109" 0x78d334).
 *
 * 0x5b856c is ops slot +0x14 of the layout1 ops table (ROM 0x713f54) and takes
 * the temperature in s0; the Fahrenheit conversion is done in double
 * precision (vmla.f64): profile g2-apollo-main-20. */
#include <stdint.h>
#include <stddef.h>
#include "dashboard_watchface_layout1.h"

#define VFP __attribute__((pcs("aapcs-vfp")))

/* Stock rounds the product before the add (vmla.f64, not vfma). */
#pragma STDC FP_CONTRACT OFF

/* Argument block built on the stack by 0x5b856c. */
typedef struct {
    uint16_t icon_code;   /* +0x0 dashboard weather icon code */
    uint8_t pad[2];
    float temperature_c;  /* +0x4 */
    uint32_t valid;       /* +0x8 0 = no data, show "-" */
    uint32_t celsius;     /* +0xc 1 = Celsius, else Fahrenheit */
} g2_wf_weather_t;
_Static_assert(sizeof(g2_wf_weather_t) == 16u, "weather argument block");

extern uint32_t audio_terminal_ui_object_valid_43e2ea(void *object);  /* lv_obj_is_valid */
extern const void *dashboard_icon_src_by_code_50f810(uint32_t code);
extern void audio_uart_page_498680(void *object, const void *source); /* lv_image_set_src */
extern const char *audio_uart_page_49942e(void *label, const char *text); /* lv_label_set_text */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */

static const char no_value[] = "-";                 /* ROM 0x5b87d8 */
static const char celsius_fmt[] = "%d\xe2\x84\x83";  /* ROM 0x78d32c "%d" U+2103 */
static const char fahrenheit_fmt[] = "%d\xe2\x84\x89"; /* ROM 0x78d334 "%d" U+2109 */

void layout1_slot_weather_refresh_5b84ac(g2_wf_slot_t *slot, const void *arg)
{
    const g2_wf_weather_t *const weather = arg;
    char text[16];

    if (slot == NULL || slot->icon == NULL || slot->label == NULL)
        return;
    if (audio_terminal_ui_object_valid_43e2ea(slot->icon) == 0u ||
        audio_terminal_ui_object_valid_43e2ea(slot->label) == 0u)
        return;
    const void *const icon = dashboard_icon_src_by_code_50f810(weather->icon_code);
    if (icon != NULL)
        audio_uart_page_498680(slot->icon, icon);
    aeabi_memset_43c0e4(text, sizeof(text), 0);
    if (weather->valid == 0u)
        g2_audio_dump_snprintf(text, sizeof(text), no_value);
    else if (weather->celsius == 1u)
        g2_audio_dump_snprintf(text, sizeof(text), celsius_fmt, (int32_t)weather->temperature_c);
    else
        g2_audio_dump_snprintf(text, sizeof(text), fahrenheit_fmt,
                               (int32_t)(32.0 + (double)weather->temperature_c * 1.8));
    audio_uart_page_49942e(slot->label, text);
    layout1_slot_layout_5b7a4c(slot);
}

/* ops +0x14 */
VFP void layout1_update_weather_5b856c(uint16_t icon_code, uint32_t valid, uint32_t celsius,
                                       float temperature_c)
{
    const g2_wf_weather_t weather = {
        .icon_code = icon_code, .temperature_c = temperature_c, .valid = valid, .celsius = celsius,
    };

    layout1_slots_for_kind_5b845c(1u, layout1_slot_weather_refresh_5b84ac, &weather);
}

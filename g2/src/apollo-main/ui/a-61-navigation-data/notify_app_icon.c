/* Notification app identifier -> icon / display name lookups.
 * Native 0x588514..0x5885b3 with literal pool 0x58858c..0x588597; the stock
 * source file is not named by any string (the rows sit between
 * navigation_data_handler.c and pb_service_teleprompt.c, the TSV names are
 * placeholders). Callers: the message notification list
 * (ui/a-52-msg-notif-list) and other notification UIs.
 *
 * The table (ROM 0x687b60) holds 89 {bundle id, lv_image_dsc_t *, name}
 * records ("com.apple.MobileSMS" -> Messages ... "com.google.android.youtube"
 * -> YouTube) followed by a default record {NULL, ROM 0x769804,
 * "Unknown App"}. A NULL identifier returns the default without scanning. */
#include <stdint.h>
#include <stddef.h>

#define NOTIFY_APP_ICON_COUNT 89u

typedef struct {
    const char *app_identifier; /* +0x0 */
    const void *icon;           /* +0x4 lv_image_dsc_t */
    const char *name;           /* +0x8 */
} g2_notify_app_icon_t;
_Static_assert(sizeof(g2_notify_app_icon_t) == 12u, "stock record is 12 bytes");

extern const g2_notify_app_icon_t g2_notify_app_icon_table_687b60[NOTIFY_APP_ICON_COUNT + 1u]; /* ROM 0x687b60 */
extern const uint8_t g2_notify_app_icon_default_769804[]; /* ROM 0x769804 lv_image_dsc_t */

extern int32_t audio_uart_font_path_compare(const char *a, const char *b); /* strcmp 0x46cacc */
extern void audio_uart_page_498680(void *image, const void *src);         /* lv_image_set_src */

static const char unknown_app[] = "Unknown App"; /* ROM 0x78a298 */

const void *navigation_record_second_field_lookup(const char *app_identifier)
{
    if (app_identifier == NULL)
        return g2_notify_app_icon_default_769804;
    for (uint32_t i = 0u; i < NOTIFY_APP_ICON_COUNT; i++) {
        if (audio_uart_font_path_compare(g2_notify_app_icon_table_687b60[i].app_identifier,
                                         app_identifier) == 0)
            return g2_notify_app_icon_table_687b60[i].icon;
    }
    return g2_notify_app_icon_table_687b60[NOTIFY_APP_ICON_COUNT].icon;
}

const char *navigation_record_third_field_lookup(const char *app_identifier)
{
    if (app_identifier == NULL)
        return unknown_app;
    for (uint32_t i = 0u; i < NOTIFY_APP_ICON_COUNT; i++) {
        if (audio_uart_font_path_compare(g2_notify_app_icon_table_687b60[i].app_identifier,
                                         app_identifier) == 0)
            return g2_notify_app_icon_table_687b60[i].name;
    }
    return g2_notify_app_icon_table_687b60[NOTIFY_APP_ICON_COUNT].name;
}

void navigation_apply_named_resource(void *image, const char *app_identifier)
{
    const void *icon;

    if (image == NULL)
        return;
    icon = navigation_record_second_field_lookup(app_identifier);
    if (icon != NULL)
        audio_uart_page_498680(image, icon);
}

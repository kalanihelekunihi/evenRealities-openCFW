/* Product FreeRTOS-Plus-CLI UI commands "alert" and "dashboard_layout",
 * stock directory D:\01_workspace\s200_ap510b_iar_git\kernel\
 * FreeRTOS-Plus-CLI\prvCommand\ (file name not retained). Native: alert
 * 0x58185c..0x581873, dashboard_layout 0x581874..0x58195f, pool
 * 0x581970..0x581983. The registrar 0x581960 is in
 * a-59-cli-commands/prvCommand_registrars.c. */
#include <stddef.h>
#include <stdint.h>
#include "../a-59-cli-commands/cli_commands.h"

#define DASHBOARD_LAYOUT_BYTES 128u
#define DASHBOARD_WIDGETS_MAX 5

/* Layout image handed to audio_dashboard_layout_set (128 bytes). */
typedef struct {
    uint8_t base_pos;                    /* +0x0 */
    uint8_t widget_count;                /* +0x1 0..5 */
    uint8_t widgets[DASHBOARD_LAYOUT_BYTES - 2u]; /* +0x2 */
} g2_dashboard_layout_cli_t;
_Static_assert(sizeof(g2_dashboard_layout_cli_t) == DASHBOARD_LAYOUT_BYTES, "dashboard layout");

extern int32_t atoi_48d868(const char *text);
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint32_t system_alert_ring_event_4d306c(uint8_t); /* 0x4d306c, alert 0x21, 10 s throttle */
extern void audio_dashboard_layout_reset(void);           /* 0x558148 */
extern int32_t audio_dashboard_layout_set(const void *);  /* 0x558376 */

static const char s_reset[] = "dashboard layout reset to default\r\n"; /* ROM 0x7585bc */
static const char s_usage[] =
    "usage: dashboard_layout <base_pos> <widget_count> [w0..w4]\r\n"; /* ROM 0x70dfe4 */
static const char s_missing[] = "missing widget[%d] parameter\r\n"; /* ROM 0x763e70 */
static const char s_set_ok[] =
    "dashboard layout set OK: base_pos=%d widget_count=%d (next dashboard entry)\r\n"; /* ROM 0x6ef2c8 */
static const char s_invalid[] = "dashboard layout invalid, fallback to default\r\n"; /* ROM 0x736f74 */

int32_t cli_cmd_alert_58185c(char *write_buffer, size_t write_buffer_len, const char *command_string);
int32_t cli_cmd_dashboard_layout_581874(char *write_buffer, size_t write_buffer_len,
                                        const char *command_string);

/* "alert <n>": raise system ring alert n. */
int32_t cli_cmd_alert_58185c(char *write_buffer, size_t write_buffer_len, const char *command_string)
{
    int32_t length;

    (void)write_buffer;
    (void)write_buffer_len;
    (void)system_alert_ring_event_4d306c(
        (uint8_t)atoi_48d868(freertos_cli_get_parameter_5848fc(command_string, 1u, &length)));
    return 0;
}

/* "dashboard_layout" alone resets to the default layout; otherwise the
 * widget count is clamped to 0..5 and that many widget ids must follow. */
int32_t cli_cmd_dashboard_layout_581874(char *write_buffer, size_t write_buffer_len,
                                        const char *command_string)
{
    int32_t length = 0;
    g2_dashboard_layout_cli_t layout;
    const char *text;
    int32_t base_pos;
    int32_t count;
    int32_t i;

    text = freertos_cli_get_parameter_5848fc(command_string, 1u, &length);
    if (text == NULL) {
        audio_dashboard_layout_reset();
        (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_reset);
        return 0;
    }
    base_pos = atoi_48d868(text);
    text = freertos_cli_get_parameter_5848fc(command_string, 2u, &length);
    if (text == NULL) {
        (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_usage);
        return 0;
    }
    count = atoi_48d868(text);
    if (count < 0)
        count = 0;
    if (count > DASHBOARD_WIDGETS_MAX)
        count = DASHBOARD_WIDGETS_MAX;
    (void)aeabi_memset_43c0e4(&layout, sizeof(layout), 0);
    layout.base_pos = (uint8_t)base_pos;
    layout.widget_count = (uint8_t)count;
    for (i = 0; i < count; i++) {
        text = freertos_cli_get_parameter_5848fc(command_string, (uint32_t)i + 3u, &length);
        if (text == NULL) {
            (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_missing, i);
            return 0;
        }
        layout.widgets[i] = (uint8_t)atoi_48d868(text);
    }
    if (audio_dashboard_layout_set(&layout) == 0)
        (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_set_ok, base_pos, count);
    else
        (void)g2_audio_dump_snprintf(write_buffer, (uint32_t)write_buffer_len, s_invalid);
    return 0;
}

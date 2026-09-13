/* SPDX-License-Identifier: MIT */
#include <stdint.h>
struct notification_state { uint8_t prefix[52]; uint16_t vad_reporting; };
extern struct notification_state open_cfw_gx8002_notification_state;
extern int open_cfw_gx8002_printf(const char *, ...);
extern void open_cfw_gx8002_notification_stamp(void);
extern int open_cfw_gx8002_app_reply(uint32_t, uint32_t, uint32_t);
static const char diagnostic[] = "notify vad status\n";
int open_cfw_gx8002_vad_notify(uint32_t status)
{
    if (open_cfw_gx8002_notification_state.vad_reporting) {
        open_cfw_gx8002_printf(diagnostic);
        open_cfw_gx8002_notification_stamp();
        open_cfw_gx8002_app_reply(1, 13, status);
    }
    return 0;
}

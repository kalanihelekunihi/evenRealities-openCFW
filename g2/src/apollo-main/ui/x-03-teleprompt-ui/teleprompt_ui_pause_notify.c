/* Teleprompt pause/resume notify, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\teleprompt\teleprompt_ui.c
 * (module tag "teleprompt.ui" ROM 0x7897d0). Native 0x554102..0x55416f;
 * literal pools 0x554b20..0x554b2b and 0x554d38..0x554d43 shared with
 * ui/a-53-teleprompt-ui.
 *
 * Only the master (right) glasses tell the app: the 2-byte status record
 * (template ROM 0x78f6c0 = {0, 0}) gets the command in byte 0 (2 pause,
 * 3 resume from the teleprompt input handler) and is sent with
 * APP_PbTxEncodeStatusNotify (pb_service_teleprompt). */
#include <stdint.h>

#define DEVICE_ROLE_MASTER 1u

extern const uint16_t g2_teleprompt_status_notify_init_78f6c0; /* ROM 0x78f6c0 */

extern uint8_t audio_uart_device_role_get(void);                    /* 0x45a568, 1 = master */
extern uint32_t APP_PbTxEncodeStatusNotify(const uint16_t *status); /* 0x58887a */
extern uint32_t audio_log_flags(void);                              /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                  /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

void teleprompt_ui_pause_notify_send_554102(uint8_t cmd);

static const char module_tag[] = "teleprompt.ui"; /* ROM 0x7897d0 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\teleprompt\\teleprompt_ui.c"; /* ROM 0x6fd97c */
static const char fn_pause_notify[] = "teleprompt_ui_pause_notify_send"; /* ROM 0x766070 */
static const char notify_text[] = "notify app pause/resume: cmd=%d";   /* ROM 0x766090 */
static const char notify_short[] = "[teleprompt.ui]notify app pause/resume: cmd=%d"; /* ROM 0x739434 */

void teleprompt_ui_pause_notify_send_554102(uint8_t cmd)
{
    union {
        uint16_t word;
        uint8_t bytes[2];
    } status;

    if (audio_uart_device_role_get() != DEVICE_ROLE_MASTER)
        return;
    status.word = g2_teleprompt_status_notify_init_78f6c0;
    status.bytes[0] = cmd;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module_tag, source_file, fn_pause_notify, 235u, notify_text,
                           (uint32_t)cmd);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0c400000u, notify_short, notify_short, (uint32_t)cmd);
    (void)APP_PbTxEncodeStatusNotify(&status.word);
}

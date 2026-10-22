/* System monitor common-data handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\system\system_monitor.c.
 * Native 0x584ee4..0x5850e1; literal pool 0x5850e4..0x58511f.
 *
 * Stock name system_monitor_common_data_handler (log strings). It is reached
 * only through UI registry row 28 (ROM 0x6a4670), whose table in
 * system/ui-registry declares it as audio_uart_registry_callback_584ee4; that
 * name is kept so the table links. The registry passes (event type, payload,
 * length); the function returns nothing useful in r0.
 *
 * Event type 5 with the 6-byte payload 55 04 12 34 56 78 is the peer reboot
 * notice. The handler then stops any running display / foreground /
 * background app, waits up to 11 x 100 ms for the page manager to go idle,
 * sends the schedule-manager idle command when this side is the master, and
 * resets dashboard, Even AI, onboarding colour, terminal and ring-sync state. */
#include <stdint.h>
#include <stddef.h>

#define SYSMON_EVENT_PEER_REBOOT 5u
#define SYSMON_IDLE_WAIT_POLLS   11
#define SYSMON_IDLE_WAIT_MS      100u
#define DEVICE_ROLE_MASTER       1u

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

extern uint32_t ui_page_manager_ready_443484(void);            /* 1 while the display/page manager is running */
extern uint32_t display_background_app_running_44349c(void);   /* logged by stock as "foreground app is running" */
extern uint32_t display_foreground_app_running_4434b4(void);   /* logged by stock as "background app is running" */
extern int32_t audio_uart_slave_display_stop(uint32_t id, const void *payload, uint32_t bytes); /* 0x4443cc */
extern void audio_uart_task_delay(uint32_t ms);                /* 0x454b4c */
extern uint32_t display_driver_uled_mode_45a568(void);         /* device role, 1 = master */
extern int32_t audio_uart_display_quiesce(void);               /* 0x465b10 SendIdleCommandtoScheduleManager */
extern void dashboard_data_reset_49c0b0(void);
extern void audio_even_ai_sync_remote_4973f4(uint32_t notify);
extern void onboarding_saved_color_state_reset(void);          /* 0x46800c */
extern void audio_td_state_reset(void);                        /* 0x5970f0 td_state_reset */
extern void audio_uart_service_prepare6(void);                 /* 0x47d818 RPC_SyncRingStatusWithPeer */

void audio_uart_registry_callback_584ee4(uint32_t event_type, const uint8_t *data, uint32_t len);

static const char module_tag[] = "system_monitor"; /* ROM 0x789650 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\system\\system_monitor.c"; /* ROM 0x706590 */
static const char handler_fn[] = "system_monitor_common_data_handler"; /* ROM 0x75a950 */
static const char event_fmt[] = "system_monitor_common_data_handler: eventType = %d, len = %d"; /* ROM 0x70fa24 */
static const char event_fmt_short[] = "[system_monitor]system_monitor_common_data_handler: eventType = %d, len = %d"; /* ROM 0x6efea8 */
static const char reboot_msg[] = "system_monitor_common_data_handler: peer reboot"; /* ROM 0x738f24 */
static const char reboot_msg_short[] = "[system_monitor]system_monitor_common_data_handler: peer reboot"; /* ROM 0x70fa64 */
static const char display_msg[] = "system_monitor_common_data_handler: display is running"; /* ROM 0x723b28 */
static const char display_msg_short[] = "[system_monitor]system_monitor_common_data_handler: display is running"; /* ROM 0x6fd814 */
static const char fg_msg[] = "system_monitor_common_data_handler: foreground app is running"; /* ROM 0x70faa4 */
static const char fg_msg_short[] = "[system_monitor]system_monitor_common_data_handler: foreground app is running"; /* ROM 0x6efef8 */
static const char bg_msg[] = "system_monitor_common_data_handler: background app is running"; /* ROM 0x70fae4 */
static const char bg_msg_short[] = "[system_monitor]system_monitor_common_data_handler: background app is running"; /* ROM 0x6eff48 */
static const char idle_msg[] = "system_monitor_common_data_handler: master role, send idle command to schedule manager"; /* ROM 0x6e5458 */
static const char idle_msg_short[] = "[system_monitor]system_monitor_common_data_handler: master role, send idle command to schedule manager"; /* ROM 0x6d9aac */

static const uint8_t peer_reboot_magic[6] = {0x55u, 0x04u, 0x12u, 0x34u, 0x56u, 0x78u};

static void log_line(uint8_t level, uint32_t line, uint32_t code, const char *msg, const char *msg_short)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module_tag, source_file, handler_fn, line, msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(code, msg_short, msg_short);
}

void audio_uart_registry_callback_584ee4(uint32_t event_type, const uint8_t *data, uint32_t len)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, handler_fn, 0x30u, event_fmt, event_type, len);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c800000u, event_fmt_short, event_fmt_short, event_type, len);

    if (event_type != SYSMON_EVENT_PEER_REBOOT)
        return;
    /* Byte-wise compare, stock exits at the first mismatch. */
    for (uint32_t i = 0; i < sizeof peer_reboot_magic; i++) {
        if (data[i] != peer_reboot_magic[i])
            return;
    }

    log_line(4u, 0x34u, 0x10000000u, reboot_msg, reboot_msg_short);
    if (ui_page_manager_ready_443484() == 1u) {
        log_line(4u, 0x36u, 0x10000000u, display_msg, display_msg_short);
        if (display_background_app_running_44349c() == 1u) {
            log_line(4u, 0x38u, 0x10000000u, fg_msg, fg_msg_short);
            (void)audio_uart_slave_display_stop(0u, NULL, 0u);
        }
        if (display_foreground_app_running_4434b4() == 1u) {
            log_line(3u, 0x3du, 0x0c000000u, bg_msg, bg_msg_short);
            (void)audio_uart_slave_display_stop(0u, NULL, 0u);
        }
    }

    for (int32_t polls = 0; polls < SYSMON_IDLE_WAIT_POLLS; polls++) {
        if (ui_page_manager_ready_443484() != 1u)
            break;
        audio_uart_task_delay(SYSMON_IDLE_WAIT_MS);
    }

    if (display_driver_uled_mode_45a568() == DEVICE_ROLE_MASTER) {
        log_line(3u, 0x4cu, 0x0c000000u, idle_msg, idle_msg_short);
        (void)audio_uart_display_quiesce();
    }
    dashboard_data_reset_49c0b0();
    audio_even_ai_sync_remote_4973f4(0u);
    onboarding_saved_color_state_reset();
    audio_td_state_reset();
    audio_uart_service_prepare6();
}

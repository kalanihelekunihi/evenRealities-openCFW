/* System-alert page event handler and ring-event sender, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\SystemAlert\systemAlert.c.
 * Native 0x4d2c42..0x4d2f47 (system_alert_page_event_handler) and
 * 0x4d306c..0x4d30b9; literal pool 0x4d3424..0x4d3483.
 *
 * Application id 0x21 is the system-alert page. RequestDisplayStop (0x464c36)
 * closes it, RequestDisplayReflash (0x45aaca) posts an auto-exit event to it,
 * and SendDataToBoth (0x464d1c) forwards an event byte to the peer side. */
#include <stdint.h>

#define SYSTEM_ALERT_APP_ID 0x21u
#define SYSTEM_ALERT_PAGE_ID 0xb4u
#define DEVICE_ROLE_MASTER 1u
#define DEVICE_ROLE_SLAVE 2u

/* Page events delivered to the handler (third argument). */
enum {
    PAGE_EVT_LV_CLICKED = 10,          /* LV_EVENT_CLICKED */
    PAGE_EVT_IMU_REFLASH = 0x40,
    PAGE_EVT_SCROLLUP = 0x44,
    PAGE_EVT_SCROLLDOWN = 0x45,
    PAGE_EVT_EXIT = 0x48,
    PAGE_EVT_FOREGROUND_ENTER_ANIM_COMPLETE = 0x4d,
    PAGE_EVT_FOREGROUND_EXIT_ANIM_COMPLETE = 0x4e,
};

#define AUTO_EXIT_EVENT 5u
#define AUTO_EXIT_DELAY_MS 3000u
#define RING_EVENT_THROTTLE_MS 10000u

extern uint8_t audio_system_alert_active_20075025;   /* RAM 0x20075025 */
extern uint32_t audio_system_alert_page_id_20003bcc; /* RAM 0x20003bcc */
extern uint32_t g2_system_alert_ring_event_tick;     /* RAM 0x200749f8, last send tick */

extern uint32_t audio_log_flags(void);                                       /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *path,
                               const char *function, uint32_t line, const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *format, const char *compact, ...); /* 0x43ce9e */
extern uint8_t audio_uart_device_role_get(void);                             /* 0x45a568 */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);  /* 0x43c0e4 */
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload,
                                            uint32_t length, uint32_t context); /* RequestDisplayStop */
extern int32_t async_request_display_reflash_45aaca(uint32_t application, const void *payload,
                                                    uint32_t length, uint32_t delay);
extern int32_t audio_uart_input_event_send_464d1c(uint16_t type, const void *payload,
                                                  uint32_t length, uint32_t context); /* SendDataToBoth */
extern uint32_t osKernelGetTickCount(void);                                  /* 0x4490cc */

static const char module[] = "system_alert"; /* ROM 0x789660 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemAlert\\systemAlert.c"; /* ROM 0x6fd85c */
static const char function[] = "system_alert_page_event_handler"; /* ROM 0x7659d0 */
static const char clicked[] = "LV_EVENT_CLICKED";                  /* ROM 0x783cf8 */
static const char clicked_c[] = "[system_alert]LV_EVENT_CLICKED";   /* ROM 0x7659f0 */
static const char scrollup[] = "SCROLLUP_EVENT";                   /* ROM 0x789670 */
static const char scrollup_c[] = "[system_alert]SCROLLUP_EVENT";    /* ROM 0x765a10 */
static const char scrolldown[] = "SCROLLDOWN_EVENT";               /* ROM 0x783d0c */
static const char scrolldown_c[] = "[system_alert]SCROLLDOWN_EVENT"; /* ROM 0x765a30 */
static const char enter_done[] = "PAGE_EVENT_FOREGROUND_ENTER_ANIM_COMPLETE"; /* ROM 0x744304 */
static const char enter_done_c[] =
    "[system_alert]PAGE_EVENT_FOREGROUND_ENTER_ANIM_COMPLETE";      /* ROM 0x723b60 */
static const char auto_exit[] = "send system alert auto exit event to self"; /* ROM 0x744330 */
static const char auto_exit_c[] =
    "[system_alert]send system alert auto exit event to self";      /* ROM 0x723b98 */
static const char exit_done[] = "PAGE_EVENT_FOREGROUND_EXIT_ANIM_COMPLETE"; /* ROM 0x74435c */
static const char exit_done_c[] =
    "[system_alert]PAGE_EVENT_FOREGROUND_EXIT_ANIM_COMPLETE";       /* ROM 0x723bd0 */
static const char imu_reflash[] = "IMU Reflash Event.";            /* ROM 0x783d20 */
static const char imu_reflash_c[] = "[system_alert]IMU Reflash Event."; /* ROM 0x75a9bc */

static void log_event(uint8_t level, uint32_t line, uint32_t mask,
                      const char *plain, const char *compact)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, path, function, line, plain);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(mask, compact, compact);
}

/* Only the master closes the page; the slave (role 2) ignores the request. */
static void close_on_master(void)
{
    if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE)
        return;
    if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER) {
        audio_system_alert_active_20075025 = 0u;
        audio_system_alert_page_id_20003bcc = SYSTEM_ALERT_PAGE_ID;
        audio_system_alert_close_464c36(SYSTEM_ALERT_APP_ID, 0u, 0u, 0u);
    }
}

uint32_t system_alert_page_event_handler_4d2c42(uint32_t page, uint32_t object,
                                                uint32_t event, uint32_t param)
{
    uint8_t message[4];

    (void)page;
    (void)object;
    (void)param;
    if (event == PAGE_EVT_LV_CLICKED) {
        log_event(4u, 0x4au, 0x10000000u, clicked, clicked_c);
        close_on_master();
    } else if (event == PAGE_EVT_EXIT) {
        close_on_master();
    } else if (event == PAGE_EVT_SCROLLUP) {
        log_event(4u, 0x61u, 0x10000000u, scrollup, scrollup_c);
        close_on_master();
    } else if (event == PAGE_EVT_SCROLLDOWN) {
        log_event(4u, 0x6du, 0x10000000u, scrolldown, scrolldown_c);
        close_on_master();
    } else if (event == PAGE_EVT_FOREGROUND_ENTER_ANIM_COMPLETE) {
        log_event(3u, 0x79u, 0x0c000000u, enter_done, enter_done_c);
        audio_system_alert_active_20075025 = 1u;
        audio_system_alert_page_id_20003bcc = SYSTEM_ALERT_PAGE_ID;
        if (audio_uart_device_role_get() == DEVICE_ROLE_MASTER) {
            audio_uart_buffer_zero(message, 1u, 0u);
            message[0] = AUTO_EXIT_EVENT;
            (void)async_request_display_reflash_45aaca(SYSTEM_ALERT_APP_ID, message, 1u,
                                                       AUTO_EXIT_DELAY_MS);
            log_event(3u, 0x80u, 0x0c000000u, auto_exit, auto_exit_c);
        }
    } else if (event == PAGE_EVT_FOREGROUND_EXIT_ANIM_COMPLETE) {
        log_event(3u, 0x85u, 0x0c000000u, exit_done, exit_done_c);
    } else if (event == PAGE_EVT_IMU_REFLASH) {
        log_event(4u, 0x89u, 0x10000000u, imu_reflash, imu_reflash_c);
    }
    return 1u;
}

/* Sends one system-alert event byte to both sides, at most once per 10 s.
 * The window restarts only when the tick has advanced past the stored value
 * (a wrapped tick sends without updating it). Returns 0 when throttled. */
uint32_t system_alert_ring_event_4d306c(uint8_t value)
{
    uint8_t message[4];
    uint32_t now = osKernelGetTickCount();

    if (g2_system_alert_ring_event_tick == 0u) {
        g2_system_alert_ring_event_tick = now;
    } else if (g2_system_alert_ring_event_tick < now) {
        if (now - g2_system_alert_ring_event_tick < RING_EVENT_THROTTLE_MS)
            return 0u;
        g2_system_alert_ring_event_tick = now;
    }
    audio_uart_buffer_zero(message, 1u, 0u);
    message[0] = value;
    return (uint32_t)audio_uart_input_event_send_464d1c(SYSTEM_ALERT_APP_ID, message, 1u, 0u);
}

/* Stock D:\01_workspace\s200_ap510b_iar_git\app\gui\MessageNotify\msg_notif_timer.c
 * Native 0x5528b8..0x552adb; literal pool 0x552adc..0x552b2f.
 *
 * Auto-close timer for the message-notification list. Only the master eye
 * (device role 1) arms it; the page handler polls check_timeout and then calls
 * process_timeout, which closes the notification application (id 4) when it is
 * still the foreground application. */
#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t start_tick; /* +0x00 osKernelGetTickCount at start */
    uint32_t timeout_ms; /* +0x04 */
    uint8_t state;       /* +0x08 0 idle, 1 running, 2 expired */
    uint8_t reserved_09[3];
} g2_msg_notif_timer_t;
_Static_assert(sizeof(g2_msg_notif_timer_t) == 0x0c, "stock timer manager is 12 bytes");

enum { MSG_NOTIF_TIMER_IDLE = 0u, MSG_NOTIF_TIMER_RUNNING = 1u, MSG_NOTIF_TIMER_EXPIRED = 2u };
enum { DEVICE_ROLE_MASTER = 1u };
enum { MSG_NOTIF_APP_ID = 4u, MSG_NOTIF_DEFAULT_TIMEOUT_MS = 10000u };

extern g2_msg_notif_timer_t g2_msg_notif_timer_2007405c; /* RAM 0x2007405c */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern uint32_t osKernelGetTickCount(void);                     /* 0x4490cc */
extern uint32_t display_driver_uled_mode_45a568(void);          /* device role, 1 master */
extern uint8_t *audio_message_notify_ancc_state_get_49729c(void); /* service_ancc_state_get */
extern uint32_t ui_page_manager_ready_443484(void);             /* *flag == 1 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app_id); /* app is foreground */
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload,
                                            uint32_t length, uint32_t flags);

static const char module_tag[] = "message_notify.timer"; /* ROM 0x7797b4 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\MessageNotify\\msg_notif_timer.c"; /* ROM 0x6f4604 */

static const char fn_init[] = "msg_notif_timer_mgr_init"; /* ROM 0x76e184 */
static const char msg_init[] = "msg_notif_timer_mgr_init"; /* ROM 0x76e1a0 */
static const char msg_init_short[] = "[message_notify.timer]msg_notif_timer_mgr_init"; /* ROM 0x7357a4 */
static const char fn_deinit[] = "msg_notif_timer_mgr_deinit"; /* ROM 0x76e1bc */
static const char msg_deinit[] = "msg_notif_timer_mgr_deinit"; /* ROM 0x76e1d8 */
static const char msg_deinit_short[] = "[message_notify.timer]msg_notif_timer_mgr_deinit"; /* ROM 0x72ae54 */
static const char fn_start[] = "msg_notif_timer_mgr_start"; /* ROM 0x76e1f4 */
static const char msg_start[] = "msg_notif_timer_mgr_start: timeout_ms = %d"; /* ROM 0x740238 */
static const char msg_start_short[] = "[message_notify.timer]msg_notif_timer_mgr_start: timeout_ms = %d"; /* ROM 0x703c20 */
static const char fn_stop[] = "msg_notif_timer_mgr_stop"; /* ROM 0x76e210 */
static const char msg_stop[] = "msg_notif_timer_mgr_stop"; /* ROM 0x76e22c */
static const char msg_stop_short[] = "[message_notify.timer]msg_notif_timer_mgr_stop"; /* ROM 0x7357d4 */
static const char fn_check[] = "msg_notif_timer_mgr_check_timeout"; /* ROM 0x756b70 */
static const char msg_check[] = "msg_notif_timer_mgr_check_timeout: timeout occurred, elapsed_time = %d ms"; /* ROM 0x6f4650 */
static const char msg_check_short[] = "[message_notify.timer]msg_notif_timer_mgr_check_timeout: timeout occurred, elapsed_time = %d ms"; /* ROM 0x6ddd14 */
static const char fn_process[] = "msg_notif_timer_mgr_process_timeout"; /* ROM 0x756b94 */
static const char msg_process[] = "msg_notif_timer_mgr_process_timeout: processing timeout"; /* ROM 0x720440 */
static const char msg_process_short[] = "[message_notify.timer]msg_notif_timer_mgr_process_timeout: processing timeout"; /* ROM 0x6ee5a8 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

void msg_notif_timer_mgr_init_5528b8(void)
{
    g2_msg_notif_timer_t *t = &g2_msg_notif_timer_2007405c;

    (void)aeabi_memset_43c0e4(t, sizeof(*t), 0);
    t->state = MSG_NOTIF_TIMER_IDLE;
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_init, 0x16u, msg_init);
    if (log_compressed_on())
        (void)compress_log_output(0x10000000u, msg_init_short, msg_init_short);
}

void msg_notif_timer_mgr_deinit_552906(void)
{
    g2_msg_notif_timer_2007405c.state = MSG_NOTIF_TIMER_IDLE;
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_deinit, 0x1cu, msg_deinit);
    if (log_compressed_on())
        (void)compress_log_output(0x10000000u, msg_deinit_short, msg_deinit_short);
}

void msg_notif_timer_mgr_start_552948(uint32_t timeout_ms)
{
    g2_msg_notif_timer_t *t = &g2_msg_notif_timer_2007405c;

    if ((uint8_t)display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER)
        return;
    t->start_tick = osKernelGetTickCount();
    t->timeout_ms = timeout_ms;
    t->state = MSG_NOTIF_TIMER_RUNNING;
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_start, 0x2au, msg_start, timeout_ms);
    if (log_compressed_on())
        (void)compress_log_output(0x10400000u, msg_start_short, msg_start_short, timeout_ms);
}

void msg_notif_timer_mgr_stop_5529a2(void)
{
    g2_msg_notif_timer_2007405c.state = MSG_NOTIF_TIMER_IDLE;
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_stop, 0x30u, msg_stop);
    if (log_compressed_on())
        (void)compress_log_output(0x10000000u, msg_stop_short, msg_stop_short);
}

/* Returns 1 exactly once per expiry: the running timer moves to EXPIRED. */
uint32_t msg_notif_timer_mgr_check_timeout_5529e4(void)
{
    g2_msg_notif_timer_t *t = &g2_msg_notif_timer_2007405c;

    if (t->state != MSG_NOTIF_TIMER_RUNNING)
        return 0u;
    uint32_t elapsed = osKernelGetTickCount() - t->start_tick;
    if (elapsed < t->timeout_ms)
        return 0u;
    t->state = MSG_NOTIF_TIMER_EXPIRED;
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_check, 0x3eu, msg_check, elapsed);
    if (log_compressed_on())
        (void)compress_log_output(0x10400000u, msg_check_short, msg_check_short, elapsed);
    return 1u;
}

void msg_notif_timer_mgr_process_timeout_552a4a(void)
{
    if (g2_msg_notif_timer_2007405c.state != MSG_NOTIF_TIMER_EXPIRED)
        return;
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_process, 0x4bu, msg_process);
    if (log_compressed_on())
        (void)compress_log_output(0x0c000000u, msg_process_short, msg_process_short);
    msg_notif_timer_mgr_stop_5529a2();
    if (ui_page_manager_ready_443484() == 1u && audio_quicklist_refresh_enabled_4434d0(MSG_NOTIF_APP_ID) == 1u)
        audio_system_alert_close_464c36(MSG_NOTIF_APP_ID, 0u, 0u, 0u);
}

/* Arms the timer from the ANCC auto-close setting (byte 2, seconds; 0 = 10 s). */
void msg_notif_timer_start_552ab0(void)
{
    if (display_driver_uled_mode_45a568() != DEVICE_ROLE_MASTER)
        return;
    const uint8_t *ancc = audio_message_notify_ancc_state_get_49729c();
    if (ancc[2] == 0u)
        msg_notif_timer_mgr_start_552948(MSG_NOTIF_DEFAULT_TIMEOUT_MS);
    else
        msg_notif_timer_mgr_start_552948((uint32_t)ancc[2] * 1000u);
}

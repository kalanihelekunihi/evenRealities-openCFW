/* EvenAI common/heartbeat timer managers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenAI\even_ai_timer.c.
 * Native 0x4e2e10..0x4e31cc (literal pool 0x4e3130..0x4e3193). The start/stop
 * entries 0x4e2e62, 0x4e2e86, 0x4e304c and 0x4e31a0 live in rtos/even-ai/.
 *
 * Each timer is a 10-byte record: start tick (+0), interval (+4),
 * state (+8: 1 armed, 2 expired) and armed flag (+9). Expiry is polled from the
 * EvenAI frame task via even_ai_timer_process_all. */
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t start_tick; /* +0 */
    uint32_t interval;   /* +4 */
    uint8_t state;       /* +8 1 running, 2 expired */
    uint8_t armed;       /* +9 */
} g2_even_ai_timer_t;

extern uint8_t audio_even_ai_common_timer_state_20074008[10]; /* RAM 0x20074008 */
extern uint8_t audio_even_ai_heartbeat_state_20074014[10];    /* RAM 0x20074014 */
#define COMMON_TIMER ((g2_even_ai_timer_t *)(void *)audio_even_ai_common_timer_state_20074008)
#define HEARTBEAT_TIMER ((g2_even_ai_timer_t *)(void *)audio_even_ai_heartbeat_state_20074014)
extern uint8_t audio_even_ai_ready_state_2006f138[0x218];   /* RAM 0x2006f138, +0 mode, +1 sub-mode */
extern uint8_t audio_even_ai_service_state_2006ed10[0x218]; /* RAM 0x2006ed10, +8 VAD-sent flag */

extern uint32_t osKernelGetTickCount(void);                      /* 0x4490cc */
extern uint8_t audio_uart_device_role_get(void);                 /* 0x45a568, 1 = master */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t length,
                                                   uint32_t id, uint32_t event);
extern void service_even_ai_fn_0049832e(uint32_t event, uint32_t arg); /* 0x49832e */
extern void service_even_ai_fn_00498528(uint32_t vad);                 /* 0x498528 */
extern uint32_t audio_even_ai_common_timer_start_4e2e62(uint32_t duration);
extern void audio_even_ai_common_timer_stop_4e2e86(void);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char timer_tag[] = "even_ai.timer"; /* ROM 0x785df0 */
static const char timer_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai_timer.c"; /* ROM 0x7026e0 */
static const char common_deinit_fn[] = "even_ai_common_timer_mgr_deinit";  /* ROM 0x75fe10 */
static const char common_deinit_msg[] = "even_ai_common_timer_mgr_deinit"; /* ROM 0x75fe30 */
static const char common_deinit_short[] = "[even_ai.timer]even_ai_common_timer_mgr_deinit"; /* ROM 0x733ee4 */
static const char common_timeout_fn[] = "even_ai_common_timer_mgr_process_timeout"; /* ROM 0x73eb5c */
static const char common_timeout_msg[] = "even_ai_common_timer: processing timeout"; /* ROM 0x73eb88 */
static const char common_timeout_short[] =
    "[even_ai.timer]even_ai_common_timer: processing timeout"; /* ROM 0x71ec68 */
static const char hb_deinit_fn[] = "even_ai_heartbeat_timer_mgr_deinit";  /* ROM 0x754458 */
static const char hb_deinit_msg[] = "even_ai_heartbeat_timer_mgr_deinit"; /* ROM 0x75447c */
static const char hb_deinit_short[] = "[even_ai.timer]even_ai_heartbeat_timer_mgr_deinit"; /* ROM 0x7295c0 */
static const char hb_stop_fn[] = "even_ai_heartbeat_timer_mgr_stop";  /* ROM 0x7544a0 */
static const char hb_stop_msg[] = "even_ai_heartbeat_timer_mgr_stop"; /* ROM 0x7544c4 */
static const char hb_stop_short[] = "[even_ai.timer]even_ai_heartbeat_timer_mgr_stop"; /* ROM 0x733f44 */
static const char hb_timeout_fn[] = "even_ai_heartbeat_timer_mgr_process_timeout"; /* ROM 0x73ebb4 */
static const char hb_timeout_msg[] = "even_ai_heartbeat_timer: processing timeout"; /* ROM 0x73ebe0 */
static const char hb_timeout_short[] =
    "[even_ai.timer]even_ai_heartbeat_timer: processing timeout"; /* ROM 0x714cb0 */

#define TIMER_LOG(level, fn, line, msg, cflags, short_msg)                                  \
    do {                                                                                    \
        if ((audio_log_flags() & 2u) != 0u)                                                 \
            audio_log_extended((level), timer_tag, timer_file, (fn), (line), (msg));        \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)               \
            (void)compress_log_output((cflags), (short_msg), (short_msg));                  \
    } while (0)

enum { TIMER_RUNNING = 1u, TIMER_EXPIRED = 2u };
enum { EVEN_AI_SYNC_APP = 7u, EVEN_AI_CTRL_LEN = 3u, EVEN_AI_SYNC_EVENT = 5u };
#define EVEN_AI_RETRY_MS 3000u

void even_ai_common_timer_mgr_deinit(void) {
    g2_even_ai_timer_t *t = COMMON_TIMER;
    t->armed = 0u;
    t->state = 0u;
    TIMER_LOG(4u, common_deinit_fn, 0x23u, common_deinit_msg, 0x10000000u, common_deinit_short);
}

bool even_ai_common_timer_mgr_check_timeout(void) {
    g2_even_ai_timer_t *t = COMMON_TIMER;
    if (t->armed == 0u)
        return false;
    if (osKernelGetTickCount() - t->start_tick < t->interval)
        return false;
    t->state = TIMER_EXPIRED;
    t->armed = 0u;
    return true;
}

/* On expiry in mode 1 the master re-arms for 3 s and re-sends the 07 07 04
 * listen control to both arms; modes 5..7 report event 3 to the service. */
void even_ai_common_timer_mgr_process_timeout(void) {
    uint8_t listen_vad[3];

    if (COMMON_TIMER->state != TIMER_EXPIRED)
        return;
    TIMER_LOG(3u, common_timeout_fn, 0x55u, common_timeout_msg, 0x0c000000u, common_timeout_short);
    audio_even_ai_common_timer_stop_4e2e86();

    const uint8_t *ready = audio_even_ai_ready_state_2006f138;
    switch (ready[0]) {
    case 1u:
        if (ready[1] == 1u) {
            if (audio_uart_device_role_get() == 1u) {
                /* initializer copied from ROM 0x78f040 (07 07 04 00) */
                uint8_t listen_retry[3] = {7u, 7u, 4u};
                (void)audio_even_ai_common_timer_start_4e2e62(EVEN_AI_RETRY_MS);
                (void)audio_sync_send_to_both_ext_464f76(EVEN_AI_SYNC_APP, listen_retry,
                                                         EVEN_AI_CTRL_LEN, 0u, EVEN_AI_SYNC_EVENT);
            }
        } else if (ready[1] == 2u) {
            audio_uart_buffer_zero(listen_vad, 3u, 0u);
            if (audio_even_ai_service_state_2006ed10[8] == 0u)
                service_even_ai_fn_00498528(3u);
            listen_vad[0] = 7u;
            listen_vad[1] = 7u;
            listen_vad[2] = 4u;
            if (audio_uart_device_role_get() == 1u) {
                (void)audio_even_ai_common_timer_start_4e2e62(EVEN_AI_RETRY_MS);
                (void)audio_sync_send_to_both_ext_464f76(EVEN_AI_SYNC_APP, listen_vad,
                                                         EVEN_AI_CTRL_LEN, 0u, EVEN_AI_SYNC_EVENT);
            }
        }
        break;
    case 5u:
    case 6u:
        service_even_ai_fn_0049832e(3u, 0u);
        break;
    case 7u:
        service_even_ai_fn_0049832e(3u, 0u);
        break;
    default:
        break;
    }
}

void even_ai_heartbeat_timer_mgr_deinit(void) {
    g2_even_ai_timer_t *t = HEARTBEAT_TIMER;
    t->armed = 0u;
    t->state = 0u;
    TIMER_LOG(4u, hb_deinit_fn, 0xafu, hb_deinit_msg, 0x10000000u, hb_deinit_short);
}

void even_ai_heartbeat_timer_mgr_stop(void) {
    g2_even_ai_timer_t *t = HEARTBEAT_TIMER;
    t->armed = 0u;
    t->state = 0u;
    TIMER_LOG(4u, hb_stop_fn, 0xc5u, hb_stop_msg, 0x10000000u, hb_stop_short);
}

bool even_ai_heartbeat_timer_mgr_check_timeout(void) {
    g2_even_ai_timer_t *t = HEARTBEAT_TIMER;
    if (t->armed == 0u)
        return false;
    if (osKernelGetTickCount() - t->start_tick < t->interval)
        return false;
    t->state = TIMER_EXPIRED;
    t->armed = 0u;
    return true;
}

/* A missed heartbeat ends the session through service event 3. */
void even_ai_heartbeat_timer_mgr_process_timeout(void) {
    if (HEARTBEAT_TIMER->state != TIMER_EXPIRED)
        return;
    TIMER_LOG(3u, hb_timeout_fn, 0xe1u, hb_timeout_msg, 0x0c000000u, hb_timeout_short);
    even_ai_heartbeat_timer_mgr_stop();
    service_even_ai_fn_0049832e(3u, 0u);
}

void even_ai_timer_deinit_all(void) {
    even_ai_common_timer_mgr_deinit();
    even_ai_heartbeat_timer_mgr_deinit();
}

void even_ai_timer_process_all(void) {
    if (even_ai_common_timer_mgr_check_timeout())
        even_ai_common_timer_mgr_process_timeout();
    if (even_ai_heartbeat_timer_mgr_check_timeout())
        even_ai_heartbeat_timer_mgr_process_timeout();
}

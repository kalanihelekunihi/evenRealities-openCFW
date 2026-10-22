/* Display-start blocking window of the sync framework (master role only),
 * stock D:\01_workspace\s200_ap510b_iar_git\framework\sync\sync_framework.c.
 * Native 0x45bc06..0x45bc77 (DispStartBlocking_TimerCb), 0x45bca0..0x45be61
 * (DispStartBlockingEn), 0x45be6c..0x45bf71 (DispStartBlockingCancel);
 * literal pool 0x45bff0..0x45c057.
 *
 * DispStartBlockingEn raises the 16-bit flag at RAM 0x20074f48 and arms the
 * one-shot timer at RAM 0x200749dc (clamped to 15000 ms); the timer callback or
 * DispStartBlockingCancel clears it. While the flag is set the schedule manager
 * (0x45c058) refuses idle app launches. Mutex and timer are created by the
 * schedule-manager thread. */
#include <stdint.h>
#include <stddef.h>

extern void *g2_disp_start_blocking_mutex;           /* RAM 0x200749e0 */
extern void *g2_disp_start_blocking_timer;           /* RAM 0x200749dc */
extern volatile uint16_t g2_disp_start_blocking_flag; /* RAM 0x20074f48 */

extern uint8_t audio_uart_device_role_get(void); /* 0x45a568, 2 = slave */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);
extern int32_t osMutexRelease(void *mutex);
extern int32_t osTimerStart(void *timer, uint32_t ticks);
extern int32_t osTimerStop(void *timer);
extern uint32_t osTimerIsRunning(void *timer);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

#define DEVICE_ROLE_SLAVE 2u
#define DISP_START_BLOCKING_MAX_MS 15000u

static const char module[] = "sync.module.framework"; /* ROM 0x77c07c */
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"; /* ROM 0x705fb8 */
static const char fn_timer_cb[] = "DispStartBlocking_TimerCb"; /* ROM 0x7726c0 */
static const char fn_enable[] = "DispStartBlockingEn"; /* ROM 0x783bcc */
static const char fn_cancel[] = "DispStartBlockingCancel"; /* ROM 0x77c0f4 */

static const char e_expired[] = "DispStartBlocking timer expired, flag cleared"; /* ROM 0x738cb4 */
static const char c_expired[] =
    "[sync.module.framework]DispStartBlocking timer expired, flag cleared"; /* ROM 0x6fd46c */
static const char e_slave_block[] = "slave role don't need to block"; /* ROM 0x7657d0 */
static const char c_slave_block[] =
    "[sync.module.framework]slave role don't need to block"; /* ROM 0x723690 */
static const char e_not_ready[] = "DispStartBlockingEn: timer/mutex not ready"; /* ROM 0x743f3c */
static const char c_not_ready[] =
    "[sync.module.framework]DispStartBlockingEn: timer/mutex not ready"; /* ROM 0x706150 */
static const char e_en_mutex[] = "DispStartBlockingEn: mutex acquire failed"; /* ROM 0x743f68 */
static const char c_en_mutex[] =
    "[sync.module.framework]DispStartBlockingEn: mutex acquire failed"; /* ROM 0x706194 */
static const char e_start_failed[] = "DispStartBlockingEn: osTimerStart failed, st=%d"; /* ROM 0x738ce4 */
static const char c_start_failed[] =
    "[sync.module.framework]DispStartBlockingEn: osTimerStart failed, st=%d"; /* ROM 0x6fd4b4 */
static const char e_timeout[] = "DispStartBlockingEn: timeout=%u ms"; /* ROM 0x75a65c */
static const char c_timeout[] =
    "[sync.module.framework]DispStartBlockingEn: timeout=%u ms"; /* ROM 0x718ff4 */
static const char e_slave_cancel[] = "slave role don't need to cancel block"; /* ROM 0x74eb3c */
static const char c_slave_cancel[] =
    "[sync.module.framework]slave role don't need to cancel block"; /* ROM 0x70f664 */
static const char e_cancel_mutex[] = "DispStartBlockingCancel: mutex acquire failed"; /* ROM 0x738d14 */
static const char c_cancel_mutex[] =
    "[sync.module.framework]DispStartBlockingCancel: mutex acquire failed"; /* ROM 0x6fd4fc */
static const char e_cancelled[] = "DispStartBlockingCancel: flag cleared, timer stopped"; /* ROM 0x7236c8 */
static const char c_cancelled[] =
    "[sync.module.framework]DispStartBlockingCancel: flag cleared, timer stopped"; /* ROM 0x6f6614 */

static void log0(const char *fn, uint8_t level, uint32_t line, const char *e, const char *c)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, fn, line, e);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output((uint32_t)level << 26, c, c);
}

static void log1(const char *fn, uint8_t level, uint32_t line, const char *e, const char *c,
                 uint32_t value)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(level, module, source, fn, line, e, value);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(((uint32_t)level << 26) | 0x400000u, c, c, value);
}

/* osTimerNew callback (Thumb 0x45bc07). The flag is cleared even when the
 * mutex is missing or busy (try-acquire with timeout 0). */
void DispStartBlocking_TimerCb_45bc06(void *argument)
{
    (void)argument;
    if (g2_disp_start_blocking_mutex != NULL &&
        osMutexAcquire(g2_disp_start_blocking_mutex, 0u) == 0) {
        g2_disp_start_blocking_flag = 0u;
        (void)osMutexRelease(g2_disp_start_blocking_mutex);
    } else {
        g2_disp_start_blocking_flag = 0u;
    }
    log0(fn_timer_cb, 3u, 0x2b3u, e_expired, c_expired);
}

/* Returns 0 when armed, -1 when already blocking or on RTOS failure,
 * -2 on the slave role. */
int32_t DispStartBlockingEn_45bca0(uint32_t timeout_ms)
{
    if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE) {
        log0(fn_enable, 3u, 0x2bdu, e_slave_block, c_slave_block);
        return -2;
    }
    if (g2_disp_start_blocking_timer == NULL || g2_disp_start_blocking_mutex == NULL) {
        log0(fn_enable, 2u, 0x2c1u, e_not_ready, c_not_ready);
        return -1;
    }
    if (timeout_ms >= DISP_START_BLOCKING_MAX_MS + 1u)
        timeout_ms = DISP_START_BLOCKING_MAX_MS;
    if (osMutexAcquire(g2_disp_start_blocking_mutex, UINT32_MAX) != 0) {
        log0(fn_enable, 1u, 0x2cau, e_en_mutex, c_en_mutex);
        return -1;
    }
    int32_t result = 0;
    if (g2_disp_start_blocking_flag != 0u) {
        result = -1;
    } else {
        g2_disp_start_blocking_flag = 1u;
        int32_t status = osTimerStart(g2_disp_start_blocking_timer, timeout_ms);
        if (status != 0) {
            log1(fn_enable, 1u, 0x2d5u, e_start_failed, c_start_failed, (uint32_t)status);
            g2_disp_start_blocking_flag = 0u;
            result = -1;
        } else {
            log1(fn_enable, 3u, 0x2d9u, e_timeout, c_timeout, timeout_ms);
        }
    }
    (void)osMutexRelease(g2_disp_start_blocking_mutex);
    return result;
}

void DispStartBlockingCancel_45be6c(void)
{
    if (audio_uart_device_role_get() == DEVICE_ROLE_SLAVE) {
        log0(fn_cancel, 3u, 0x2e4u, e_slave_cancel, c_slave_cancel);
        return;
    }
    if (g2_disp_start_blocking_mutex == NULL) {
        g2_disp_start_blocking_flag = 0u;
        return;
    }
    if (osMutexAcquire(g2_disp_start_blocking_mutex, UINT32_MAX) != 0) {
        log0(fn_cancel, 1u, 0x2ecu, e_cancel_mutex, c_cancel_mutex);
        g2_disp_start_blocking_flag = 0u;
        return;
    }
    if (g2_disp_start_blocking_timer != NULL &&
        osTimerIsRunning(g2_disp_start_blocking_timer) != 0u)
        (void)osTimerStop(g2_disp_start_blocking_timer);
    g2_disp_start_blocking_flag = 0u;
    (void)osMutexRelease(g2_disp_start_blocking_mutex);
    log0(fn_cancel, 4u, 0x2f7u, e_cancelled, c_cancelled);
}

/* Cordio WSF timer service, Ambiq FreeRTOS port, stock
 * D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\wsf\sources\port\freertos\wsf_timer.c.
 * Native WsfTimerUpdate 0x52a4e6, WsfTimerNextExpiration 0x52a51a and
 * WsfTimerUpdateTicks 0x52a574..0x52a613; literal pool 0x52a614..0x52a63b.
 *
 * The Ambiq FreeRTOS port is not the public r20.05c baremetal body: timers are
 * driven from a FreeRTOS software timer ("WSF Timer") and a tick snapshot.
 * Stock folds CLK_TICKS_PER_WSF_TICKS to 10 and pdMS_TO_TICKS(next * 10) to
 * (next * 10000) / 1000. The other functions of this file are already in
 * g2/src: wsfTimerRemove (ble/wsf-timer), wsfTimerInsert (ble/ble-wsf),
 * WsfTimerInit (ble/wsf-timer) and WsfTimerServiceExpired
 * (apollo-common/wsf-radio). */
#include <stdint.h>
#include <stddef.h>

/* wsfTimer_t in the stock layout: next +0, ticks +4, msg +8, handlerId +0xc, isStarted +0xd. */
typedef struct g2_wsf_timer {
    struct g2_wsf_timer *next; /* +0x0 */
    uint32_t ticks;            /* +0x4 */
    uint8_t msg[4];            /* +0x8 wsfMsgHdr_t */
    uint8_t handler_id;        /* +0xc */
    uint8_t is_started;        /* +0xd */
} g2_wsf_timer_t;

#define WSF_TIMER_EVENT 2u
#define CLK_TICKS_PER_WSF_TICK 10u
#define TMR_COMMAND_CHANGE_PERIOD 4u
#define TIMER_CMD_WAIT 100u

extern uint32_t audio_wsf_timer_list[2];        /* RAM 0x200741b0 wsfTimerTimerQueue {head, tail} */
extern void *audio_wsf_timer_handle;            /* RAM 0x20074ef4 xWsfTimer */
extern uint32_t audio_wsf_timer_last_tick;      /* RAM 0x20074ef8 g_ui32LastTime */

extern void WsfTaskLock(void);                  /* 0x52b8c8 */
extern void WsfTaskUnlock(void);                /* 0x52b8d0 */
extern void WsfTaskSetReady(uint8_t handler_id, uint8_t event); /* 0x52b95e */
extern uint32_t xTaskGetTickCount(void);        /* 0x454efe */
extern uint32_t ulSetInterruptMask(void);       /* 0x5fa0a4 */
/* FreeRTOS xTimerGenericCommand(timer, command, value, woken, wait). */
extern int32_t audio_uart_ring_persist_wait_event_47e7b0(uint32_t timer, uint32_t command,
                                                         uint32_t value, void *woken,
                                                         uint32_t wait);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char wsf_tag[] = "wsf_timer"; /* ROM 0x78c968 */
static const char wsf_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\wsf\\sources\\port\\freertos\\wsf_timer.c"; /* ROM 0x6df034 */
static const char update_ticks_fn[] = "WsfTimerUpdateTicks"; /* ROM 0x784b6c */
static const char change_failed[] = "--->xTimerChangePeriod failed"; /* ROM 0x768250 */
static const char change_failed_short[] = "[wsf_timer]--->xTimerChangePeriod failed"; /* ROM 0x746cf4 */

void WsfTimerUpdate(uint32_t ticks)
{
    WsfTaskLock();
    for (g2_wsf_timer_t *timer = (g2_wsf_timer_t *)(uintptr_t)audio_wsf_timer_list[0];
         timer != NULL; timer = timer->next) {
        if (timer->ticks > ticks) {
            timer->ticks -= ticks;
        } else {
            timer->ticks = 0u;
            WsfTaskSetReady(timer->handler_id, WSF_TIMER_EVENT);
        }
    }
    WsfTaskUnlock();
}

uint32_t WsfTimerNextExpiration(uint8_t *timer_running)
{
    uint32_t ticks;
    WsfTaskLock();
    if (audio_wsf_timer_list[0] == 0u) {
        *timer_running = 0u;
        ticks = 0u;
    } else {
        *timer_running = 1u;
        ticks = ((g2_wsf_timer_t *)(uintptr_t)audio_wsf_timer_list[0])->ticks;
    }
    WsfTaskUnlock();
    return ticks;
}

void WsfTimerUpdateTicks(void)
{
    uint8_t running;
    uint32_t now = xTaskGetTickCount();
    uint32_t elapsed = now - audio_wsf_timer_last_tick;

    if (elapsed / CLK_TICKS_PER_WSF_TICK != 0u) {
        WsfTimerUpdate(elapsed / CLK_TICKS_PER_WSF_TICK);
        audio_wsf_timer_last_tick = now;
    }
    uint32_t next = WsfTimerNextExpiration(&running);
    if (next == 0u)
        return;

    /* configASSERT(pdPASS == xTimerChangePeriod(xWsfTimer, pdMS_TO_TICKS(next * 10), 100)) */
    int32_t status = audio_uart_ring_persist_wait_event_47e7b0(
        (uint32_t)(uintptr_t)audio_wsf_timer_handle, TMR_COMMAND_CHANGE_PERIOD,
        (next * 10000u) / 1000u, NULL, TIMER_CMD_WAIT);
    if (status != 1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, wsf_tag, wsf_file, update_ticks_fn, 0x199u, change_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, change_failed_short, change_failed_short);
    }
    if (status != 1) {
        (void)ulSetInterruptMask();
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
        for (;;) {
        }
    }
}

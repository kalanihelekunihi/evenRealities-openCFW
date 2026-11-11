// SPDX-License-Identifier: BSD-3-Clause
/*
 * wsfOsDispatcher (stock 0x52B9D0) and wsfOsReadyToSleep (stock 0x52B99E).
 *
 * Upstream: AmbiqSuite R3.2.0 third_party/cordio/wsf/sources/port/freertos/wsf_os.c.
 * Verified against headless-decomp 12.1.4 decompilation of G2 2.2.6.10 (g2c campaign):
 * the task record is audio_wsf_task_state (RAM 0x20073230) with
 * handler[10] @0x00, handlerEventMask[10] (uint8) @0x28, msgQueue @0x34 and
 * taskEventMask @0x3C, matching display_ble_wsf_queue_ready.c. The tail waits on
 * audio_wsf_event_group (RAM 0x20074EF0) with xEventGroupWaitBits(.., 1, 1, 0,
 * portMAX_DELAY) exactly as the AmbiqSuite FreeRTOS port does.
 */
#include <stdint.h>
#include <stddef.h>

typedef void (*wsf_handler_t)(uint8_t event, void *msg);

extern uint8_t audio_wsf_task_state[];
extern void *audio_wsf_event_group;
extern void WsfTimerUpdateTicks(void);
extern void *WsfMsgDeq(void *queue, uint8_t *handler_id);
extern void WsfMsgFree(void *msg);
extern void *WsfTimerServiceExpired(uint8_t task_id);
extern void WsfCsEnter(void);
extern void WsfCsExit(void);
extern uint32_t xEventGroupWaitBits(void *group, uint32_t bits, int clear, int all, uint32_t ticks);

#define WSF_HANDLER(i)    (((wsf_handler_t *)(void *)audio_wsf_task_state)[(i)])
#define WSF_HANDLER_EV(i) (audio_wsf_task_state[0x28u + (i)])
#define WSF_TASK_EV       (audio_wsf_task_state[0x3Cu])
#define WSF_MAX_HANDLERS  10u

int wsfOsReadyToSleep(void)
{
    return WSF_TASK_EV == 0u;
}

void wsfOsDispatcher(void)
{
    WsfTimerUpdateTicks();
    while (WSF_TASK_EV != 0u) {
        WsfCsEnter();
        uint8_t task_ev = WSF_TASK_EV;
        WSF_TASK_EV = 0u;
        WsfCsExit();

        if (task_ev & 1u) {                       /* WSF_MSG_QUEUE_EVENT */
            uint8_t id;
            void *msg;
            while ((msg = WsfMsgDeq(audio_wsf_task_state + 0x34u, &id)) != NULL) {
                WSF_HANDLER(id)(0u, msg);
                WsfMsgFree(msg);
            }
        }
        if (task_ev & 2u) {                       /* WSF_TIMER_EVENT */
            uint8_t *timer;
            while ((timer = WsfTimerServiceExpired(0u)) != NULL)
                WSF_HANDLER(timer[0xCu])(0u, timer + 8u);
        }
        if (task_ev & 4u) {                       /* WSF_HANDLER_EVENT */
            for (uint8_t i = 0; i < WSF_MAX_HANDLERS; i++) {
                if (WSF_HANDLER_EV(i) != 0u && WSF_HANDLER(i) != NULL) {
                    WsfCsEnter();
                    uint8_t ev = WSF_HANDLER_EV(i);
                    WSF_HANDLER_EV(i) = 0u;
                    WsfCsExit();
                    WSF_HANDLER(i)(ev, NULL);
                }
            }
        }
    }
    WsfTimerUpdateTicks();
    if (wsfOsReadyToSleep())
        (void)xEventGroupWaitBits(audio_wsf_event_group, 1u, 1, 0, 0xFFFFFFFFu);
}

/*
 * WsfTimerServiceExpired (stock 0x52A542), AmbiqSuite FreeRTOS-port wsf_timer.c.
 * Same body as the unlinked model g2/src/apollo-common/wsf-radio/timer_expired.c,
 * here under its upstream name so the dispatcher links. Timer queue head is
 * audio_wsf_timer_list (RAM 0x200741B0); wsfTimer_t: next +0, ticks +4,
 * msg +8, handlerId +0xC, isStarted +0xD.
 */
extern uint32_t audio_wsf_timer_list[2];
extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);
extern void WsfQueueRemove(void *queue, void *element, void *previous);

void *WsfTimerServiceExpired(uint8_t task_id)
{
    (void)task_id;
    WsfTaskLock();
    uint8_t *timer = (uint8_t *)(uintptr_t)audio_wsf_timer_list[0];
    if (timer != NULL && *(uint32_t *)(void *)(timer + 4u) == 0u) {
        WsfQueueRemove(audio_wsf_timer_list, timer, NULL);
        timer[0x0Du] = 0u;
        WsfTaskUnlock();
        return timer;
    }
    WsfTaskUnlock();
    return NULL;
}

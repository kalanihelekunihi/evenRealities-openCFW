/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 EvenAI tick/deadline manager.  The
 * authenticated stock object uses two private 12-byte records and unsigned
 * tick subtraction; it does not allocate CMSIS or FreeRTOS software timers.
 */
#include "even_ai_timer.h"

#define OPEN_CFW_STATIC_ASSERT(name, condition) \
    typedef char open_cfw_static_assert_##name[(condition) ? 1 : -1]

OPEN_CFW_STATIC_ASSERT(timer_record_size,
                       sizeof(open_cfw_even_ai_timer_record) == 12U);

#ifndef OPEN_CFW_EVEN_AI_COMMON_TIMER
#define OPEN_CFW_EVEN_AI_COMMON_TIMER \
    (*(volatile open_cfw_even_ai_timer_record *)0x20074008U)
#endif

#ifndef OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER
#define OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER \
    (*(volatile open_cfw_even_ai_timer_record *)0x20074014U)
#endif

#ifndef OPEN_CFW_EVEN_AI_WORKFLOW_STATE
#define OPEN_CFW_EVEN_AI_WORKFLOW_STATE \
    ((volatile uint8_t *)0x2006F138U)
#endif

#ifndef OPEN_CFW_EVEN_AI_SERVICE_STATUS
#define OPEN_CFW_EVEN_AI_SERVICE_STATUS \
    ((volatile uint8_t *)0x2006ED10U)
#endif

#ifndef OPEN_CFW_EVEN_AI_TICK_NOW
uint32_t open_cfw_even_ai_tick_now(void);
#define OPEN_CFW_EVEN_AI_TICK_NOW() open_cfw_even_ai_tick_now()
#endif

#ifndef OPEN_CFW_EVEN_AI_ROLE
uint8_t open_cfw_even_ai_role(void);
#define OPEN_CFW_EVEN_AI_ROLE() open_cfw_even_ai_role()
#endif

#ifndef OPEN_CFW_EVEN_AI_SYNC
int open_cfw_even_ai_sync(uint16_t record_id, const void *payload,
                          uint32_t payload_bytes, void *completion,
                          uint32_t channel);
#define OPEN_CFW_EVEN_AI_SYNC(record_id, payload, payload_bytes, completion, channel) \
    open_cfw_even_ai_sync( \
        (record_id), (payload), (payload_bytes), (completion), (channel))
#endif

#ifndef OPEN_CFW_EVEN_AI_SEND_CONTROL
void open_cfw_even_ai_send_control(uint8_t command);
#define OPEN_CFW_EVEN_AI_SEND_CONTROL(command) \
    open_cfw_even_ai_send_control((command))
#endif

#ifndef OPEN_CFW_EVEN_AI_SET_STATE
void open_cfw_even_ai_set_state(uint32_t command, uint32_t value);
#define OPEN_CFW_EVEN_AI_SET_STATE(command, value) \
    open_cfw_even_ai_set_state((command), (value))
#endif

#if defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) || \
    defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) || \
    defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) || \
    defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
static void open_cfw_even_ai_timer_clear(
    volatile open_cfw_even_ai_timer_record *timer
)
{
    timer->state = 0U;
    timer->armed = 0U;
}
#endif

#if defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_common_timer_mgr_deinit(void)
{
    open_cfw_even_ai_timer_clear(&OPEN_CFW_EVEN_AI_COMMON_TIMER);
}
#endif

#if defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_common_timer_mgr_start(uint32_t duration_ticks)
{
    volatile open_cfw_even_ai_timer_record *timer;
    if (OPEN_CFW_EVEN_AI_ROLE() != 1U) {
        return;
    }
    timer = &OPEN_CFW_EVEN_AI_COMMON_TIMER;
    timer->start_tick = OPEN_CFW_EVEN_AI_TICK_NOW();
    timer->duration_ticks = duration_ticks;
    timer->state = 1U;
    timer->armed = 1U;
}
#endif

#if defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_common_timer_mgr_stop(void)
{
    open_cfw_even_ai_timer_clear(&OPEN_CFW_EVEN_AI_COMMON_TIMER);
}
#endif

#if defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
int open_cfw_even_ai_common_timer_mgr_check_timeout(void)
{
    volatile open_cfw_even_ai_timer_record *timer =
        &OPEN_CFW_EVEN_AI_COMMON_TIMER;
    if (timer->armed == 0U ||
        (uint32_t)(OPEN_CFW_EVEN_AI_TICK_NOW() - timer->start_tick) <
            timer->duration_ticks) {
        return 0;
    }
    timer->state = 2U;
    timer->armed = 0U;
    return 1;
}
#endif

#if defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_common_timer_mgr_process_timeout(void)
{
    const volatile uint8_t *workflow = OPEN_CFW_EVEN_AI_WORKFLOW_STATE;
    uint32_t payload = 0x00040707U;

    if (OPEN_CFW_EVEN_AI_COMMON_TIMER.state != 2U) {
        return;
    }
    open_cfw_even_ai_common_timer_mgr_stop();

    if (workflow[0] == 1U) {
        if (workflow[1] == 1U) {
            if (OPEN_CFW_EVEN_AI_ROLE() == 1U) {
                open_cfw_even_ai_common_timer_mgr_start(3000U);
                (void)OPEN_CFW_EVEN_AI_SYNC(7U, &payload, 3U, (void *)0, 5U);
            }
        } else if (workflow[1] == 2U) {
            if (OPEN_CFW_EVEN_AI_SERVICE_STATUS[8] == 0U) {
                OPEN_CFW_EVEN_AI_SEND_CONTROL(3U);
            }
            if (OPEN_CFW_EVEN_AI_ROLE() == 1U) {
                open_cfw_even_ai_common_timer_mgr_start(3000U);
                (void)OPEN_CFW_EVEN_AI_SYNC(7U, &payload, 3U, (void *)0, 5U);
            }
        }
    } else if (workflow[0] == 5U || workflow[0] == 6U ||
               workflow[0] == 7U) {
        OPEN_CFW_EVEN_AI_SET_STATE(3U, 0U);
    }
}
#endif

#if defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_heartbeat_timer_mgr_deinit(void)
{
    open_cfw_even_ai_timer_clear(&OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER);
}
#endif

#if defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_heartbeat_timer_mgr_start(uint32_t duration_ticks)
{
    volatile open_cfw_even_ai_timer_record *timer;
    if (OPEN_CFW_EVEN_AI_ROLE() != 1U) {
        return;
    }
    timer = &OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER;
    timer->start_tick = OPEN_CFW_EVEN_AI_TICK_NOW();
    timer->duration_ticks = duration_ticks;
    timer->state = 1U;
    timer->armed = 1U;
}
#endif

#if defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_heartbeat_timer_mgr_stop(void)
{
    open_cfw_even_ai_timer_clear(&OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER);
}
#endif

#if defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
int open_cfw_even_ai_heartbeat_timer_mgr_check_timeout(void)
{
    volatile open_cfw_even_ai_timer_record *timer =
        &OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER;
    if (timer->armed == 0U ||
        (uint32_t)(OPEN_CFW_EVEN_AI_TICK_NOW() - timer->start_tick) <
            timer->duration_ticks) {
        return 0;
    }
    timer->state = 2U;
    timer->armed = 0U;
    return 1;
}
#endif

#if defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_heartbeat_timer_mgr_process_timeout(void)
{
    if (OPEN_CFW_EVEN_AI_HEARTBEAT_TIMER.state != 2U) {
        return;
    }
    open_cfw_even_ai_heartbeat_timer_mgr_stop();
    OPEN_CFW_EVEN_AI_SET_STATE(3U, 0U);
}
#endif

#if defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_timer_deinit_all(void)
{
    open_cfw_even_ai_common_timer_mgr_deinit();
    open_cfw_even_ai_heartbeat_timer_mgr_deinit();
}
#endif

#if defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY))
void open_cfw_even_ai_timer_start_all(uint32_t common_duration_ticks)
{
    open_cfw_even_ai_common_timer_mgr_start(common_duration_ticks);
    open_cfw_even_ai_heartbeat_timer_mgr_start(10000U);
}
#endif

#if defined(OPEN_CFW_EVEN_AI_PROCESS_ALL_ONLY) || \
    (!defined(OPEN_CFW_EVEN_AI_COMMON_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_COMMON_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_DEINIT_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_START_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_STOP_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_CHECK_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_HEARTBEAT_PROCESS_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_DEINIT_ALL_ONLY) && \
     !defined(OPEN_CFW_EVEN_AI_START_ALL_ONLY))
void open_cfw_even_ai_timer_process_all(void)
{
    if (open_cfw_even_ai_common_timer_mgr_check_timeout() != 0) {
        open_cfw_even_ai_common_timer_mgr_process_timeout();
    }
    if (open_cfw_even_ai_heartbeat_timer_mgr_check_timeout() != 0) {
        open_cfw_even_ai_heartbeat_timer_mgr_process_timeout();
    }
}
#endif

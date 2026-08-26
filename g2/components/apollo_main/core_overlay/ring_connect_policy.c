/*
 * OpenCFW clean-room G2 Ring connection policy.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * This implementation is derived from the authenticated public behavior and
 * ABI inventory of the linked G2 object.  It contains no vendor source text.
 */

#include <stdint.h>
#include <stddef.h>

#ifndef OPEN_CFW_RING_POLICY_SELECTOR
#define OPEN_CFW_RING_POLICY_SELECTOR 0
#endif

typedef void (*open_cfw_ring_policy_callback)(uint32_t argument);

struct open_cfw_ring_policy_state {
    uint8_t mode;
    uint8_t reserved[3];
    uint32_t started_at;
    uint8_t connect_info_processed;
};

_Static_assert(offsetof(struct open_cfw_ring_policy_state, started_at) == 4u,
               "G2 Ring-policy start-tick offset changed");
_Static_assert(offsetof(struct open_cfw_ring_policy_state,
                        connect_info_processed) == 8u,
               "G2 Ring-policy throttle offset changed");

#ifndef OPEN_CFW_RING_POLICY_STATE
#define OPEN_CFW_RING_POLICY_STATE \
    (*(volatile struct open_cfw_ring_policy_state *)(uintptr_t)0x2007408cu)
#endif
#ifndef OPEN_CFW_RING_POLICY_THROTTLE_TICK
#define OPEN_CFW_RING_POLICY_THROTTLE_TICK \
    (*(volatile uint32_t *)(uintptr_t)0x200748fcu)
#endif
#ifndef OPEN_CFW_RING_POLICY_RECONNECT_PENDING
#define OPEN_CFW_RING_POLICY_RECONNECT_PENDING \
    (*(volatile uint8_t *)(uintptr_t)0x2007500bu)
#endif

#ifndef OPEN_CFW_RING_POLICY_TICK
uint32_t open_cfw_cmsis_kernel_get_tick_count(void);
#define OPEN_CFW_RING_POLICY_TICK() open_cfw_cmsis_kernel_get_tick_count()
#endif
#ifndef OPEN_CFW_RING_POLICY_REMOVE
uint8_t open_cfw_event_loop_remove_delayed(
    open_cfw_ring_policy_callback callback);
#define OPEN_CFW_RING_POLICY_REMOVE(callback) \
    open_cfw_event_loop_remove_delayed((callback))
#endif
#ifndef OPEN_CFW_RING_POLICY_PUSH
void open_cfw_event_loop_push_delayed(
    open_cfw_ring_policy_callback callback, uint32_t argument, uint32_t delay);
#define OPEN_CFW_RING_POLICY_PUSH(callback, argument, delay) \
    open_cfw_event_loop_push_delayed((callback), (argument), (delay))
#endif
void PB_TxEncodeNotifyRingConnectInfo(uint32_t value);
#ifndef OPEN_CFW_RING_POLICY_NOTIFY
#define OPEN_CFW_RING_POLICY_NOTIFY(value) \
    PB_TxEncodeNotifyRingConnectInfo((value))
#endif
#ifndef OPEN_CFW_RING_POLICY_IS_OWNER
uint32_t open_cfw_retained_ring_is_owner(void);
#define OPEN_CFW_RING_POLICY_IS_OWNER() open_cfw_retained_ring_is_owner()
#endif
#ifndef OPEN_CFW_RING_POLICY_NOTIFY_CALLBACK
#define OPEN_CFW_RING_POLICY_NOTIFY_CALLBACK \
    ((open_cfw_ring_policy_callback)(uintptr_t)0x004bc419u)
#endif
#ifndef OPEN_CFW_RING_POLICY_RECONNECT_CALLBACK
#define OPEN_CFW_RING_POLICY_RECONNECT_CALLBACK \
    ((open_cfw_ring_policy_callback)(uintptr_t)0x0049f501u)
#endif

enum {
    OPEN_CFW_RING_POLICY_IDLE = 0u,
    OPEN_CFW_RING_POLICY_SWITCH = 1u,
    OPEN_CFW_RING_POLICY_FOLLOW_UP = 2u,
    OPEN_CFW_RING_POLICY_SWITCH_TICKS = 20000u,
    OPEN_CFW_RING_POLICY_FOLLOW_UP_TICKS = 3000u,
    OPEN_CFW_RING_POLICY_SUCCESS_DELAY = 200u,
    OPEN_CFW_RING_POLICY_TIMEOUT_EVENT = 0x5au
};

uint32_t open_cfw_ring_policy_tick_now(void);
uint32_t open_cfw_ring_policy_elapsed_ticks(uint32_t started_at);
uint32_t open_cfw_ring_policy_timeout_for_mode(uint8_t mode);
uint8_t open_cfw_ring_policy_get_state(void);
void open_cfw_ring_policy_enter_state(uint8_t mode);
uint32_t open_cfw_ring_policy_on_dominant_hand(
    uint8_t current_hand, uint8_t requested_hand);
uint32_t open_cfw_ring_policy_should_block_connect_info(uint8_t enabled);
void open_cfw_ring_policy_mark_connect_info_processed(uint8_t processed);
void open_cfw_ring_policy_schedule_connect_timeout(void);
void open_cfw_ring_policy_reconnect_timeout_fire(uint32_t argument);
void open_cfw_ring_policy_schedule_reconnect_timeout(void);
void open_cfw_ring_policy_cancel_connect_timeout(void);
void open_cfw_ring_policy_notify_connect_success_soon(void);
void open_cfw_ring_policy_reset(void);
void open_cfw_ring_policy_reset_connect_info_throttle(void);

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 1
__attribute__((noinline)) uint32_t open_cfw_ring_policy_tick_now(void)
{
    return OPEN_CFW_RING_POLICY_TICK();
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 2
__attribute__((noinline)) uint32_t
open_cfw_ring_policy_elapsed_ticks(uint32_t started_at)
{
    return started_at == 0u ? UINT32_MAX :
        open_cfw_ring_policy_tick_now() - started_at;
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 3
__attribute__((noinline)) uint32_t
open_cfw_ring_policy_timeout_for_mode(uint8_t mode)
{
    if (mode == OPEN_CFW_RING_POLICY_SWITCH) {
        return OPEN_CFW_RING_POLICY_SWITCH_TICKS;
    }
    if (mode == OPEN_CFW_RING_POLICY_FOLLOW_UP) {
        return OPEN_CFW_RING_POLICY_FOLLOW_UP_TICKS;
    }
    return 0u;
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 4
__attribute__((noinline)) uint8_t open_cfw_ring_policy_get_state(void)
{
    uint8_t mode = OPEN_CFW_RING_POLICY_STATE.mode;
    uint32_t timeout;

    if (mode == OPEN_CFW_RING_POLICY_IDLE) {
        return mode;
    }
    timeout = open_cfw_ring_policy_timeout_for_mode(mode);
    if (timeout != 0u &&
        open_cfw_ring_policy_elapsed_ticks(
            OPEN_CFW_RING_POLICY_STATE.started_at) >= timeout) {
        OPEN_CFW_RING_POLICY_STATE.mode = OPEN_CFW_RING_POLICY_IDLE;
        OPEN_CFW_RING_POLICY_STATE.started_at = 0u;
        OPEN_CFW_RING_POLICY_STATE.connect_info_processed = 0u;
        mode = OPEN_CFW_RING_POLICY_IDLE;
    }
    return mode;
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 5
__attribute__((noinline)) void open_cfw_ring_policy_enter_state(uint8_t mode)
{
    OPEN_CFW_RING_POLICY_STATE.mode = mode;
    OPEN_CFW_RING_POLICY_STATE.started_at =
        mode == OPEN_CFW_RING_POLICY_IDLE ? 0u :
        open_cfw_ring_policy_tick_now();
    OPEN_CFW_RING_POLICY_STATE.connect_info_processed = 0u;
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 6
__attribute__((noinline)) uint32_t open_cfw_ring_policy_on_dominant_hand(
    uint8_t current_hand, uint8_t requested_hand)
{
    uint8_t mode = open_cfw_ring_policy_get_state();

    if (requested_hand == current_hand) {
        if (mode != OPEN_CFW_RING_POLICY_SWITCH) {
            open_cfw_ring_policy_enter_state(OPEN_CFW_RING_POLICY_FOLLOW_UP);
        }
        return 1u;
    }
    if (mode == OPEN_CFW_RING_POLICY_SWITCH) {
        return 2u;
    }
    open_cfw_ring_policy_enter_state(OPEN_CFW_RING_POLICY_SWITCH);
    return 0u;
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 7
__attribute__((noinline)) uint32_t
open_cfw_ring_policy_should_block_connect_info(uint8_t enabled)
{
    if (enabled == 0u) {
        return 0u;
    }
    if (open_cfw_ring_policy_get_state() == OPEN_CFW_RING_POLICY_SWITCH) {
        return OPEN_CFW_RING_POLICY_STATE.connect_info_processed != 0u;
    }
    if (OPEN_CFW_RING_POLICY_THROTTLE_TICK == 0u ||
        open_cfw_ring_policy_elapsed_ticks(
            OPEN_CFW_RING_POLICY_THROTTLE_TICK) >=
            OPEN_CFW_RING_POLICY_SWITCH_TICKS) {
        return 0u;
    }
    return 1u;
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 8
__attribute__((noinline)) void
open_cfw_ring_policy_mark_connect_info_processed(uint8_t processed)
{
    uint32_t now;

    if (processed == 0u) {
        return;
    }
    now = open_cfw_ring_policy_tick_now();
    OPEN_CFW_RING_POLICY_THROTTLE_TICK = now == 0u ? 1u : now;
    if (open_cfw_ring_policy_get_state() == OPEN_CFW_RING_POLICY_SWITCH) {
        OPEN_CFW_RING_POLICY_STATE.connect_info_processed = 1u;
    }
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 9
__attribute__((noinline)) void
open_cfw_ring_policy_schedule_connect_timeout(void)
{
    (void)OPEN_CFW_RING_POLICY_REMOVE(
        OPEN_CFW_RING_POLICY_NOTIFY_CALLBACK);
    OPEN_CFW_RING_POLICY_PUSH(
        OPEN_CFW_RING_POLICY_NOTIFY_CALLBACK,
        OPEN_CFW_RING_POLICY_TIMEOUT_EVENT,
        OPEN_CFW_RING_POLICY_SWITCH_TICKS);
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 10
__attribute__((noinline)) void
open_cfw_ring_policy_reconnect_timeout_fire(uint32_t argument)
{
    (void)argument;
    OPEN_CFW_RING_POLICY_RECONNECT_PENDING = 0u;
    OPEN_CFW_RING_POLICY_NOTIFY(OPEN_CFW_RING_POLICY_TIMEOUT_EVENT);
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 11
__attribute__((noinline)) void
open_cfw_ring_policy_schedule_reconnect_timeout(void)
{
    if (OPEN_CFW_RING_POLICY_RECONNECT_PENDING != 0u) {
        return;
    }
    OPEN_CFW_RING_POLICY_RECONNECT_PENDING = 1u;
    (void)OPEN_CFW_RING_POLICY_REMOVE(
        OPEN_CFW_RING_POLICY_RECONNECT_CALLBACK);
    OPEN_CFW_RING_POLICY_PUSH(
        OPEN_CFW_RING_POLICY_RECONNECT_CALLBACK, 0u,
        OPEN_CFW_RING_POLICY_SWITCH_TICKS);
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 12
__attribute__((noinline)) void
open_cfw_ring_policy_cancel_connect_timeout(void)
{
    OPEN_CFW_RING_POLICY_RECONNECT_PENDING = 0u;
    (void)OPEN_CFW_RING_POLICY_REMOVE(
        OPEN_CFW_RING_POLICY_RECONNECT_CALLBACK);
    (void)OPEN_CFW_RING_POLICY_REMOVE(
        OPEN_CFW_RING_POLICY_NOTIFY_CALLBACK);
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 13
__attribute__((noinline)) void
open_cfw_ring_policy_notify_connect_success_soon(void)
{
    OPEN_CFW_RING_POLICY_RECONNECT_PENDING = 0u;
    (void)OPEN_CFW_RING_POLICY_REMOVE(
        OPEN_CFW_RING_POLICY_RECONNECT_CALLBACK);
    (void)OPEN_CFW_RING_POLICY_REMOVE(
        OPEN_CFW_RING_POLICY_NOTIFY_CALLBACK);
    if (OPEN_CFW_RING_POLICY_IS_OWNER() != 0u) {
        OPEN_CFW_RING_POLICY_PUSH(
            OPEN_CFW_RING_POLICY_NOTIFY_CALLBACK,
            0u, OPEN_CFW_RING_POLICY_SUCCESS_DELAY);
    }
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 14
__attribute__((noinline)) void open_cfw_ring_policy_reset(void)
{
    open_cfw_ring_policy_enter_state(OPEN_CFW_RING_POLICY_IDLE);
    OPEN_CFW_RING_POLICY_THROTTLE_TICK = 0u;
    OPEN_CFW_RING_POLICY_RECONNECT_PENDING = 0u;
    (void)OPEN_CFW_RING_POLICY_REMOVE(
        OPEN_CFW_RING_POLICY_RECONNECT_CALLBACK);
}
#endif

#if OPEN_CFW_RING_POLICY_SELECTOR == 0 || OPEN_CFW_RING_POLICY_SELECTOR == 15
__attribute__((noinline)) void
open_cfw_ring_policy_reset_connect_info_throttle(void)
{
    OPEN_CFW_RING_POLICY_THROTTLE_TICK = 0u;
}
#endif

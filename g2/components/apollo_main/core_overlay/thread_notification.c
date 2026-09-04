/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 notification thread.  The retained
 * CMSIS entry points use 32-bit opaque handles on Cortex-M; product policy is
 * kept behind narrow provider seams.
 */
#include "thread_notification.h"

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_STATIC_ASSERT(name, condition) \
    typedef char open_cfw_static_assert_##name[(condition) ? 1 : -1]

OPEN_CFW_STATIC_ASSERT(notification_state_size,
                       sizeof(open_cfw_thread_notification_state) == 16U);
OPEN_CFW_STATIC_ASSERT(notification_record_payload_offset,
                       offsetof(open_cfw_thread_notification_record, payload) == 8U);

#if !defined(OPEN_CFW_THREAD_NOTIFICATION_ENTRY_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_INIT_HOOK_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_QUEUE_INIT_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_WHITELIST_INIT_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_STATE_ENTER_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_STATE_READY_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_CREATE_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_DESTROY_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_DRAIN_QUEUE_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_EVENT_HANDLER_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_EXIT_ONLY) && \
    !defined(OPEN_CFW_THREAD_NOTIFICATION_SEND_EVENT_ONLY)
#define OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL 1
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_STATE
#define OPEN_CFW_THREAD_NOTIFICATION_STATE \
    (*(volatile open_cfw_thread_notification_state *)0x200040FCU)
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_ATTRIBUTES
#define OPEN_CFW_THREAD_NOTIFICATION_ATTRIBUTES ((const void *)0x0075B934U)
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_THREAD_NEW
uint32_t open_cfw_thread_notification_thread_new(
    void (*entry)(void *), void *argument, const void *attributes);
#define OPEN_CFW_THREAD_NOTIFICATION_THREAD_NEW(entry, argument, attributes) \
    open_cfw_thread_notification_thread_new((entry), (argument), (attributes))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_THREAD_TERMINATE
int32_t open_cfw_thread_notification_thread_terminate(uint32_t thread_id);
#define OPEN_CFW_THREAD_NOTIFICATION_THREAD_TERMINATE(thread_id) \
    open_cfw_thread_notification_thread_terminate((thread_id))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_FLAGS_SET
uint32_t open_cfw_thread_notification_flags_set(
    uint32_t thread_id, uint32_t flags);
#define OPEN_CFW_THREAD_NOTIFICATION_FLAGS_SET(thread_id, flags) \
    open_cfw_thread_notification_flags_set((thread_id), (flags))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_FLAGS_WAIT
uint32_t open_cfw_thread_notification_flags_wait(
    uint32_t flags, uint32_t options, uint32_t timeout);
#define OPEN_CFW_THREAD_NOTIFICATION_FLAGS_WAIT(flags, options, timeout) \
    open_cfw_thread_notification_flags_wait((flags), (options), (timeout))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_DELAY
int32_t open_cfw_thread_notification_delay(uint32_t ticks);
#define OPEN_CFW_THREAD_NOTIFICATION_DELAY(ticks) \
    open_cfw_thread_notification_delay((ticks))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_QUEUE_NEW
uint32_t open_cfw_thread_notification_queue_new(
    uint32_t count, uint32_t item_bytes, const void *attributes);
#define OPEN_CFW_THREAD_NOTIFICATION_QUEUE_NEW(count, item_bytes, attributes) \
    open_cfw_thread_notification_queue_new((count), (item_bytes), (attributes))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_QUEUE_GET
int32_t open_cfw_thread_notification_queue_get(
    uint32_t queue_id, void *record, uint8_t *priority, uint32_t timeout);
#define OPEN_CFW_THREAD_NOTIFICATION_QUEUE_GET(queue_id, record, priority, timeout) \
    open_cfw_thread_notification_queue_get( \
        (queue_id), (record), (priority), (timeout))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_QUEUE_DELETE
int32_t open_cfw_thread_notification_queue_delete(uint32_t queue_id);
#define OPEN_CFW_THREAD_NOTIFICATION_QUEUE_DELETE(queue_id) \
    open_cfw_thread_notification_queue_delete((queue_id))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_FREE
void open_cfw_thread_notification_free(void *record);
#define OPEN_CFW_THREAD_NOTIFICATION_FREE(record) \
    open_cfw_thread_notification_free((record))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_REGISTER
void open_cfw_thread_notification_register(void);
#define OPEN_CFW_THREAD_NOTIFICATION_REGISTER() \
    open_cfw_thread_notification_register()
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_UNREGISTER
void open_cfw_thread_notification_unregister(void);
#define OPEN_CFW_THREAD_NOTIFICATION_UNREGISTER() \
    open_cfw_thread_notification_unregister()
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_MESSAGE
void open_cfw_thread_notification_dispatch_message(
    const void *payload, uint16_t payload_bytes);
#define OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_MESSAGE(payload, payload_bytes) \
    open_cfw_thread_notification_dispatch_message((payload), (payload_bytes))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_WHITELIST
void open_cfw_thread_notification_dispatch_whitelist(
    const void *payload, uint16_t payload_bytes);
#define OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_WHITELIST(payload, payload_bytes) \
    open_cfw_thread_notification_dispatch_whitelist((payload), (payload_bytes))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_WHITELIST_RELOAD
void open_cfw_thread_notification_whitelist_reload(void);
#define OPEN_CFW_THREAD_NOTIFICATION_WHITELIST_RELOAD() \
    open_cfw_thread_notification_whitelist_reload()
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_MARK_ENTER
void open_cfw_thread_notification_mark_enter(uint32_t thread_class);
#define OPEN_CFW_THREAD_NOTIFICATION_MARK_ENTER(thread_class) \
    open_cfw_thread_notification_mark_enter((thread_class))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_MARK_READY
void open_cfw_thread_notification_mark_ready(uint32_t thread_class);
#define OPEN_CFW_THREAD_NOTIFICATION_MARK_READY(thread_class) \
    open_cfw_thread_notification_mark_ready((thread_class))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_MARK_EXIT
void open_cfw_thread_notification_mark_exit(uint32_t thread_class);
#define OPEN_CFW_THREAD_NOTIFICATION_MARK_EXIT(thread_class) \
    open_cfw_thread_notification_mark_exit((thread_class))
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_PANIC_PREPARE
uint32_t open_cfw_thread_notification_panic_prepare(void);
#define OPEN_CFW_THREAD_NOTIFICATION_PANIC_PREPARE() \
    ((void)open_cfw_thread_notification_panic_prepare())
#endif

#ifndef OPEN_CFW_THREAD_NOTIFICATION_PANIC
#define OPEN_CFW_THREAD_NOTIFICATION_PANIC() \
    do { \
        OPEN_CFW_THREAD_NOTIFICATION_PANIC_PREPARE(); \
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0U; \
        for (;;) { \
        } \
    } while (0)
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_ENTRY_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_entry(void *argument)
{
    (void)argument;
    open_cfw_thread_notification_state_enter();
    open_cfw_thread_notification_queue_init();
    open_cfw_thread_notification_init_hook();
    open_cfw_thread_notification_whitelist_init();
    open_cfw_thread_notification_state_ready();

    for (;;) {
        uint32_t events = OPEN_CFW_THREAD_NOTIFICATION_FLAGS_WAIT(
            OPEN_CFW_THREAD_NOTIFICATION_EVENT_MASK, 0U, UINT32_MAX);
        if (events != 0U && events < 0x80000000U) {
            open_cfw_thread_notification_event_handler(events);
        }
    }
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_INIT_HOOK_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_init_hook(void)
{
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_QUEUE_INIT_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_queue_init(void)
{
    OPEN_CFW_THREAD_NOTIFICATION_STATE.queue_id =
        OPEN_CFW_THREAD_NOTIFICATION_QUEUE_NEW(50U, 4U, NULL);
    if (OPEN_CFW_THREAD_NOTIFICATION_STATE.queue_id == 0U) {
        OPEN_CFW_THREAD_NOTIFICATION_PANIC();
    }
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_WHITELIST_INIT_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_whitelist_init(void)
{
    OPEN_CFW_THREAD_NOTIFICATION_WHITELIST_RELOAD();
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_STATE_ENTER_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_state_enter(void)
{
    OPEN_CFW_THREAD_NOTIFICATION_MARK_ENTER(1U);
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_STATE_READY_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_state_ready(void)
{
    OPEN_CFW_THREAD_NOTIFICATION_MARK_READY(1U);
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_CREATE_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_create(void)
{
    OPEN_CFW_THREAD_NOTIFICATION_STATE.thread_id =
        OPEN_CFW_THREAD_NOTIFICATION_THREAD_NEW(
            open_cfw_thread_notification_entry, NULL,
            OPEN_CFW_THREAD_NOTIFICATION_ATTRIBUTES);
    if (OPEN_CFW_THREAD_NOTIFICATION_STATE.thread_id == 0U) {
        OPEN_CFW_THREAD_NOTIFICATION_PANIC();
    }
    OPEN_CFW_THREAD_NOTIFICATION_REGISTER();
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_DESTROY_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_destroy(void)
{
    if (OPEN_CFW_THREAD_NOTIFICATION_STATE.thread_id != 0U) {
        (void)OPEN_CFW_THREAD_NOTIFICATION_THREAD_TERMINATE(
            OPEN_CFW_THREAD_NOTIFICATION_STATE.thread_id);
        OPEN_CFW_THREAD_NOTIFICATION_STATE.thread_id = 0U;
    }
    OPEN_CFW_THREAD_NOTIFICATION_UNREGISTER();
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_DRAIN_QUEUE_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_drain_queue(void)
{
    open_cfw_thread_notification_record *record = NULL;

    while (OPEN_CFW_THREAD_NOTIFICATION_QUEUE_GET(
               OPEN_CFW_THREAD_NOTIFICATION_STATE.queue_id,
               &record, NULL, 0U) == 0 &&
           record != NULL) {
        uint16_t payload_bytes = (uint16_t)record->payload_bytes;
        if (record->id == OPEN_CFW_THREAD_NOTIFICATION_RECORD_WHITELIST) {
            OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_WHITELIST(
                record->payload, payload_bytes);
        } else if (record->id ==
                   OPEN_CFW_THREAD_NOTIFICATION_RECORD_MESSAGE) {
            OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_MESSAGE(
                record->payload, payload_bytes);
        }
        OPEN_CFW_THREAD_NOTIFICATION_FREE(record);
        record = NULL;
    }
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_EVENT_HANDLER_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_event_handler(uint32_t events)
{
    if ((events & OPEN_CFW_THREAD_NOTIFICATION_EVENT_QUEUE) != 0U) {
        open_cfw_thread_notification_drain_queue();
    }
    if ((events & OPEN_CFW_THREAD_NOTIFICATION_EVENT_WHITELIST) != 0U) {
        OPEN_CFW_THREAD_NOTIFICATION_WHITELIST_RELOAD();
    }
    if ((events & OPEN_CFW_THREAD_NOTIFICATION_EVENT_EXIT) != 0U) {
        open_cfw_thread_notification_exit();
    }
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_EXIT_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
_Noreturn void open_cfw_thread_notification_exit(void)
{
    OPEN_CFW_THREAD_NOTIFICATION_MARK_EXIT(1U);
    if (OPEN_CFW_THREAD_NOTIFICATION_STATE.queue_id != 0U) {
        (void)OPEN_CFW_THREAD_NOTIFICATION_QUEUE_DELETE(
            OPEN_CFW_THREAD_NOTIFICATION_STATE.queue_id);
        OPEN_CFW_THREAD_NOTIFICATION_STATE.queue_id = 0U;
    }
    for (;;) {
        (void)OPEN_CFW_THREAD_NOTIFICATION_DELAY(UINT32_MAX);
    }
}
#endif

#if defined(OPEN_CFW_THREAD_NOTIFICATION_SEND_EVENT_ONLY) || \
    defined(OPEN_CFW_THREAD_NOTIFICATION_BUILD_ALL)
void open_cfw_thread_notification_send_event(uint32_t events)
{
    (void)OPEN_CFW_THREAD_NOTIFICATION_FLAGS_SET(
        OPEN_CFW_THREAD_NOTIFICATION_STATE.thread_id, events);
}
#endif

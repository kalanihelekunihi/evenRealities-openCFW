/* SPDX-License-Identifier: MIT */
#include <setjmp.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "../../components/apollo_main/core_overlay/thread_notification.h"

typedef struct {
    uint32_t id;
    uint32_t payload_bytes;
    uint8_t payload[4];
} host_record;

static open_cfw_thread_notification_state host_state;
static host_record host_records[3];
static open_cfw_thread_notification_record *host_queue[3];
static unsigned host_queue_cursor;
static uint32_t host_queue_new_result = 0x2222U;
static uint32_t host_thread_new_result = 0x1111U;
static unsigned host_queue_new_calls;
static unsigned host_queue_delete_calls;
static unsigned host_thread_new_calls;
static unsigned host_thread_terminate_calls;
static unsigned host_flags_set_calls;
static unsigned host_flags_wait_calls;
static unsigned host_register_calls;
static unsigned host_unregister_calls;
static unsigned host_reload_calls;
static unsigned host_message_calls;
static unsigned host_whitelist_calls;
static unsigned host_free_calls;
static unsigned host_delay_calls;
static unsigned host_mark_enter_calls;
static unsigned host_mark_ready_calls;
static unsigned host_mark_exit_calls;
static unsigned host_panic_calls;
static uint32_t host_last_flags;
static uint32_t host_last_thread;
static uint16_t host_message_bytes;
static uint16_t host_whitelist_bytes;
static uint8_t host_message_payload[4];
static uint8_t host_whitelist_payload[4];
static jmp_buf host_jump;
static int host_jump_enabled;

static void require(int condition)
{
    if (!condition) {
        abort();
    }
}

static uint32_t host_thread_new(
    void (*entry)(void *), void *argument, const void *attributes)
{
    require(entry == open_cfw_thread_notification_entry);
    require(argument == NULL);
    require((uintptr_t)attributes == 0x0075B934U);
    ++host_thread_new_calls;
    return host_thread_new_result;
}

static int32_t host_thread_terminate(uint32_t thread_id)
{
    host_last_thread = thread_id;
    ++host_thread_terminate_calls;
    return 0;
}

static uint32_t host_flags_set(uint32_t thread_id, uint32_t flags)
{
    host_last_thread = thread_id;
    host_last_flags = flags;
    ++host_flags_set_calls;
    return flags;
}

static uint32_t host_flags_wait(
    uint32_t flags, uint32_t options, uint32_t timeout)
{
    static const uint32_t results[] = {0U, 0x80000000U, 2U};
    require(flags == 0x00FFFFFFU);
    require(options == 0U);
    require(timeout == UINT32_MAX);
    if (host_flags_wait_calls < sizeof(results) / sizeof(results[0])) {
        return results[host_flags_wait_calls++];
    }
    ++host_flags_wait_calls;
    require(host_jump_enabled != 0);
    longjmp(host_jump, 1);
}

static int32_t host_delay(uint32_t ticks)
{
    require(ticks == UINT32_MAX);
    ++host_delay_calls;
    require(host_jump_enabled != 0);
    longjmp(host_jump, 2);
}

static uint32_t host_queue_new(
    uint32_t count, uint32_t item_bytes, const void *attributes)
{
    require(count == 50U);
    require(item_bytes == 4U);
    require(attributes == NULL);
    ++host_queue_new_calls;
    return host_queue_new_result;
}

static int32_t host_queue_get(
    uint32_t queue_id, void *output, uint8_t *priority, uint32_t timeout)
{
    open_cfw_thread_notification_record **record =
        (open_cfw_thread_notification_record **)output;
    require(queue_id == host_state.queue_id);
    require(priority == NULL);
    require(timeout == 0U);
    if (host_queue_cursor == 3U) {
        return -3;
    }
    *record = host_queue[host_queue_cursor++];
    return 0;
}

static int32_t host_queue_delete(uint32_t queue_id)
{
    require(queue_id == 0x3333U);
    ++host_queue_delete_calls;
    return 0;
}

static void host_free(void *record)
{
    require(record == host_queue[host_free_calls]);
    ++host_free_calls;
}

static void host_dispatch_message(const void *payload, uint16_t payload_bytes)
{
    host_message_bytes = payload_bytes;
    memcpy(host_message_payload, payload, payload_bytes);
    ++host_message_calls;
}

static void host_dispatch_whitelist(const void *payload, uint16_t payload_bytes)
{
    host_whitelist_bytes = payload_bytes;
    memcpy(host_whitelist_payload, payload, payload_bytes);
    ++host_whitelist_calls;
}

static void host_panic(void)
{
    ++host_panic_calls;
    require(host_jump_enabled != 0);
    longjmp(host_jump, 3);
}

#define OPEN_CFW_THREAD_NOTIFICATION_STATE host_state
#define OPEN_CFW_THREAD_NOTIFICATION_THREAD_NEW(entry, argument, attributes) \
    host_thread_new((entry), (argument), (attributes))
#define OPEN_CFW_THREAD_NOTIFICATION_THREAD_TERMINATE(thread_id) \
    host_thread_terminate((thread_id))
#define OPEN_CFW_THREAD_NOTIFICATION_FLAGS_SET(thread_id, flags) \
    host_flags_set((thread_id), (flags))
#define OPEN_CFW_THREAD_NOTIFICATION_FLAGS_WAIT(flags, options, timeout) \
    host_flags_wait((flags), (options), (timeout))
#define OPEN_CFW_THREAD_NOTIFICATION_DELAY(ticks) host_delay((ticks))
#define OPEN_CFW_THREAD_NOTIFICATION_QUEUE_NEW(count, item_bytes, attributes) \
    host_queue_new((count), (item_bytes), (attributes))
#define OPEN_CFW_THREAD_NOTIFICATION_QUEUE_GET(queue_id, output, priority, timeout) \
    host_queue_get((queue_id), (output), (priority), (timeout))
#define OPEN_CFW_THREAD_NOTIFICATION_QUEUE_DELETE(queue_id) \
    host_queue_delete((queue_id))
#define OPEN_CFW_THREAD_NOTIFICATION_FREE(record) host_free((record))
#define OPEN_CFW_THREAD_NOTIFICATION_REGISTER() (++host_register_calls)
#define OPEN_CFW_THREAD_NOTIFICATION_UNREGISTER() (++host_unregister_calls)
#define OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_MESSAGE(payload, payload_bytes) \
    host_dispatch_message((payload), (payload_bytes))
#define OPEN_CFW_THREAD_NOTIFICATION_DISPATCH_WHITELIST(payload, payload_bytes) \
    host_dispatch_whitelist((payload), (payload_bytes))
#define OPEN_CFW_THREAD_NOTIFICATION_WHITELIST_RELOAD() (++host_reload_calls)
#define OPEN_CFW_THREAD_NOTIFICATION_MARK_ENTER(thread_class) \
    (require((thread_class) == 1U), ++host_mark_enter_calls)
#define OPEN_CFW_THREAD_NOTIFICATION_MARK_READY(thread_class) \
    (require((thread_class) == 1U), ++host_mark_ready_calls)
#define OPEN_CFW_THREAD_NOTIFICATION_MARK_EXIT(thread_class) \
    (require((thread_class) == 1U), ++host_mark_exit_calls)
#define OPEN_CFW_THREAD_NOTIFICATION_PANIC() host_panic()
#include "../../components/apollo_main/core_overlay/thread_notification.c"

int main(void)
{
    unsigned index;

    memset(&host_state, 0, sizeof(host_state));
    open_cfw_thread_notification_queue_init();
    require(host_queue_new_calls == 1U && host_state.queue_id == 0x2222U);

    open_cfw_thread_notification_create();
    require(host_thread_new_calls == 1U && host_state.thread_id == 0x1111U);
    require(host_register_calls == 1U);

    open_cfw_thread_notification_send_event(0x00400002U);
    require(host_flags_set_calls == 1U && host_last_thread == 0x1111U);
    require(host_last_flags == 0x00400002U);

    host_records[0].id = 4U;
    host_records[0].payload_bytes = 0x00010002U;
    host_records[0].payload[0] = 0xA1U;
    host_records[0].payload[1] = 0xA2U;
    host_records[1].id = 0x101U;
    host_records[1].payload_bytes = 3U;
    host_records[1].payload[0] = 0xB1U;
    host_records[1].payload[1] = 0xB2U;
    host_records[1].payload[2] = 0xB3U;
    host_records[2].id = 0xDEADU;
    host_records[2].payload_bytes = 1U;
    for (index = 0; index < 3U; ++index) {
        host_queue[index] = (open_cfw_thread_notification_record *)&host_records[index];
    }
    open_cfw_thread_notification_event_handler(0x00400002U);
    require(host_queue_cursor == 3U && host_free_calls == 3U);
    require(host_whitelist_calls == 1U && host_whitelist_bytes == 2U);
    require(host_whitelist_payload[0] == 0xA1U &&
            host_whitelist_payload[1] == 0xA2U);
    require(host_message_calls == 1U && host_message_bytes == 3U);
    require(host_message_payload[0] == 0xB1U &&
            host_message_payload[2] == 0xB3U);
    require(host_reload_calls == 1U);

    host_state.thread_id = 0x1111U;
    open_cfw_thread_notification_destroy();
    require(host_thread_terminate_calls == 1U && host_last_thread == 0x1111U);
    require(host_state.thread_id == 0U && host_unregister_calls == 1U);
    open_cfw_thread_notification_destroy();
    require(host_thread_terminate_calls == 1U && host_unregister_calls == 2U);

    host_state.queue_id = 0x3333U;
    host_jump_enabled = 1;
    if (setjmp(host_jump) == 0) {
        open_cfw_thread_notification_exit();
    }
    host_jump_enabled = 0;
    require(host_mark_exit_calls == 1U && host_queue_delete_calls == 1U);
    require(host_state.queue_id == 0U && host_delay_calls == 1U);

    host_queue_new_result = 0U;
    host_jump_enabled = 1;
    if (setjmp(host_jump) == 0) {
        open_cfw_thread_notification_queue_init();
    }
    host_jump_enabled = 0;
    require(host_panic_calls == 1U);

    host_queue_new_result = 0x2222U;
    host_thread_new_result = 0U;
    host_jump_enabled = 1;
    if (setjmp(host_jump) == 0) {
        open_cfw_thread_notification_create();
    }
    host_jump_enabled = 0;
    require(host_panic_calls == 2U && host_register_calls == 1U);

    host_thread_new_result = 0x1111U;
    host_flags_wait_calls = 0U;
    host_reload_calls = 0U;
    host_queue_new_calls = 0U;
    host_jump_enabled = 1;
    if (setjmp(host_jump) == 0) {
        open_cfw_thread_notification_entry(NULL);
    }
    host_jump_enabled = 0;
    require(host_mark_enter_calls == 1U && host_mark_ready_calls == 1U);
    require(host_queue_new_calls == 1U && host_flags_wait_calls == 4U);
    require(host_reload_calls == 2U);
    return 0;
}

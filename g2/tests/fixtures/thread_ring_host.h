#ifndef OPEN_CFW_THREAD_RING_HOST_H
#define OPEN_CFW_THREAD_RING_HOST_H

#include <stddef.h>
#include <stdint.h>

extern void *host_thread_ring_thread_id;
extern void *host_thread_ring_queue_id;

void *host_thread_ring_thread_new(
    void (*entry)(void *), void *argument, const void *attributes);
int32_t host_thread_ring_thread_terminate(void *thread_id);
uint32_t host_thread_ring_flags_set(void *thread_id, uint32_t flags);
uint32_t host_thread_ring_flags_wait(
    uint32_t flags, uint32_t options, uint32_t timeout);
int32_t host_thread_ring_delay(uint32_t ticks);
void *host_thread_ring_queue_new(
    uint32_t count, uint32_t size, const void *attributes);
int32_t host_thread_ring_queue_put(
    void *queue_id, const void *message, uint8_t priority, uint32_t timeout);
int32_t host_thread_ring_queue_get(
    void *queue_id, void *message, uint8_t *priority, uint32_t timeout);
int32_t host_thread_ring_queue_delete(void *queue_id);
void host_thread_ring_assert_fail(void);
void *host_thread_ring_alloc(size_t size);
void host_thread_ring_free(void *allocation);
void host_thread_ring_state_active(uint32_t thread_index);
void host_thread_ring_state_ready(uint32_t thread_index);
void host_thread_ring_state_exit(uint32_t thread_index);
uint8_t host_thread_ring_phone_connection_state(void);
uint32_t host_thread_ring_phone_role(void);
uint8_t host_thread_ring_remove(void (*callback)(uint32_t));
void host_thread_ring_push(
    void (*callback)(uint32_t), uint32_t argument, uint32_t delay);
uint32_t host_thread_ring_heartbeat(void);
uint32_t host_thread_ring_touch_time(uint16_t ticks);
uint32_t host_thread_ring_touch_enable(uint8_t enabled);
uint32_t host_thread_ring_status(uint8_t bit7, uint8_t bit6);
int32_t host_thread_ring_post_touch(uint8_t event);
int32_t host_thread_ring_glasses_status(void);
uint32_t host_thread_ring_pair_request(void);
void host_thread_ring_owner_callback(uint32_t argument);
void host_thread_ring_touch_error_callback(uint32_t argument);
void host_thread_ring_post_disconnect(void);
void host_thread_ring_parse(const uint8_t *packet, uint16_t length);
void host_thread_ring_exit_wait(void);
void host_thread_ring_reset(void);

#define OPEN_CFW_THREAD_RING_THREAD_ID host_thread_ring_thread_id
#define OPEN_CFW_THREAD_RING_QUEUE_ID host_thread_ring_queue_id
#define OPEN_CFW_THREAD_RING_THREAD_ATTRIBUTES ((const void *)0x75b8a4u)
#define OPEN_CFW_THREAD_RING_THREAD_NEW(entry, argument, attributes) \
    host_thread_ring_thread_new((entry), (argument), (attributes))
#define OPEN_CFW_THREAD_RING_THREAD_TERMINATE(thread_id) \
    host_thread_ring_thread_terminate((thread_id))
#define OPEN_CFW_THREAD_RING_FLAGS_SET(thread_id, flags) \
    host_thread_ring_flags_set((thread_id), (flags))
#define OPEN_CFW_THREAD_RING_FLAGS_WAIT(flags, options, timeout) \
    host_thread_ring_flags_wait((flags), (options), (timeout))
#define OPEN_CFW_THREAD_RING_DELAY(ticks) host_thread_ring_delay((ticks))
#define OPEN_CFW_THREAD_RING_QUEUE_NEW(count, size, attributes) \
    host_thread_ring_queue_new((count), (size), (attributes))
#define OPEN_CFW_THREAD_RING_QUEUE_PUT(queue_id, message, priority, timeout) \
    host_thread_ring_queue_put((queue_id), (message), (priority), (timeout))
#define OPEN_CFW_THREAD_RING_QUEUE_GET(queue_id, message, priority, timeout) \
    host_thread_ring_queue_get((queue_id), (message), (priority), (timeout))
#define OPEN_CFW_THREAD_RING_QUEUE_DELETE(queue_id) \
    host_thread_ring_queue_delete((queue_id))
#define OPEN_CFW_THREAD_RING_ASSERT_FAIL() host_thread_ring_assert_fail()
#define OPEN_CFW_THREAD_RING_ALLOC(size) host_thread_ring_alloc((size))
#define OPEN_CFW_THREAD_RING_FREE(allocation) \
    host_thread_ring_free((allocation))
#define OPEN_CFW_THREAD_RING_STATE_ACTIVE(index) \
    host_thread_ring_state_active((index))
#define OPEN_CFW_THREAD_RING_STATE_READY(index) \
    host_thread_ring_state_ready((index))
#define OPEN_CFW_THREAD_RING_STATE_EXIT(index) \
    host_thread_ring_state_exit((index))
#define OPEN_CFW_THREAD_RING_PHONE_CONNECTION_STATE() \
    host_thread_ring_phone_connection_state()
#define OPEN_CFW_THREAD_RING_PHONE_ROLE() host_thread_ring_phone_role()
#define OPEN_CFW_THREAD_RING_REMOVE(callback) \
    host_thread_ring_remove((callback))
#define OPEN_CFW_THREAD_RING_PUSH(callback, argument, delay) \
    host_thread_ring_push((callback), (argument), (delay))
#define OPEN_CFW_THREAD_RING_ADVERTISING_CALLBACK \
    ((void (*)(uint32_t))(uintptr_t)0x46ee71u)
#define OPEN_CFW_THREAD_RING_DOMINANT_CALLBACK \
    ((void (*)(uint32_t))(uintptr_t)0x4a285du)
#define OPEN_CFW_THREAD_RING_EXIT_WAIT_FOREVER() host_thread_ring_exit_wait()

#define open_cfw_ring_service_heartbeat_process host_thread_ring_heartbeat
#define open_cfw_ring_service_touch_report_time_process \
    host_thread_ring_touch_time
#define open_cfw_ring_service_send_touch_enable host_thread_ring_touch_enable
#define open_cfw_ring_service_send_status_bits host_thread_ring_status
#define open_cfw_ring_service_post_touch_event host_thread_ring_post_touch
#define open_cfw_ring_service_send_glasses_status_event \
    host_thread_ring_glasses_status
#define open_cfw_ring_service_send_pair_request host_thread_ring_pair_request
#define open_cfw_ring_service_owner_connect_callback \
    host_thread_ring_owner_callback
#define open_cfw_ring_service_touch_error_callback \
    host_thread_ring_touch_error_callback
#define open_cfw_ring_service_post_disconnect_event \
    host_thread_ring_post_disconnect
#define open_cfw_ring_service_cmd_package_parse host_thread_ring_parse

#endif

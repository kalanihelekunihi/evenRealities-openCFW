#include <stdlib.h>
#include <string.h>

unsigned int open_cfw_test_ble_msgrx_state_words[4];
unsigned int open_cfw_test_ble_msgrx_events[128];
unsigned int open_cfw_test_ble_msgrx_event_count;
unsigned int open_cfw_test_ble_msgrx_queue_new_result = 1U;
unsigned int open_cfw_test_ble_msgrx_allocate_fail;
unsigned int open_cfw_test_ble_msgrx_queue_put_result;
unsigned int open_cfw_test_ble_msgrx_last_allocation;
unsigned int open_cfw_test_ble_msgrx_last_type;
unsigned int open_cfw_test_ble_msgrx_last_length;
unsigned int open_cfw_test_ble_msgrx_last_timeout;
unsigned int open_cfw_test_ble_msgrx_last_flag;
unsigned char open_cfw_test_ble_msgrx_last_payload[64];

typedef struct {
    unsigned int type;
    unsigned int length;
    unsigned char payload[64];
} test_record;

static test_record *queue_records[32];
static unsigned int queue_head;
static unsigned int queue_tail;

static void event(unsigned int value)
{
    open_cfw_test_ble_msgrx_events[open_cfw_test_ble_msgrx_event_count++] = value;
}

void open_cfw_test_ble_msgrx_reset(void)
{
    unsigned int index;
    for (index = queue_head; index < queue_tail; ++index) {
        free(queue_records[index]);
    }
    memset(open_cfw_test_ble_msgrx_state_words, 0, sizeof(open_cfw_test_ble_msgrx_state_words));
    memset(open_cfw_test_ble_msgrx_events, 0, sizeof(open_cfw_test_ble_msgrx_events));
    memset(open_cfw_test_ble_msgrx_last_payload, 0, sizeof(open_cfw_test_ble_msgrx_last_payload));
    open_cfw_test_ble_msgrx_event_count = 0;
    open_cfw_test_ble_msgrx_queue_new_result = 1;
    open_cfw_test_ble_msgrx_allocate_fail = 0;
    open_cfw_test_ble_msgrx_queue_put_result = 0;
    open_cfw_test_ble_msgrx_last_allocation = 0;
    open_cfw_test_ble_msgrx_last_type = 0;
    open_cfw_test_ble_msgrx_last_length = 0;
    open_cfw_test_ble_msgrx_last_timeout = 0;
    open_cfw_test_ble_msgrx_last_flag = 0;
    queue_head = 0;
    queue_tail = 0;
}

void *open_cfw_test_ble_msgrx_queue_new(unsigned int count, unsigned int size, const void *attributes)
{
    (void)attributes;
    event(0x10000000U | count);
    event(size);
    return (void *)(unsigned long)open_cfw_test_ble_msgrx_queue_new_result;
}

void open_cfw_test_ble_msgrx_failure(void) { event(0xF0000000U); }
void open_cfw_test_ble_msgrx_stage_enter(unsigned int index) { event(0x20000000U | index); }
void open_cfw_test_ble_msgrx_stage_ready(unsigned int index) { event(0x21000000U | index); }

void *open_cfw_test_ble_msgrx_thread_new(void *entry, void *argument, const void *attributes)
{
    (void)entry; (void)argument; (void)attributes;
    event(0x22000000U);
    return (void *)2;
}

void open_cfw_test_ble_msgrx_thread_terminate(void *thread)
{
    event(0x23000000U | (unsigned int)(unsigned long)thread);
}

unsigned int open_cfw_test_ble_msgrx_queue_get(void *queue, void *record, unsigned char *priority, unsigned int timeout)
{
    (void)queue; (void)priority; (void)timeout;
    if (queue_head == queue_tail) return 1;
    *(test_record **)record = queue_records[queue_head++];
    return 0;
}

unsigned int open_cfw_test_ble_msgrx_queue_count(void *queue)
{
    (void)queue;
    return queue_tail - queue_head;
}

unsigned int open_cfw_test_ble_msgrx_queue_capacity(void *queue)
{
    (void)queue;
    return 150;
}

unsigned int open_cfw_test_ble_msgrx_queue_put(void *queue, const void *record, unsigned char priority, unsigned int timeout)
{
    test_record *value = *(test_record *const *)record;
    (void)queue; (void)priority;
    open_cfw_test_ble_msgrx_last_timeout = timeout;
    if (open_cfw_test_ble_msgrx_queue_put_result == 0U) {
        queue_records[queue_tail++] = value;
    }
    return open_cfw_test_ble_msgrx_queue_put_result;
}

unsigned int open_cfw_test_ble_msgrx_flags_set(void *thread, unsigned int flags)
{
    (void)thread;
    open_cfw_test_ble_msgrx_last_flag = flags;
    return flags;
}

void *open_cfw_test_ble_msgrx_allocate(unsigned int size)
{
    open_cfw_test_ble_msgrx_last_allocation = size;
    if (open_cfw_test_ble_msgrx_allocate_fail) return NULL;
    return malloc(size);
}

void open_cfw_test_ble_msgrx_free(void *pointer)
{
    event(0x30000000U);
    free(pointer);
}

void *open_cfw_test_ble_msgrx_memset(void *destination, int value, size_t size)
{
    return memset(destination, value, size);
}

void *open_cfw_test_ble_msgrx_memcpy(void *destination, const void *source, size_t size)
{
    return memcpy(destination, source, size);
}

static void route(unsigned int kind, unsigned int type, const void *payload, unsigned int length)
{
    open_cfw_test_ble_msgrx_last_type = type;
    open_cfw_test_ble_msgrx_last_length = length;
    if (payload && length <= sizeof(open_cfw_test_ble_msgrx_last_payload)) {
        memcpy(open_cfw_test_ble_msgrx_last_payload, payload, length);
    }
    event(kind);
}

void open_cfw_test_ble_msgrx_route_80(const void *payload, unsigned int length) { route(0x80, 0x80, payload, length); }
void open_cfw_test_ble_msgrx_route_c0(unsigned int type, const void *payload, unsigned int length) { route(0xC0, type, payload, length); }
void open_cfw_test_ble_msgrx_route_c4(unsigned int type, const void *payload, unsigned int length) { route(0xC4, type, payload, length); }
void open_cfw_test_ble_msgrx_route_200(unsigned int selector, const void *payload) { route(0x200, selector, payload, 16); }
void open_cfw_test_ble_msgrx_route_400(void) { route(0x400, 0x400, NULL, 0); }
void open_cfw_test_ble_msgrx_hexdump(const void *payload, unsigned int length) { route(0xD00, 0x200, payload, length); }
unsigned int open_cfw_test_ble_msgrx_wait(unsigned int flags, unsigned int options, unsigned int timeout) { (void)flags; (void)options; (void)timeout; return 0; }
int open_cfw_test_ble_msgrx_loop_continue(void) { return 0; }

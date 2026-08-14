#include "openr1_event_bus.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "cmsis_os2.h"
#include "FreeRTOS.h"
#include "task.h"

/* Recovered queue record handed to the stock per-window RTOS queues:
 * {UInt32 event id, UInt32 payload length, 4-byte inline payload or heap
 * pointer} (EVENT-BUS-CORRELATION.md). */
typedef struct {
    uint32_t event_id;
    uint32_t length;
    uint32_t payload;
} openr1_event_bus_record;

/* Local bound, not recovered: the stock queue depths are not pinned.  A
 * full queue is a send failure, never a block. */
#define OPENR1_EVENT_BUS_QUEUE_DEPTH 8u
#define OPENR1_EVENT_BUS_RECORDS_PENDING_FLAG UINT32_C(0x00000001)
#define OPENR1_EVENT_BUS_WINDOW_COUNT 3u

static osMessageQueueId_t window_queues[OPENR1_EVENT_BUS_WINDOW_COUNT];
static osThreadId_t consumer_thread;
static r1_event_bus *platform_bus;
static volatile uint32_t event_bus_last_error;

static StaticTask_t consumer_control_block;
static StackType_t consumer_stack[configMINIMAL_STACK_SIZE];

static void event_bus_record_error(uint32_t error) {
    if (event_bus_last_error == 0u) {
        event_bus_last_error = error;
    }
}

/* Queue-handoff sink bound through r1_event_bus_bind_enqueue.  Payloads up
 * to 4 bytes travel inline in the record; larger payloads take a bounded
 * heap copy (publish caps the length at R1_EVENT_BUS_PAYLOAD_LIMIT) that is
 * freed when the queue send fails, matching the stock flow.  The put uses a
 * zero timeout: the SoftDevice event thread must never block on a full
 * queue, so a full queue fails the handoff (stock 0 return). */
static bool event_bus_queue_sink(
    const r1_event_bus_event *event, void *context) {
    (void)context;
    if (event == NULL || (uint32_t)event->window >=
            OPENR1_EVENT_BUS_WINDOW_COUNT) {
        return false;
    }
    const osMessageQueueId_t queue = window_queues[event->window];
    if (queue == NULL) {
        return false;
    }
    openr1_event_bus_record record = {
        .event_id = event->event_id,
        .length = (uint32_t)event->length,
        .payload = 0u,
    };
    void *heap_copy = NULL;
    if (event->length > R1_EVENT_BUS_INLINE_PAYLOAD_LIMIT) {
        heap_copy = pvPortMalloc(event->length);
        if (heap_copy == NULL) {
            return false;
        }
        memcpy(heap_copy, event->payload, event->length);
        record.payload = (uint32_t)(uintptr_t)heap_copy;
    } else if (event->length > 0u) {
        memcpy(&record.payload, event->payload, event->length);
    }
    if (osMessageQueuePut(queue, &record, 0u, 0u) != osOK) {
        vPortFree(heap_copy);
        return false;
    }
    if (consumer_thread != NULL) {
        (void)osThreadFlagsSet(
            consumer_thread, OPENR1_EVENT_BUS_RECORDS_PENDING_FLAG);
    }
    return true;
}

static void event_bus_deliver(const openr1_event_bus_record *record) {
    const bool heap_payload =
        record->length > R1_EVENT_BUS_INLINE_PAYLOAD_LIMIT;
    /* Defensive bound: the producer caps lengths at
     * R1_EVENT_BUS_PAYLOAD_LIMIT, but the queue record crosses a context
     * boundary, so re-validate before touching the payload. */
    if (record->length > R1_EVENT_BUS_PAYLOAD_LIMIT) {
        if (heap_payload) {
            vPortFree((void *)(uintptr_t)record->payload);
        }
        event_bus_record_error((uint32_t)NRF_ERROR_INVALID_LENGTH);
        return;
    }
    const uint8_t *payload = heap_payload
        ? (const uint8_t *)(uintptr_t)record->payload
        : (const uint8_t *)&record->payload;
    /* Divergence from stock: the consumer-side per-id dispatch table
     * (0x0008D888) and the two-entry cross-context republish routing table
     * are not recovered, so each record is delivered same-context to every
     * populated slot in ascending order.  No production publisher exists
     * yet; a future publisher with class-specific listeners must first
     * recover the id-to-slot mapping. */
    if (platform_bus != NULL) {
        for (uint8_t slot = 0u; slot < R1_EVENT_BUS_SLOT_COUNT; ++slot) {
            if (r1_event_bus_multicast(
                    platform_bus, slot, payload, record->length,
                    NULL) != R1_OK) {
                event_bus_record_error((uint32_t)NRF_ERROR_INTERNAL);
            }
        }
    }
    if (heap_payload) {
        vPortFree((void *)(uintptr_t)record->payload);
    }
}

static void event_bus_consumer(void *context) {
    (void)context;
    for (;;) {
        (void)osThreadFlagsWait(
            OPENR1_EVENT_BUS_RECORDS_PENDING_FLAG, osFlagsWaitAny,
            osWaitForever);
        /* Drain every window: the flag is set after each successful put,
         * so a record queued between the drain and the wait still wakes
         * the thread. */
        for (size_t window = 0u; window < OPENR1_EVENT_BUS_WINDOW_COUNT;
             ++window) {
            openr1_event_bus_record record;
            while (osMessageQueueGet(
                       window_queues[window], &record, NULL, 0u) == osOK) {
                event_bus_deliver(&record);
            }
        }
    }
}

ret_code_t openr1_event_bus_bind(r1_event_bus *bus) {
    static const osThreadAttr_t attributes = {
        .name = "eventbus",
        .cb_mem = &consumer_control_block,
        .cb_size = sizeof consumer_control_block,
        .stack_mem = consumer_stack,
        .stack_size = sizeof consumer_stack,
        .priority = osPriorityLow,
    };
    if (bus == NULL) {
        return NRF_ERROR_NULL;
    }
    if (platform_bus != NULL) {
        return platform_bus == bus ? NRF_SUCCESS : NRF_ERROR_INVALID_STATE;
    }
    for (size_t window = 0u; window < OPENR1_EVENT_BUS_WINDOW_COUNT;
         ++window) {
        window_queues[window] = osMessageQueueNew(
            OPENR1_EVENT_BUS_QUEUE_DEPTH, sizeof(openr1_event_bus_record),
            NULL);
        if (window_queues[window] == NULL) {
            return NRF_ERROR_NO_MEM;
        }
    }
    platform_bus = bus;
    consumer_thread = osThreadNew(event_bus_consumer, NULL, &attributes);
    if (consumer_thread == NULL) {
        platform_bus = NULL;
        return NRF_ERROR_NO_MEM;
    }
    if (r1_event_bus_bind_enqueue(bus, event_bus_queue_sink, NULL) !=
        R1_OK) {
        platform_bus = NULL;
        return NRF_ERROR_INTERNAL;
    }
    return NRF_SUCCESS;
}

uint32_t openr1_event_bus_last_error(void) {
    return event_bus_last_error;
}

unsigned char open_cfw_test_event_service_busy;
unsigned char open_cfw_test_event_service_ring_mode;
unsigned char open_cfw_test_event_service_destination[64];
unsigned char open_cfw_test_event_service_ring[16];
unsigned int open_cfw_test_event_service_total;
unsigned int open_cfw_test_event_service_offset;
unsigned int open_cfw_test_event_service_ring_available;
unsigned int open_cfw_test_event_service_progress_word;
volatile unsigned int *open_cfw_test_event_service_progress;
void (*open_cfw_test_event_service_callback)(
    unsigned int result,
    void *context
);
void *open_cfw_test_event_service_context;

unsigned int open_cfw_test_event_service_interrupt_mask;
unsigned int open_cfw_test_event_service_enter_count;
unsigned int open_cfw_test_event_service_exit_count;
unsigned int open_cfw_test_event_service_exit_mask;

unsigned int open_cfw_test_event_service_ring_fill_count;
void *open_cfw_test_event_service_ring_fill_handle;

unsigned int open_cfw_test_event_service_direct_count;
unsigned int open_cfw_test_event_service_direct_result;
unsigned int open_cfw_test_event_service_direct_transferred;
void *open_cfw_test_event_service_direct_handle;
void *open_cfw_test_event_service_direct_destination;
unsigned int open_cfw_test_event_service_direct_requested;

unsigned int open_cfw_test_event_service_ring_read_count;
unsigned int open_cfw_test_event_service_ring_read_result;
void *open_cfw_test_event_service_ring_pointer;
void *open_cfw_test_event_service_ring_destination;
unsigned int open_cfw_test_event_service_ring_requested;

unsigned int open_cfw_test_event_service_callback_count;
unsigned int open_cfw_test_event_service_callback_result;
void *open_cfw_test_event_service_callback_context;
unsigned int open_cfw_test_event_service_callback_exit_count;

unsigned int open_cfw_test_event_service_trace[16];
unsigned int open_cfw_test_event_service_trace_count;

static void open_cfw_test_event_service_trace_add(unsigned int event)
{
    open_cfw_test_event_service_trace[
        open_cfw_test_event_service_trace_count++
    ] = event;
}

void open_cfw_test_event_service_callback_impl(
    unsigned int result,
    void *context
)
{
    open_cfw_test_event_service_trace_add(6U);
    ++open_cfw_test_event_service_callback_count;
    open_cfw_test_event_service_callback_result = result;
    open_cfw_test_event_service_callback_context = context;
    open_cfw_test_event_service_callback_exit_count =
        open_cfw_test_event_service_exit_count;
}

void open_cfw_test_event_service_reset(void)
{
    unsigned int index;

    open_cfw_test_event_service_busy = 1U;
    open_cfw_test_event_service_ring_mode = 0U;
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_event_service_destination[index] = 0xA5U;
    }
    open_cfw_test_event_service_total = 12U;
    open_cfw_test_event_service_offset = 0U;
    open_cfw_test_event_service_ring_available = 8U;
    open_cfw_test_event_service_progress_word = 0xA5A5A5A5U;
    open_cfw_test_event_service_progress =
        &open_cfw_test_event_service_progress_word;
    open_cfw_test_event_service_callback =
        open_cfw_test_event_service_callback_impl;
    open_cfw_test_event_service_context =
        (void *)open_cfw_test_event_service_ring;

    open_cfw_test_event_service_interrupt_mask = 0U;
    open_cfw_test_event_service_enter_count = 0U;
    open_cfw_test_event_service_exit_count = 0U;
    open_cfw_test_event_service_exit_mask = 0xFFFFFFFFU;

    open_cfw_test_event_service_ring_fill_count = 0U;
    open_cfw_test_event_service_ring_fill_handle = (void *)0;

    open_cfw_test_event_service_direct_count = 0U;
    open_cfw_test_event_service_direct_result = 0U;
    open_cfw_test_event_service_direct_transferred = 4U;
    open_cfw_test_event_service_direct_handle = (void *)0;
    open_cfw_test_event_service_direct_destination = (void *)0;
    open_cfw_test_event_service_direct_requested = 0U;

    open_cfw_test_event_service_ring_read_count = 0U;
    open_cfw_test_event_service_ring_read_result = 1U;
    open_cfw_test_event_service_ring_pointer = (void *)0;
    open_cfw_test_event_service_ring_destination = (void *)0;
    open_cfw_test_event_service_ring_requested = 0U;

    open_cfw_test_event_service_callback_count = 0U;
    open_cfw_test_event_service_callback_result = 0xFFFFFFFFU;
    open_cfw_test_event_service_callback_context = (void *)0;
    open_cfw_test_event_service_callback_exit_count = 0xFFFFFFFFU;

    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_event_service_trace[index] = 0U;
    }
    open_cfw_test_event_service_trace_count = 0U;
}

unsigned int open_cfw_test_event_service_critical_enter(void)
{
    open_cfw_test_event_service_trace_add(2U);
    ++open_cfw_test_event_service_enter_count;
    return open_cfw_test_event_service_interrupt_mask;
}

void open_cfw_test_event_service_critical_exit(unsigned int interrupt_mask)
{
    open_cfw_test_event_service_trace_add(5U);
    ++open_cfw_test_event_service_exit_count;
    open_cfw_test_event_service_exit_mask = interrupt_mask;
}

void open_cfw_test_event_service_ring_fill(void *handle)
{
    open_cfw_test_event_service_trace_add(1U);
    ++open_cfw_test_event_service_ring_fill_count;
    open_cfw_test_event_service_ring_fill_handle = handle;
}

unsigned int open_cfw_test_event_service_direct_read(
    void *handle,
    void *destination,
    unsigned int count,
    unsigned int *read_count
)
{
    open_cfw_test_event_service_trace_add(3U);
    ++open_cfw_test_event_service_direct_count;
    open_cfw_test_event_service_direct_handle = handle;
    open_cfw_test_event_service_direct_destination = destination;
    open_cfw_test_event_service_direct_requested = count;
    *read_count = open_cfw_test_event_service_direct_transferred;
    return open_cfw_test_event_service_direct_result;
}

unsigned int open_cfw_test_event_service_ring_read(
    void *ring,
    void *destination,
    unsigned int count
)
{
    open_cfw_test_event_service_trace_add(4U);
    ++open_cfw_test_event_service_ring_read_count;
    open_cfw_test_event_service_ring_pointer = ring;
    open_cfw_test_event_service_ring_destination = destination;
    open_cfw_test_event_service_ring_requested = count;
    return open_cfw_test_event_service_ring_read_result;
}

#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_ENTER() \
    open_cfw_test_event_service_critical_enter()
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_test_event_service_critical_exit(interrupt_mask)
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_BUSY(handle) \
    open_cfw_test_event_service_busy
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DESTINATION(handle) \
    open_cfw_test_event_service_destination
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_TOTAL(handle) \
    open_cfw_test_event_service_total
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_PROGRESS_POINTER(handle) \
    open_cfw_test_event_service_progress
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK(handle) \
    open_cfw_test_event_service_callback
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_CALLBACK_CONTEXT(handle) \
    open_cfw_test_event_service_context
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_OFFSET(handle) \
    open_cfw_test_event_service_offset
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_MODE(handle) \
    open_cfw_test_event_service_ring_mode
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_AVAILABLE(handle) \
    open_cfw_test_event_service_ring_available
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING(handle) \
    ((void *)open_cfw_test_event_service_ring)
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_FILL(handle) \
    open_cfw_test_event_service_ring_fill(handle)
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_DIRECT_READ( \
    handle, \
    destination, \
    count, \
    read_count \
) \
    open_cfw_test_event_service_direct_read( \
        (handle), \
        (destination), \
        (count), \
        (read_count) \
    )
#define OPEN_CFW_UI_DISPLAY_EVENT_SERVICE_RING_READ( \
    ring, \
    destination, \
    count \
) \
    open_cfw_test_event_service_ring_read( \
        (ring), \
        (destination), \
        (count) \
    )

#include "../../components/apollo_main/core_overlay/ui_display_event_service.c"

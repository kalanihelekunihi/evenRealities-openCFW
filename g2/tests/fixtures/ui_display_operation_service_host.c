unsigned char open_cfw_test_operation_service_busy;
unsigned char open_cfw_test_operation_service_ring_mode;
unsigned char open_cfw_test_operation_service_source[64];
unsigned char open_cfw_test_operation_service_ring[16];
unsigned int open_cfw_test_operation_service_total;
unsigned int open_cfw_test_operation_service_offset;
unsigned int open_cfw_test_operation_service_consumer;
unsigned int open_cfw_test_operation_service_producer;
unsigned int open_cfw_test_operation_service_progress_word;
volatile unsigned int *open_cfw_test_operation_service_progress;
void (*open_cfw_test_operation_service_callback)(
    unsigned int result,
    void *context
);
void *open_cfw_test_operation_service_context;

unsigned int open_cfw_test_operation_service_interrupt_mask;
unsigned int open_cfw_test_operation_service_enter_count;
unsigned int open_cfw_test_operation_service_exit_count;
unsigned int open_cfw_test_operation_service_exit_mask;

unsigned int open_cfw_test_operation_service_direct_count;
unsigned int open_cfw_test_operation_service_direct_result;
unsigned int open_cfw_test_operation_service_direct_written;
void *open_cfw_test_operation_service_direct_handle;
const void *open_cfw_test_operation_service_direct_source;
unsigned int open_cfw_test_operation_service_direct_requested;

unsigned int open_cfw_test_operation_service_ring_write_count;
unsigned int open_cfw_test_operation_service_ring_write_result;
void *open_cfw_test_operation_service_ring_pointer;
const void *open_cfw_test_operation_service_ring_source;
unsigned int open_cfw_test_operation_service_ring_requested;

unsigned int open_cfw_test_operation_service_ring_service_count;
void *open_cfw_test_operation_service_ring_service_handle;
unsigned int open_cfw_test_operation_service_ring_service_exit_count;

unsigned int open_cfw_test_operation_service_callback_count;
unsigned int open_cfw_test_operation_service_callback_result;
void *open_cfw_test_operation_service_callback_context;
unsigned int open_cfw_test_operation_service_callback_exit_count;

void open_cfw_test_operation_service_callback_impl(
    unsigned int result,
    void *context
)
{
    ++open_cfw_test_operation_service_callback_count;
    open_cfw_test_operation_service_callback_result = result;
    open_cfw_test_operation_service_callback_context = context;
    open_cfw_test_operation_service_callback_exit_count =
        open_cfw_test_operation_service_exit_count;
}

void open_cfw_test_operation_service_reset(void)
{
    unsigned int index;

    open_cfw_test_operation_service_busy = 1U;
    open_cfw_test_operation_service_ring_mode = 0U;
    for (index = 0U; index < 64U; ++index) {
        open_cfw_test_operation_service_source[index] =
            (unsigned char)(index + 1U);
    }
    open_cfw_test_operation_service_total = 12U;
    open_cfw_test_operation_service_offset = 0U;
    open_cfw_test_operation_service_consumer = 0U;
    open_cfw_test_operation_service_producer = 8U;
    open_cfw_test_operation_service_progress_word = 0xA5A5A5A5U;
    open_cfw_test_operation_service_progress =
        &open_cfw_test_operation_service_progress_word;
    open_cfw_test_operation_service_callback =
        open_cfw_test_operation_service_callback_impl;
    open_cfw_test_operation_service_context =
        (void *)open_cfw_test_operation_service_ring;

    open_cfw_test_operation_service_interrupt_mask = 0U;
    open_cfw_test_operation_service_enter_count = 0U;
    open_cfw_test_operation_service_exit_count = 0U;
    open_cfw_test_operation_service_exit_mask = 0xFFFFFFFFU;

    open_cfw_test_operation_service_direct_count = 0U;
    open_cfw_test_operation_service_direct_result = 0U;
    open_cfw_test_operation_service_direct_written = 4U;
    open_cfw_test_operation_service_direct_handle = (void *)0;
    open_cfw_test_operation_service_direct_source = (const void *)0;
    open_cfw_test_operation_service_direct_requested = 0U;

    open_cfw_test_operation_service_ring_write_count = 0U;
    open_cfw_test_operation_service_ring_write_result = 7U;
    open_cfw_test_operation_service_ring_pointer = (void *)0;
    open_cfw_test_operation_service_ring_source = (const void *)0;
    open_cfw_test_operation_service_ring_requested = 0U;

    open_cfw_test_operation_service_ring_service_count = 0U;
    open_cfw_test_operation_service_ring_service_handle = (void *)0;
    open_cfw_test_operation_service_ring_service_exit_count = 0U;

    open_cfw_test_operation_service_callback_count = 0U;
    open_cfw_test_operation_service_callback_result = 0xFFFFFFFFU;
    open_cfw_test_operation_service_callback_context = (void *)0;
    open_cfw_test_operation_service_callback_exit_count = 0xFFFFFFFFU;
}

unsigned int open_cfw_test_operation_service_critical_enter(void)
{
    ++open_cfw_test_operation_service_enter_count;
    return open_cfw_test_operation_service_interrupt_mask;
}

void open_cfw_test_operation_service_critical_exit(
    unsigned int interrupt_mask
)
{
    ++open_cfw_test_operation_service_exit_count;
    open_cfw_test_operation_service_exit_mask = interrupt_mask;
}

unsigned int open_cfw_test_operation_service_direct_write(
    void *handle,
    const void *source,
    unsigned int count,
    unsigned int *written
)
{
    ++open_cfw_test_operation_service_direct_count;
    open_cfw_test_operation_service_direct_handle = handle;
    open_cfw_test_operation_service_direct_source = source;
    open_cfw_test_operation_service_direct_requested = count;
    *written = open_cfw_test_operation_service_direct_written;
    return open_cfw_test_operation_service_direct_result;
}

unsigned int open_cfw_test_operation_service_ring_write(
    void *ring,
    const void *source,
    unsigned int count
)
{
    ++open_cfw_test_operation_service_ring_write_count;
    open_cfw_test_operation_service_ring_pointer = ring;
    open_cfw_test_operation_service_ring_source = source;
    open_cfw_test_operation_service_ring_requested = count;
    return open_cfw_test_operation_service_ring_write_result;
}

void open_cfw_test_operation_service_ring_service(void *handle)
{
    ++open_cfw_test_operation_service_ring_service_count;
    open_cfw_test_operation_service_ring_service_handle = handle;
    open_cfw_test_operation_service_ring_service_exit_count =
        open_cfw_test_operation_service_exit_count;
}

#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_ENTER() \
    open_cfw_test_operation_service_critical_enter()
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_test_operation_service_critical_exit(interrupt_mask)
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_BUSY(handle) \
    open_cfw_test_operation_service_busy
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_SOURCE(handle) \
    open_cfw_test_operation_service_source
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_TOTAL(handle) \
    open_cfw_test_operation_service_total
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_PROGRESS_POINTER(handle) \
    open_cfw_test_operation_service_progress
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK(handle) \
    open_cfw_test_operation_service_callback
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_CALLBACK_CONTEXT(handle) \
    open_cfw_test_operation_service_context
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_OFFSET(handle) \
    open_cfw_test_operation_service_offset
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_MODE(handle) \
    open_cfw_test_operation_service_ring_mode
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_AVAILABLE(handle) \
    ( \
        open_cfw_test_operation_service_producer \
        - open_cfw_test_operation_service_consumer \
    )
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_DIRECT_WRITE( \
    handle, \
    source, \
    count, \
    written \
) \
    open_cfw_test_operation_service_direct_write( \
        (handle), \
        (source), \
        (count), \
        (written) \
    )
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_WRITE( \
    ring, \
    source, \
    count \
) \
    open_cfw_test_operation_service_ring_write( \
        (ring), \
        (source), \
        (count) \
    )
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING(handle) \
    ((void *)open_cfw_test_operation_service_ring)
#define OPEN_CFW_UI_DISPLAY_OPERATION_SERVICE_RING_SERVICE(handle) \
    open_cfw_test_operation_service_ring_service(handle)

#include "../../components/apollo_main/core_overlay/ui_display_operation_service.c"

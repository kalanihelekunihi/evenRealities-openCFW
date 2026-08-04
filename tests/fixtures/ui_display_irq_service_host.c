unsigned int open_cfw_test_irq_signature;
unsigned int open_cfw_test_irq_instance;
unsigned char open_cfw_test_irq_special;
unsigned char open_cfw_test_irq_normal_flag;
unsigned int open_cfw_test_irq_progress_base;
unsigned int open_cfw_test_irq_progress_word;
volatile unsigned int *open_cfw_test_irq_progress;
void (*open_cfw_test_irq_callback)(unsigned int result, void *context);
void *open_cfw_test_irq_context;
unsigned int open_cfw_test_irq_fifo_position;
unsigned int open_cfw_test_irq_callback_result;

unsigned int open_cfw_test_irq_event_count;
unsigned int open_cfw_test_irq_operation_count;
unsigned int open_cfw_test_irq_bit6_count;
unsigned int open_cfw_test_irq_bit12_count;
unsigned int open_cfw_test_irq_finish_count;
unsigned int open_cfw_test_irq_result_count;
unsigned int open_cfw_test_irq_callback_count;
unsigned int open_cfw_test_irq_callback_value;
void *open_cfw_test_irq_callback_context;
void *open_cfw_test_irq_last_handle;
unsigned int open_cfw_test_irq_result_instance;
unsigned int open_cfw_test_irq_result_status;
unsigned int open_cfw_test_irq_fifo_instance;
unsigned int open_cfw_test_irq_trace[16];
unsigned int open_cfw_test_irq_trace_count;

static void open_cfw_test_irq_trace_add(unsigned int event)
{
    open_cfw_test_irq_trace[open_cfw_test_irq_trace_count++] = event;
}

void open_cfw_test_irq_callback_impl(
    unsigned int result,
    void *context
)
{
    open_cfw_test_irq_trace_add(7U);
    ++open_cfw_test_irq_callback_count;
    open_cfw_test_irq_callback_value = result;
    open_cfw_test_irq_callback_context = context;
}

void open_cfw_test_irq_reset(void)
{
    unsigned int index;

    open_cfw_test_irq_signature = 0x01EA9E06U;
    open_cfw_test_irq_instance = 3U;
    open_cfw_test_irq_special = 0U;
    open_cfw_test_irq_normal_flag = 0U;
    open_cfw_test_irq_progress_base = 0x1234U;
    open_cfw_test_irq_progress_word = 0xA5A5A5A5U;
    open_cfw_test_irq_progress = &open_cfw_test_irq_progress_word;
    open_cfw_test_irq_callback = open_cfw_test_irq_callback_impl;
    open_cfw_test_irq_context = (void *)&open_cfw_test_irq_progress_word;
    open_cfw_test_irq_fifo_position = 0x234U;
    open_cfw_test_irq_callback_result = 0x55667788U;

    open_cfw_test_irq_event_count = 0U;
    open_cfw_test_irq_operation_count = 0U;
    open_cfw_test_irq_bit6_count = 0U;
    open_cfw_test_irq_bit12_count = 0U;
    open_cfw_test_irq_finish_count = 0U;
    open_cfw_test_irq_result_count = 0U;
    open_cfw_test_irq_callback_count = 0U;
    open_cfw_test_irq_callback_value = 0U;
    open_cfw_test_irq_callback_context = (void *)0;
    open_cfw_test_irq_last_handle = (void *)0;
    open_cfw_test_irq_result_instance = 0U;
    open_cfw_test_irq_result_status = 0U;
    open_cfw_test_irq_fifo_instance = 0U;
    open_cfw_test_irq_trace_count = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_irq_trace[index] = 0U;
    }
}

void open_cfw_test_irq_event_service(void *handle)
{
    open_cfw_test_irq_trace_add(1U);
    ++open_cfw_test_irq_event_count;
    open_cfw_test_irq_last_handle = handle;
}

void open_cfw_test_irq_operation_service(void *handle)
{
    open_cfw_test_irq_trace_add(2U);
    ++open_cfw_test_irq_operation_count;
    open_cfw_test_irq_last_handle = handle;
}

void open_cfw_test_irq_bit6(void *handle)
{
    open_cfw_test_irq_trace_add(4U);
    ++open_cfw_test_irq_bit6_count;
    open_cfw_test_irq_last_handle = handle;
}

void open_cfw_test_irq_bit12(void *handle)
{
    open_cfw_test_irq_trace_add(5U);
    ++open_cfw_test_irq_bit12_count;
    open_cfw_test_irq_last_handle = handle;
}

unsigned int open_cfw_test_irq_result(
    unsigned int instance,
    unsigned int status
)
{
    open_cfw_test_irq_trace_add(6U);
    ++open_cfw_test_irq_result_count;
    open_cfw_test_irq_result_instance = instance;
    open_cfw_test_irq_result_status = status;
    return open_cfw_test_irq_callback_result;
}

void open_cfw_test_irq_finish(void *handle)
{
    open_cfw_test_irq_trace_add(8U);
    ++open_cfw_test_irq_finish_count;
    open_cfw_test_irq_last_handle = handle;
}

unsigned int open_cfw_test_irq_fifo(unsigned int instance)
{
    open_cfw_test_irq_trace_add(3U);
    open_cfw_test_irq_fifo_instance = instance;
    return open_cfw_test_irq_fifo_position;
}

#define OPEN_CFW_UI_DISPLAY_IRQ_SIGNATURE(handle) \
    open_cfw_test_irq_signature
#define OPEN_CFW_UI_DISPLAY_IRQ_INSTANCE(handle) \
    open_cfw_test_irq_instance
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL(handle) \
    open_cfw_test_irq_special
#define OPEN_CFW_UI_DISPLAY_IRQ_NORMAL_FLAG(handle) \
    open_cfw_test_irq_normal_flag
#define OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_BASE(handle) \
    open_cfw_test_irq_progress_base
#define OPEN_CFW_UI_DISPLAY_IRQ_PROGRESS_POINTER(handle) \
    open_cfw_test_irq_progress
#define OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK(handle) \
    open_cfw_test_irq_callback
#define OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_CONTEXT(handle) \
    open_cfw_test_irq_context
#define OPEN_CFW_UI_DISPLAY_IRQ_FIFO_POSITION(instance) \
    open_cfw_test_irq_fifo(instance)
#define OPEN_CFW_UI_DISPLAY_IRQ_EVENT_SERVICE(handle) \
    open_cfw_test_irq_event_service(handle)
#define OPEN_CFW_UI_DISPLAY_IRQ_OPERATION_SERVICE(handle) \
    open_cfw_test_irq_operation_service(handle)
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT6(handle) \
    open_cfw_test_irq_bit6(handle)
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_BIT12(handle) \
    open_cfw_test_irq_bit12(handle)
#define OPEN_CFW_UI_DISPLAY_IRQ_CALLBACK_RESULT(instance, status) \
    open_cfw_test_irq_result((instance), (status))
#define OPEN_CFW_UI_DISPLAY_IRQ_SPECIAL_FINISH(handle) \
    open_cfw_test_irq_finish(handle)

#include "../../components/apollo_main/core_overlay/ui_display_irq_service.c"

unsigned int open_cfw_test_irq_helpers_instance;
unsigned int open_cfw_test_irq_helpers_clock;
unsigned char open_cfw_test_irq_helpers_special;
unsigned int open_cfw_test_irq_helpers_mmio[4][24];
unsigned int open_cfw_test_irq_helpers_delay_count;
unsigned int open_cfw_test_irq_helpers_delay_ticks;
unsigned int open_cfw_test_irq_helpers_discard_count;
unsigned int open_cfw_test_irq_helpers_abort_count;
void *open_cfw_test_irq_helpers_last_handle;
unsigned int open_cfw_test_irq_helpers_trace[8];
unsigned int open_cfw_test_irq_helpers_trace_count;

static void open_cfw_test_irq_helpers_trace_add(unsigned int event)
{
    open_cfw_test_irq_helpers_trace[
        open_cfw_test_irq_helpers_trace_count++
    ] = event;
}

void open_cfw_test_irq_helpers_reset(void)
{
    unsigned int instance;
    unsigned int word;

    open_cfw_test_irq_helpers_instance = 2U;
    open_cfw_test_irq_helpers_clock = 10U;
    open_cfw_test_irq_helpers_special = 0U;
    for (instance = 0U; instance < 4U; ++instance) {
        for (word = 0U; word < 24U; ++word) {
            open_cfw_test_irq_helpers_mmio[instance][word] =
                0xA5A5A5A5U;
        }
    }
    open_cfw_test_irq_helpers_delay_count = 0U;
    open_cfw_test_irq_helpers_delay_ticks = 0U;
    open_cfw_test_irq_helpers_discard_count = 0U;
    open_cfw_test_irq_helpers_abort_count = 0U;
    open_cfw_test_irq_helpers_last_handle = (void *)0;
    open_cfw_test_irq_helpers_trace_count = 0U;
    for (word = 0U; word < 8U; ++word) {
        open_cfw_test_irq_helpers_trace[word] = 0U;
    }
}

void open_cfw_test_irq_helpers_delay(unsigned int ticks)
{
    open_cfw_test_irq_helpers_trace_add(1U);
    ++open_cfw_test_irq_helpers_delay_count;
    open_cfw_test_irq_helpers_delay_ticks = ticks;
}

void open_cfw_test_irq_helpers_discard(void *handle)
{
    open_cfw_test_irq_helpers_trace_add(2U);
    ++open_cfw_test_irq_helpers_discard_count;
    open_cfw_test_irq_helpers_last_handle = handle;
}

void open_cfw_test_irq_helpers_abort(void *handle)
{
    open_cfw_test_irq_helpers_trace_add(3U);
    ++open_cfw_test_irq_helpers_abort_count;
    open_cfw_test_irq_helpers_last_handle = handle;
}

#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_INSTANCE(handle) \
    ((void)(handle), open_cfw_test_irq_helpers_instance)
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_MMIO_WORD(instance, offset) \
    open_cfw_test_irq_helpers_mmio[(instance)][(offset) / 4U]
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_CLOCK(handle) \
    ((void)(handle), open_cfw_test_irq_helpers_clock)
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_SPECIAL(handle) \
    ((void)(handle), open_cfw_test_irq_helpers_special)
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_DELAY(ticks) \
    open_cfw_test_irq_helpers_delay(ticks)
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_FIFO_DISCARD(handle) \
    open_cfw_test_irq_helpers_discard(handle)
#define OPEN_CFW_UI_DISPLAY_IRQ_HELPER_EVENT_ABORT(handle) \
    open_cfw_test_irq_helpers_abort(handle)

#include "../../components/apollo_main/core_overlay/ui_display_irq_helpers.c"

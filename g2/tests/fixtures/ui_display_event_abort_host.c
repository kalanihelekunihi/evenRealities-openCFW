unsigned int open_cfw_test_event_abort_interrupt_mask;
unsigned int open_cfw_test_event_abort_enter_count;
unsigned int open_cfw_test_event_abort_exit_count;
unsigned int open_cfw_test_event_abort_exit_mask;

void open_cfw_test_event_abort_reset(void)
{
    open_cfw_test_event_abort_interrupt_mask = 0U;
    open_cfw_test_event_abort_enter_count = 0U;
    open_cfw_test_event_abort_exit_count = 0U;
    open_cfw_test_event_abort_exit_mask = 0xFFFFFFFFU;
}

unsigned int open_cfw_test_event_abort_critical_enter(void)
{
    ++open_cfw_test_event_abort_enter_count;
    return open_cfw_test_event_abort_interrupt_mask;
}

void open_cfw_test_event_abort_critical_exit(unsigned int interrupt_mask)
{
    ++open_cfw_test_event_abort_exit_count;
    open_cfw_test_event_abort_exit_mask = interrupt_mask;
}

#define OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_ENTER() \
    open_cfw_test_event_abort_critical_enter()
#define OPEN_CFW_UI_DISPLAY_EVENT_ABORT_CRITICAL_EXIT(interrupt_mask) \
    open_cfw_test_event_abort_critical_exit(interrupt_mask)

#include "../../components/apollo_main/core_overlay/ui_display_event_abort.c"

void *open_cfw_test_callback_context;
unsigned int open_cfw_test_first_count;
unsigned int open_cfw_test_second_count;

void (*open_cfw_test_callback_target)(void *context);

void open_cfw_test_first_target(void *context)
{
    ++open_cfw_test_first_count;
    open_cfw_test_callback_context = context;
}

void open_cfw_test_second_target(void *context)
{
    ++open_cfw_test_second_count;
    open_cfw_test_callback_context = context;
}

void open_cfw_test_callback_reset(void)
{
    open_cfw_test_callback_context = (void *)0;
    open_cfw_test_first_count = 0U;
    open_cfw_test_second_count = 0U;
    open_cfw_test_callback_target = open_cfw_test_first_target;
}

unsigned long open_cfw_test_first_target_address(void)
{
    return (unsigned long)open_cfw_test_first_target;
}

unsigned long open_cfw_test_second_target_address(void)
{
    return (unsigned long)open_cfw_test_second_target;
}

#define OPEN_CFW_UI_DISPLAY_CALLBACK_TARGET \
    open_cfw_test_callback_target
#define OPEN_CFW_UI_DISPLAY_HANDLER_SINK(selector, buffer, length) \
    ((void)(selector), (void)(buffer), (void)(length))

#include "../../components/apollo_main/core_overlay/runtime_string.c"
#include "../../components/apollo_main/core_overlay/ui_display_callback.c"

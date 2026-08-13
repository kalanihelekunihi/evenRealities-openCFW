unsigned char open_cfw_test_input_record[20];
unsigned int open_cfw_test_order_count;
unsigned int open_cfw_test_order[24];
void *open_cfw_test_bound_callback;
void *open_cfw_test_reset_record;
unsigned int open_cfw_test_configure_selector;
void *open_cfw_test_configure_record;
unsigned int open_cfw_test_transition_zero_value;
unsigned int open_cfw_test_transition_one_value;
unsigned int open_cfw_test_event_service;
unsigned int open_cfw_test_event_value;
unsigned int open_cfw_test_publish_service;
unsigned int open_cfw_test_active_value;
unsigned int open_cfw_test_callback_count;
void (*open_cfw_test_display_target)(void *context);

void open_cfw_test_display_target_impl(void *context);

static void open_cfw_test_zero(
    void *destination,
    unsigned int length
)
{
    unsigned char *bytes = (unsigned char *)destination;
    unsigned int index;

    for (index = 0U; index < length; ++index) {
        bytes[index] = 0U;
    }
}

static void open_cfw_test_record_order(unsigned int value)
{
    open_cfw_test_order[open_cfw_test_order_count++] = value;
}

void open_cfw_test_reset(void)
{
    open_cfw_test_zero(
        open_cfw_test_input_record,
        sizeof(open_cfw_test_input_record)
    );
    open_cfw_test_zero(open_cfw_test_order, sizeof(open_cfw_test_order));
    open_cfw_test_order_count = 0U;
    open_cfw_test_bound_callback = (void *)0;
    open_cfw_test_reset_record = (void *)0;
    open_cfw_test_configure_selector = 0xFFFFFFFFU;
    open_cfw_test_configure_record = (void *)0;
    open_cfw_test_transition_zero_value = 0xFFFFFFFFU;
    open_cfw_test_transition_one_value = 0xFFFFFFFFU;
    open_cfw_test_event_service = 0U;
    open_cfw_test_event_value = 0U;
    open_cfw_test_publish_service = 0U;
    open_cfw_test_active_value = 0xFFFFFFFFU;
    open_cfw_test_callback_count = 0U;
    open_cfw_test_display_target = open_cfw_test_display_target_impl;
}

void open_cfw_test_display_target_impl(void *context)
{
    (void)context;
    ++open_cfw_test_callback_count;
}

void open_cfw_test_display_runtime_begin(void)
{
    open_cfw_test_record_order(1U);
}

void open_cfw_test_display_bind(
    void (*callback)(void *unused, void *context)
)
{
    open_cfw_test_record_order(2U);
    open_cfw_test_bound_callback = (void *)callback;
}

void open_cfw_test_display_runtime_commit(void)
{
    open_cfw_test_record_order(3U);
}

void open_cfw_test_input_record_reset(void *record)
{
    unsigned int index;

    open_cfw_test_record_order(10U);
    open_cfw_test_reset_record = record;
    for (index = 0U; index < 20U; ++index) {
        ((unsigned char *)record)[index] = 0xA5U;
    }
}

void open_cfw_test_input_record_configure(
    unsigned int selector,
    void *record
)
{
    open_cfw_test_record_order(11U);
    open_cfw_test_configure_selector = selector;
    open_cfw_test_configure_record = record;
}

void open_cfw_test_input_transition_zero(unsigned int value)
{
    open_cfw_test_record_order(12U);
    open_cfw_test_transition_zero_value = value;
}

void open_cfw_test_input_transition_one(unsigned int value)
{
    open_cfw_test_record_order(13U);
    open_cfw_test_transition_one_value = value;
}

void open_cfw_test_input_post_event(
    unsigned int service,
    unsigned int event
)
{
    open_cfw_test_record_order(14U);
    open_cfw_test_event_service = service;
    open_cfw_test_event_value = event;
}

void open_cfw_test_input_publish(unsigned int service)
{
    open_cfw_test_record_order(15U);
    open_cfw_test_publish_service = service;
}

void open_cfw_test_input_runtime_commit(void)
{
    open_cfw_test_record_order(16U);
}

void open_cfw_test_input_set_active(unsigned int value)
{
    open_cfw_test_record_order(17U);
    open_cfw_test_active_value = value;
}

#define OPEN_CFW_UI_DISPLAY_CALLBACK_TARGET open_cfw_test_display_target
#define OPEN_CFW_UI_DISPLAY_HANDLER_SINK(selector, buffer, length) \
    ((void)(selector), (void)(buffer), (void)(length))
#include "../../components/apollo_main/core_overlay/runtime_string.c"
#include "../../components/apollo_main/core_overlay/ui_display_callback.c"

unsigned long open_cfw_test_display_callback_address(void)
{
    return (unsigned long)open_cfw_ui_display_callback;
}

#define OPEN_CFW_UI_SETUP_INPUT_RECORD open_cfw_test_input_record
#define OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_BEGIN() \
    open_cfw_test_display_runtime_begin()
#define OPEN_CFW_UI_SETUP_DISPLAY_BIND(callback) \
    open_cfw_test_display_bind(callback)
#define OPEN_CFW_UI_SETUP_DISPLAY_RUNTIME_COMMIT() \
    open_cfw_test_display_runtime_commit()
#define OPEN_CFW_UI_SETUP_INPUT_RECORD_RESET(record) \
    open_cfw_test_input_record_reset((void *)(record))
#define OPEN_CFW_UI_SETUP_INPUT_RECORD_CONFIGURE(selector, record) \
    open_cfw_test_input_record_configure((selector), (void *)(record))
#define OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ZERO(value) \
    open_cfw_test_input_transition_zero(value)
#define OPEN_CFW_UI_SETUP_INPUT_TRANSITION_ONE(value) \
    open_cfw_test_input_transition_one(value)
#define OPEN_CFW_UI_SETUP_INPUT_POST_EVENT(service, event) \
    open_cfw_test_input_post_event((service), (event))
#define OPEN_CFW_UI_SETUP_INPUT_PUBLISH(service) \
    open_cfw_test_input_publish(service)
#define OPEN_CFW_UI_SETUP_INPUT_RUNTIME_COMMIT() \
    open_cfw_test_input_runtime_commit()
#define OPEN_CFW_UI_SETUP_INPUT_SET_ACTIVE(value) \
    open_cfw_test_input_set_active(value)

#include "../../components/apollo_main/core_overlay/ui_display_setup.c"

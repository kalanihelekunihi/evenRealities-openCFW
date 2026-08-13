unsigned int open_cfw_test_operation_three_completion_word;
volatile unsigned int *open_cfw_test_operation_three_completion;
unsigned int open_cfw_test_operation_three_begin_result;
unsigned int open_cfw_test_operation_three_begin_count;
unsigned int open_cfw_test_operation_three_service_count;
unsigned int open_cfw_test_operation_three_completion_at_begin;
void *open_cfw_test_operation_three_begin_handle;
const void *open_cfw_test_operation_three_begin_descriptor;
void *open_cfw_test_operation_three_service_handle;

void open_cfw_test_operation_three_reset(void)
{
    open_cfw_test_operation_three_completion_word = 0xA5A5A5A5U;
    open_cfw_test_operation_three_completion =
        &open_cfw_test_operation_three_completion_word;
    open_cfw_test_operation_three_begin_result = 0U;
    open_cfw_test_operation_three_begin_count = 0U;
    open_cfw_test_operation_three_service_count = 0U;
    open_cfw_test_operation_three_completion_at_begin = 0xFFFFFFFFU;
    open_cfw_test_operation_three_begin_handle = (void *)0;
    open_cfw_test_operation_three_begin_descriptor = (const void *)0;
    open_cfw_test_operation_three_service_handle = (void *)0;
}

unsigned int open_cfw_test_operation_three_begin(
    void *handle,
    const void *descriptor
)
{
    ++open_cfw_test_operation_three_begin_count;
    open_cfw_test_operation_three_begin_handle = handle;
    open_cfw_test_operation_three_begin_descriptor = descriptor;
    open_cfw_test_operation_three_completion_at_begin =
        open_cfw_test_operation_three_completion_word;
    return open_cfw_test_operation_three_begin_result;
}

void open_cfw_test_operation_three_service(void *handle)
{
    ++open_cfw_test_operation_three_service_count;
    open_cfw_test_operation_three_service_handle = handle;
}

#define OPEN_CFW_UI_DISPLAY_OPERATION_THREE_COMPLETION(descriptor) \
    ((void)(descriptor), open_cfw_test_operation_three_completion)
#define OPEN_CFW_UI_DISPLAY_OPERATION_THREE_BEGIN(handle, descriptor) \
    open_cfw_test_operation_three_begin((handle), (descriptor))
#define OPEN_CFW_UI_DISPLAY_OPERATION_THREE_SERVICE(handle) \
    open_cfw_test_operation_three_service(handle)

#include "../../components/apollo_main/core_overlay/ui_display_operation_three.c"

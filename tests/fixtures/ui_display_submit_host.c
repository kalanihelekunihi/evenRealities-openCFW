unsigned int open_cfw_test_submit_handle_word;
unsigned char open_cfw_test_submit_descriptor[56];
unsigned int open_cfw_test_submit_call_count;
unsigned int open_cfw_test_submit_operation;
unsigned int open_cfw_test_submit_results[4];
void *open_cfw_test_submit_handle;
const void *open_cfw_test_submit_descriptor_pointer;

void open_cfw_test_submit_reset(void)
{
    unsigned int index;

    open_cfw_test_submit_handle_word = 0x01EA9E06U;
    for (index = 0; index < 56U; ++index) {
        open_cfw_test_submit_descriptor[index] = 0U;
    }
    for (index = 0; index < 4U; ++index) {
        open_cfw_test_submit_results[index] = 0x10U + index;
    }
    open_cfw_test_submit_call_count = 0U;
    open_cfw_test_submit_operation = 0xFFFFFFFFU;
    open_cfw_test_submit_handle = (void *)0;
    open_cfw_test_submit_descriptor_pointer = (const void *)0;
}

unsigned int open_cfw_test_submit_operation_call(
    unsigned int operation,
    void *handle,
    const void *descriptor
)
{
    ++open_cfw_test_submit_call_count;
    open_cfw_test_submit_operation = operation;
    open_cfw_test_submit_handle = handle;
    open_cfw_test_submit_descriptor_pointer = descriptor;
    return open_cfw_test_submit_results[operation];
}

#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ZERO(handle, descriptor) \
    open_cfw_test_submit_operation_call(0U, (handle), (descriptor))
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_ONE(handle, descriptor) \
    open_cfw_test_submit_operation_call(1U, (handle), (descriptor))
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_TWO(handle, descriptor) \
    open_cfw_test_submit_operation_call(2U, (handle), (descriptor))
#define OPEN_CFW_UI_DISPLAY_SUBMIT_OPERATION_THREE(handle, descriptor) \
    open_cfw_test_submit_operation_call(3U, (handle), (descriptor))

#include "../../components/apollo_main/core_overlay/ui_display_submit.c"

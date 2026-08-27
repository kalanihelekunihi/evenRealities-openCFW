#include <stdint.h>

typedef uintptr_t test_word;

typedef struct {
    void (*callback)(test_word);
    test_word argument;
} test_callback_record;

static test_word retained_owner;
static test_word retained_result;
static unsigned int retained_call_count;
static unsigned int callback_call_count;
static test_word callback_argument;
static test_callback_record callback_record;

static test_word open_cfw_test_callback_record(test_word owner)
{
    ++retained_call_count;
    retained_owner = owner;
    return retained_result;
}

#define OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_RECORD_4196C2(owner) \
    open_cfw_test_callback_record(owner)
#include "../../components/bootloader/core_overlay/runtime_callback_41639a.c"

static void open_cfw_test_registered_callback(test_word argument)
{
    ++callback_call_count;
    callback_argument = argument;
}

void open_cfw_test_callback_reset(test_word result_kind, test_word argument)
{
    retained_owner = 0U;
    retained_call_count = 0U;
    callback_call_count = 0U;
    callback_argument = 0U;
    callback_record.callback = open_cfw_test_registered_callback;
    callback_record.argument = argument;
    retained_result = result_kind == 0U
        ? 0U
        : ((test_word)&callback_record | (result_kind == 2U ? 1U : 0U));
}

test_word open_cfw_test_callback_retained_owner(void) { return retained_owner; }
unsigned int open_cfw_test_callback_retained_calls(void) { return retained_call_count; }
unsigned int open_cfw_test_callback_calls(void) { return callback_call_count; }
test_word open_cfw_test_callback_argument(void) { return callback_argument; }

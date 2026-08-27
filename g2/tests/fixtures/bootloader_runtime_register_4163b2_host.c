#include <stdint.h>
#include <string.h>

typedef uintptr_t test_word;

static test_word context_value;
static test_word allocation_result;
static test_word dynamic_result;
static test_word static_result;
static unsigned int allocation_calls;
static unsigned int free_calls;
static unsigned int dynamic_calls;
static unsigned int static_calls;
static test_word free_address;
static test_word backend_args[6];
static unsigned char allocated_record[32];

static test_word test_context(void) { return context_value; }
static test_word test_alloc(test_word size)
{
    ++allocation_calls;
    backend_args[0] = size;
    return allocation_result;
}
static void test_free(test_word address)
{
    ++free_calls;
    free_address = address;
}
static test_word test_dynamic(
    test_word handle, test_word count, test_word option,
    test_word tagged_record, test_word callback)
{
    ++dynamic_calls;
    backend_args[0] = handle;
    backend_args[1] = count;
    backend_args[2] = option;
    backend_args[3] = tagged_record;
    backend_args[4] = callback;
    return dynamic_result;
}
static test_word test_static(
    test_word handle, test_word count, test_word option,
    test_word tagged_record, test_word callback, test_word storage)
{
    ++static_calls;
    backend_args[0] = handle;
    backend_args[1] = count;
    backend_args[2] = option;
    backend_args[3] = tagged_record;
    backend_args[4] = callback;
    backend_args[5] = storage;
    return static_result;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() test_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_ALLOC_419730(size) test_alloc(size)
#define OPEN_CFW_BOOTLOADER_RUNTIME_FREE_419830(address) test_free(address)
#define OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_STATIC_4192DE(handle, count, option, tagged_record, callback, storage) test_static(handle, count, option, tagged_record, callback, storage)
#define OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_DYNAMIC_4192A8(handle, count, option, tagged_record, callback) test_dynamic(handle, count, option, tagged_record, callback)
#include "../../components/bootloader/core_overlay/runtime_register_4163b2.c"

void open_cfw_test_register_reset(
    test_word context, test_word allocation_ok,
    test_word dynamic_value, test_word static_value)
{
    context_value = context;
    memset(allocated_record, 0, sizeof(allocated_record));
    allocation_result = allocation_ok ? (test_word)allocated_record : 0U;
    dynamic_result = dynamic_value;
    static_result = static_value;
    allocation_calls = 0U;
    free_calls = 0U;
    dynamic_calls = 0U;
    static_calls = 0U;
    free_address = 0U;
    memset(backend_args, 0, sizeof(backend_args));
}

test_word open_cfw_test_register_allocated_address(void) { return (test_word)allocated_record; }
unsigned int open_cfw_test_register_allocation_calls(void) { return allocation_calls; }
unsigned int open_cfw_test_register_free_calls(void) { return free_calls; }
unsigned int open_cfw_test_register_dynamic_calls(void) { return dynamic_calls; }
unsigned int open_cfw_test_register_static_calls(void) { return static_calls; }
test_word open_cfw_test_register_free_address(void) { return free_address; }
test_word open_cfw_test_register_backend_arg(unsigned int index) { return backend_args[index]; }
test_word open_cfw_test_register_record_word(test_word address, unsigned int index)
{
    return ((const test_word *)address)[index];
}

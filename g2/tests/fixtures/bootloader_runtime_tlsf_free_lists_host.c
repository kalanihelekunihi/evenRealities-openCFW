#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_BOOTLOADER_TLSF_FREE_LISTS_HOST 1
#include "../../components/bootloader/core_overlay/runtime_tlsf_free_lists_416c4e.c"

static unsigned int open_cfw_test_assert_count;
static uintptr_t open_cfw_test_assert_expression;
static uintptr_t open_cfw_test_assert_file;
static unsigned int open_cfw_test_assert_line;

void open_cfw_bootloader_tlsf_free_lists_host_assert(
    const char *expression,
    const char *file,
    open_cfw_bootloader_tlsf_list_word line)
{
    ++open_cfw_test_assert_count;
    open_cfw_test_assert_expression = (uintptr_t)expression;
    open_cfw_test_assert_file = (uintptr_t)file;
    open_cfw_test_assert_line = line;
}

open_cfw_bootloader_tlsf_list_word open_cfw_bootloader_runtime_ctz_4169e2(
    open_cfw_bootloader_tlsf_list_word value)
{
    open_cfw_bootloader_tlsf_list_word count = 0U;
    while ((value & 1U) == 0U) {
        value >>= 1U;
        ++count;
    }
    return count;
}

void *open_cfw_bootloader_tlsf_block_to_pointer_416a9c(
    const open_cfw_bootloader_tlsf_list_block *block)
{
    return (void *)((uintptr_t)block +
        offsetof(open_cfw_bootloader_tlsf_list_block, size) +
        sizeof(open_cfw_bootloader_tlsf_list_word));
}

void *open_cfw_bootloader_tlsf_align_pointer_416ba4(
    const void *pointer,
    size_t alignment)
{
    return (void *)(((uintptr_t)pointer + (alignment - 1U)) &
        ~(uintptr_t)(alignment - 1U));
}

void open_cfw_test_tlsf_free_lists_reset_assert(void)
{
    open_cfw_test_assert_count = 0U;
    open_cfw_test_assert_expression = 0U;
    open_cfw_test_assert_file = 0U;
    open_cfw_test_assert_line = 0U;
}

unsigned int open_cfw_test_tlsf_free_lists_assert_count(void)
{
    return open_cfw_test_assert_count;
}

uintptr_t open_cfw_test_tlsf_free_lists_assert_expression(void)
{
    return open_cfw_test_assert_expression;
}

uintptr_t open_cfw_test_tlsf_free_lists_assert_file(void)
{
    return open_cfw_test_assert_file;
}

unsigned int open_cfw_test_tlsf_free_lists_assert_line(void)
{
    return open_cfw_test_assert_line;
}

size_t open_cfw_test_tlsf_free_lists_control_size(void)
{
    return sizeof(open_cfw_bootloader_tlsf_list_control);
}

open_cfw_bootloader_tlsf_list_block *
open_cfw_test_tlsf_free_lists_null_block(
    open_cfw_bootloader_tlsf_list_control *control)
{
    return &control->block_null;
}

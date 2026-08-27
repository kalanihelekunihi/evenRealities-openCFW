#include <stdint.h>
#include <stddef.h>

#define OPEN_CFW_BOOT_SERVICES_HOST 1
#include "../../components/bootloader/core_overlay/runtime_boot_services_41f9d8.c"

static open_cfw_boot_service_initializer initializers[300];
static open_cfw_boot_service_initializer scratch[256];
static uint32_t initializer_count;
static uint32_t delay_calls;
static uint32_t delay_duration;
static uint32_t copy_calls;
static uint32_t copy_size;
static uint32_t sort_calls;
static uint32_t sort_count;
static uint32_t sort_size;
static uint32_t invoked[256];
static uint32_t invoke_count;

static void reset_state(void)
{
    uint32_t index;
    initializer_count = 0U;
    delay_calls = 0U;
    delay_duration = 0U;
    copy_calls = 0U;
    copy_size = 0U;
    sort_calls = 0U;
    sort_count = 0U;
    sort_size = 0U;
    invoke_count = 0U;
    for (index = 0U; index < 300U; ++index) {
        initializers[index].callback = 0U;
        initializers[index].priority = 0U;
    }
    for (index = 0U; index < 256U; ++index) {
        scratch[index].callback = 0U;
        scratch[index].priority = 0U;
        invoked[index] = 0U;
    }
}

void open_cfw_boot_services_host_delay(uint32_t duration)
{
    ++delay_calls;
    delay_duration = duration;
}

const open_cfw_boot_service_initializer *
open_cfw_boot_services_host_initializer_begin(void)
{
    return initializers;
}

uint32_t open_cfw_boot_services_host_initializer_count(void)
{
    return initializer_count;
}

open_cfw_boot_service_initializer *
open_cfw_boot_services_host_initializer_scratch(void)
{
    return scratch;
}

void *open_cfw_boot_services_host_copy(
    void *destination,
    const void *source,
    uint32_t size)
{
    uint8_t *destination_bytes = (uint8_t *)destination;
    const uint8_t *source_bytes = (const uint8_t *)source;
    uint32_t index;
    ++copy_calls;
    copy_size = size;
    for (index = 0U; index < size; ++index) {
        destination_bytes[index] = source_bytes[index];
    }
    return destination;
}

void open_cfw_boot_services_host_sort(
    void *base,
    uint32_t count,
    uint32_t size,
    open_cfw_boot_service_compare_fn compare)
{
    open_cfw_boot_service_initializer *records =
        (open_cfw_boot_service_initializer *)base;
    uint32_t index;
    ++sort_calls;
    sort_count = count;
    sort_size = size;
    for (index = 1U; index < count; ++index) {
        open_cfw_boot_service_initializer value = records[index];
        uint32_t position = index;
        while (position != 0U &&
               compare(&records[position - 1U], &value) > 0) {
            records[position] = records[position - 1U];
            --position;
        }
        records[position] = value;
    }
}

void open_cfw_boot_services_host_invoke(uint32_t callback)
{
    if (invoke_count < 256U) {
        invoked[invoke_count] = callback;
    }
    ++invoke_count;
}

uint32_t open_cfw_test_boot_services_delays(void)
{
    reset_state();
    open_cfw_bootloader_delay_milliseconds_41f9d8(3U);
    if (delay_calls != 1U || delay_duration != 3000U) {
        return 0U;
    }
    open_cfw_bootloader_delay_milliseconds_41f9d8(0xFFFFFFFFU);
    if (delay_calls != 2U || delay_duration != 0xFFFFFC18U) {
        return 0U;
    }
    open_cfw_bootloader_delay_41f9e6(17U);
    return delay_calls == 3U && delay_duration == 17U;
}

uint32_t open_cfw_test_boot_services_comparator(void)
{
    open_cfw_boot_service_initializer left = {1U, 25U};
    open_cfw_boot_service_initializer right = {2U, 1U};
    return open_cfw_bootloader_initializer_priority_compare_41f9f0(
               &left, &right) == 24 &&
           open_cfw_bootloader_initializer_priority_compare_41f9f0(
               &right, &left) == -24 &&
           open_cfw_bootloader_initializer_priority_compare_41f9f0(
               &left, &left) == 0;
}

uint32_t open_cfw_test_boot_services_sorted_dispatch(void)
{
    reset_state();
    initializer_count = 5U;
    initializers[0].callback = 11U;
    initializers[0].priority = 25U;
    initializers[1].callback = 22U;
    initializers[1].priority = 1U;
    initializers[2].callback = 0U;
    initializers[2].priority = 2U;
    initializers[3].callback = 33U;
    initializers[3].priority = 1U;
    initializers[4].callback = 44U;
    initializers[4].priority = 26U;
    open_cfw_bootloader_run_initializers_41f9f8();
    return copy_calls == 1U && copy_size == 40U && sort_calls == 1U &&
           sort_count == 5U && sort_size == 8U && invoke_count == 4U &&
           invoked[0] == 22U && invoked[1] == 33U && invoked[2] == 11U &&
           invoked[3] == 44U;
}

uint32_t open_cfw_test_boot_services_count_cap(void)
{
    uint32_t index;
    reset_state();
    initializer_count = 300U;
    for (index = 0U; index < initializer_count; ++index) {
        initializers[index].callback = index + 1U;
        initializers[index].priority = 300U - index;
    }
    open_cfw_bootloader_run_initializers_41f9f8();
    if (copy_size != 2048U || sort_count != 256U || invoke_count != 256U) {
        return 0U;
    }
    for (index = 0U; index < 256U; ++index) {
        if (invoked[index] != 256U - index) {
            return 0U;
        }
    }
    return 1U;
}

uint32_t open_cfw_test_boot_services_empty_table(void)
{
    reset_state();
    open_cfw_bootloader_run_initializers_41f9f8();
    return copy_calls == 1U && copy_size == 0U && sort_calls == 1U &&
           sort_count == 0U && invoke_count == 0U;
}

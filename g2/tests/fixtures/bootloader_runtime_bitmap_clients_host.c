#include <stdint.h>
#include <string.h>

uintptr_t open_cfw_clients_host_controller0;
uintptr_t open_cfw_clients_host_controller1;
uintptr_t open_cfw_clients_host_controller_required;
uint32_t open_cfw_clients_host_configuration[3];
uintptr_t open_cfw_clients_host_current;
uint8_t open_cfw_clients_host_ready;

uint32_t open_cfw_clients_fixture_query_status;
uint32_t open_cfw_clients_fixture_query_result[3];
uintptr_t open_cfw_clients_fixture_query_controller;
uintptr_t open_cfw_clients_fixture_query_instance;
uint32_t open_cfw_clients_fixture_query_calls;
uint32_t open_cfw_clients_fixture_bitmap[2][2];
uint32_t open_cfw_clients_fixture_count6;
uint32_t open_cfw_clients_fixture_save_calls;
uint32_t open_cfw_clients_fixture_restore_calls;
uint32_t open_cfw_clients_fixture_restored_mask;
uint32_t open_cfw_clients_fixture_update_calls;
uint32_t open_cfw_clients_fixture_update_row;
uint32_t open_cfw_clients_fixture_update_bit;
uint32_t open_cfw_clients_fixture_update_enabled;
uint32_t open_cfw_clients_fixture_copy_calls;

uint32_t open_cfw_clients_host_query(
    uint32_t *output, uintptr_t controller, uintptr_t instance)
{
    ++open_cfw_clients_fixture_query_calls;
    open_cfw_clients_fixture_query_controller = controller;
    open_cfw_clients_fixture_query_instance = instance;
    memcpy(output, open_cfw_clients_fixture_query_result, 12U);
    return open_cfw_clients_fixture_query_status;
}

uint32_t open_cfw_clients_host_critical_save(void)
{
    ++open_cfw_clients_fixture_save_calls;
    return 0xA5U;
}

void open_cfw_clients_host_critical_restore(uint32_t mask)
{
    ++open_cfw_clients_fixture_restore_calls;
    open_cfw_clients_fixture_restored_mask = mask;
}

uint32_t open_cfw_clients_host_bitmap_count(uint32_t row)
{
    return row == 6U ? open_cfw_clients_fixture_count6 : 0U;
}

uint32_t open_cfw_clients_host_bitmap_test(uint32_t row, uint32_t bit)
{
    if (row >= 2U || bit >= 64U) return 0U;
    return (open_cfw_clients_fixture_bitmap[row][bit >> 5] >> (bit & 31U)) & 1U;
}

uint32_t open_cfw_clients_host_bitmap_update(
    uint32_t row, uint32_t bit, uint32_t enabled)
{
    uint32_t mask;
    ++open_cfw_clients_fixture_update_calls;
    open_cfw_clients_fixture_update_row = row;
    open_cfw_clients_fixture_update_bit = bit;
    open_cfw_clients_fixture_update_enabled = enabled;
    if (row >= 2U || bit >= 64U) return 6U;
    mask = 1U << (bit & 31U);
    if (enabled != 0U) open_cfw_clients_fixture_bitmap[row][bit >> 5] |= mask;
    else open_cfw_clients_fixture_bitmap[row][bit >> 5] &= ~mask;
    return 0U;
}

void open_cfw_clients_host_copy(void *target, const void *source, uint32_t size)
{
    ++open_cfw_clients_fixture_copy_calls;
    memcpy(target, source, size);
}

#include "../../components/bootloader/core_overlay/runtime_bitmap_clients_421978.c"

void open_cfw_clients_fixture_reset(void)
{
    open_cfw_clients_host_controller0 = 0U;
    open_cfw_clients_host_controller1 = 0U;
    open_cfw_clients_host_controller_required = 0U;
    memset(open_cfw_clients_host_configuration, 0, sizeof(open_cfw_clients_host_configuration));
    open_cfw_clients_host_current = 0U;
    open_cfw_clients_host_ready = 0U;
    open_cfw_clients_fixture_query_status = 0U;
    open_cfw_clients_fixture_query_result[0] = 0x11111111U;
    open_cfw_clients_fixture_query_result[1] = 0x22222222U;
    open_cfw_clients_fixture_query_result[2] = 0x33333333U;
    open_cfw_clients_fixture_query_controller = 0U;
    open_cfw_clients_fixture_query_instance = 0U;
    open_cfw_clients_fixture_query_calls = 0U;
    memset(open_cfw_clients_fixture_bitmap, 0, sizeof(open_cfw_clients_fixture_bitmap));
    open_cfw_clients_fixture_count6 = 0U;
    open_cfw_clients_fixture_save_calls = 0U;
    open_cfw_clients_fixture_restore_calls = 0U;
    open_cfw_clients_fixture_restored_mask = 0U;
    open_cfw_clients_fixture_update_calls = 0U;
    open_cfw_clients_fixture_update_row = 0U;
    open_cfw_clients_fixture_update_bit = 0U;
    open_cfw_clients_fixture_update_enabled = 0U;
    open_cfw_clients_fixture_copy_calls = 0U;
}

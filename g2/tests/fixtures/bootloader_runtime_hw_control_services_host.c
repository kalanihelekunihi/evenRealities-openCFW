#include <stddef.h>
#include <stdint.h>

uint32_t open_cfw_hwcs_host_control_register;
uint8_t open_cfw_hwcs_host_countdown;
uint8_t open_cfw_hwcs_host_latch;
uint32_t open_cfw_hwcs_host_register_results[8];
uint32_t open_cfw_hwcs_host_register_result_count;
uint32_t open_cfw_hwcs_host_register_result_index;
uint32_t open_cfw_hwcs_host_register_calls[8][4];
uint32_t open_cfw_hwcs_host_debug_result;
uint32_t open_cfw_hwcs_host_debug_calls;
uint32_t open_cfw_hwcs_host_delay_value;
uint32_t open_cfw_hwcs_host_primask_token;
uint32_t open_cfw_hwcs_host_restored_token;

uint32_t open_cfw_hwcs_host_register_call(
    uint32_t timeout, uint32_t address, uint32_t mask, uint32_t value)
{
    uint32_t index = open_cfw_hwcs_host_register_result_index++;
    open_cfw_hwcs_host_register_calls[index][0] = timeout;
    open_cfw_hwcs_host_register_calls[index][1] = address;
    open_cfw_hwcs_host_register_calls[index][2] = mask;
    open_cfw_hwcs_host_register_calls[index][3] = value;
    return index < open_cfw_hwcs_host_register_result_count
        ? open_cfw_hwcs_host_register_results[index] : 0U;
}

uint32_t open_cfw_hwcs_host_debug_shutdown(void)
{
    ++open_cfw_hwcs_host_debug_calls;
    return open_cfw_hwcs_host_debug_result;
}

void open_cfw_hwcs_host_delay(uint32_t value) { open_cfw_hwcs_host_delay_value = value; }
uint32_t open_cfw_hwcs_host_primask_enter(void) { return open_cfw_hwcs_host_primask_token; }
void open_cfw_hwcs_host_primask_restore(uint32_t token) { open_cfw_hwcs_host_restored_token = token; }

void open_cfw_hwcs_host_reset(void)
{
    size_t i;
    open_cfw_hwcs_host_control_register = 0U;
    open_cfw_hwcs_host_countdown = 0U;
    open_cfw_hwcs_host_latch = 0U;
    open_cfw_hwcs_host_register_result_count = 0U;
    open_cfw_hwcs_host_register_result_index = 0U;
    open_cfw_hwcs_host_debug_result = 0U;
    open_cfw_hwcs_host_debug_calls = 0U;
    open_cfw_hwcs_host_delay_value = 0U;
    open_cfw_hwcs_host_primask_token = 0U;
    open_cfw_hwcs_host_restored_token = 0U;
    for (i = 0U; i < 8U; ++i) {
        open_cfw_hwcs_host_register_results[i] = 0U;
        open_cfw_hwcs_host_register_calls[i][0] = 0U;
        open_cfw_hwcs_host_register_calls[i][1] = 0U;
        open_cfw_hwcs_host_register_calls[i][2] = 0U;
        open_cfw_hwcs_host_register_calls[i][3] = 0U;
    }
}

#include "../../components/bootloader/core_overlay/runtime_hw_control_services_423d20.c"

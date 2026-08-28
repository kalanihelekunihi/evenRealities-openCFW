#include <stdint.h>

uint8_t open_cfw_debug_host_enable_count;
uint8_t open_cfw_debug_host_power_count;
uint8_t open_cfw_debug_host_trace_count;
uint8_t open_cfw_debug_host_power_entry_state;
volatile uint32_t open_cfw_debug_host_dbgctrl;
volatile uint32_t open_cfw_debug_host_demcr;
uint32_t open_cfw_debug_host_power_was_enabled;
uint32_t open_cfw_debug_host_enable_calls;
uint32_t open_cfw_debug_host_disable_calls;
uint32_t open_cfw_debug_host_query_calls;
uint32_t open_cfw_debug_host_delay_calls;
uint32_t open_cfw_debug_host_delay_result;
uint32_t open_cfw_debug_host_restore_calls;
uint32_t open_cfw_debug_host_last_device;
uint32_t open_cfw_debug_host_last_timeout;
uint32_t open_cfw_debug_host_last_mask;
uint32_t open_cfw_debug_host_last_value;

uint32_t open_cfw_debug_host_critical_save(void) { return 0xA5A50000U + open_cfw_debug_host_restore_calls; }
void open_cfw_debug_host_critical_restore(uint32_t mask) { (void)mask; ++open_cfw_debug_host_restore_calls; }
uint32_t open_cfw_debug_host_pwrctrl_enable(uint32_t device) { open_cfw_debug_host_last_device=device; ++open_cfw_debug_host_enable_calls; return 0U; }
uint32_t open_cfw_debug_host_pwrctrl_disable(uint32_t device) { open_cfw_debug_host_last_device=device; ++open_cfw_debug_host_disable_calls; return 0U; }
uint32_t open_cfw_debug_host_pwrctrl_enabled(uint32_t device, uint8_t *enabled) { open_cfw_debug_host_last_device=device; ++open_cfw_debug_host_query_calls; *enabled=(uint8_t)open_cfw_debug_host_power_was_enabled; return 0U; }
uint32_t open_cfw_debug_host_delay_status_change(uint32_t timeout, volatile uint32_t *reg, uint32_t mask, uint32_t value) { (void)reg; open_cfw_debug_host_last_timeout=timeout; open_cfw_debug_host_last_mask=mask; open_cfw_debug_host_last_value=value; ++open_cfw_debug_host_delay_calls; return open_cfw_debug_host_delay_result; }

void open_cfw_debug_fixture_reset(void)
{
    open_cfw_debug_host_enable_count=0; open_cfw_debug_host_power_count=0;
    open_cfw_debug_host_trace_count=0; open_cfw_debug_host_power_entry_state=0;
    open_cfw_debug_host_dbgctrl=0; open_cfw_debug_host_demcr=0;
    open_cfw_debug_host_power_was_enabled=0; open_cfw_debug_host_enable_calls=0;
    open_cfw_debug_host_disable_calls=0; open_cfw_debug_host_query_calls=0;
    open_cfw_debug_host_delay_calls=0; open_cfw_debug_host_delay_result=0;
    open_cfw_debug_host_restore_calls=0; open_cfw_debug_host_last_device=0;
    open_cfw_debug_host_last_timeout=0; open_cfw_debug_host_last_mask=0;
    open_cfw_debug_host_last_value=0;
}

#include "../../components/bootloader/core_overlay/runtime_debug_services_422468.c"

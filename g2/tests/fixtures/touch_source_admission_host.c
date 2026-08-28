/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "runtime_touch_runtime_adapters.h"
#include "runtime_touch_cat2_adapters.h"

static uint32_t trace_value;
static uint32_t cycle_value;
static int halt_code;

static void trace_one(void) { trace_value = trace_value * 10u + 1u; }
static void trace_two(void) { trace_value = trace_value * 10u + 2u; }
static void trace_three(void) { trace_value = trace_value * 10u + 3u; }
static void cycles(uint32_t value) { cycle_value = value; }
static void halt_capture(int code, void *context)
{
    (void)context;
    halt_code = code;
}
static int syspm_capture(uint32_t type, void *context)
{
    return (int)type + (context != 0 ? 100 : 0);
}
static int flash_capture(uint32_t row, const uint32_t *data, void *context)
{
    return (int)(row + data[0] + (context != 0 ? 1u : 0u));
}
static int gpio_capture(void *base, uint32_t pin, const void *config, void *context)
{
    return (base != 0 && config != 0 && context != 0) ? (int)pin : -10;
}
static void i2c_capture(void *base, void *i2c_context, void *provider_context)
{
    if (base != 0 && i2c_context != 0 && provider_context != 0) {
        trace_value += 7u;
    }
}
static uint32_t scb_read_capture(
    const void *base, void *buffer, uint32_t size, void *context)
{
    uint8_t *bytes = (uint8_t *)buffer;
    if (base == 0 || context == 0 || (bytes == 0 && size != 0u)) {
        return 0u;
    }
    if (size != 0u) {
        bytes[0] = 0x5Au;
    }
    return size;
}
static uint32_t scb_write_capture(
    void *base, const void *buffer, uint32_t data, uint32_t size,
    void *context)
{
    return (base != 0 && buffer != 0 && context != 0) ? size + data : 0u;
}
static int scb_level_capture(void *base, uint32_t level, void *context)
{
    return (base != 0 && context != 0) ? (int)level : -2;
}
static int gpio_value_capture(
    void *base, uint32_t pin, uint32_t value, void *context)
{
    return (base != 0 && context != 0) ? (int)(pin + value) : -2;
}
static int sysclk_capture(
    uint32_t operation, uint32_t argument0, uint32_t argument1,
    uint32_t *result, void *context)
{
    if (result == 0 || context == 0) {
        return -2;
    }
    *result = operation + argument0 + argument1;
    return 0;
}
static int msclp_capture(
    void *base, const void *config, uint32_t key, void *context)
{
    return (base != 0 && config != 0 && context != 0) ? (int)key : -2;
}
static void i2c_helper_capture(
    void *base, uint32_t flag, void *i2c_context, void *provider_context)
{
    if (base != 0 && i2c_context != 0 && provider_context != 0) {
        trace_value += flag;
    }
}
static int register_callback_capture(void *record, void *context)
{
    return (record != 0 && context != 0) ? 1 : 0;
}
static int system_halt_capture(void *context)
{
    return context != 0 ? 7 : -2;
}

uint32_t touch_host_runtime_arrays(void)
{
    const open_cfw_touch_void_fn pre[] = {trace_one};
    const open_cfw_touch_void_fn init[] = {trace_two, 0, trace_three};
    trace_value = 0u;
    (void)open_cfw_touch_runtime_init_arrays(pre, pre + 1, init, init + 3);
    return trace_value;
}

int touch_host_runtime_exit(int with_halt)
{
    trace_value = 0u;
    halt_code = -99;
    return open_cfw_touch_runtime_exit_adapter(
        7, trace_one, with_halt ? halt_capture : 0, 0);
}

int touch_host_halt_code(void) { return halt_code; }
uint32_t touch_host_trace(void) { return trace_value; }

uint32_t touch_host_delay(uint16_t us, uint32_t mhz)
{
    cycle_value = 0u;
    (void)open_cfw_touch_cat2_delay_us(us, mhz, cycles);
    return cycle_value;
}

uint32_t touch_host_systick(void)
{
    open_cfw_touch_cat2_systick state = {0};
    trace_value = 0u;
    (void)open_cfw_touch_cat2_systick_init(&state, 1u, 999u);
    (void)open_cfw_touch_cat2_systick_set_callback(&state, 0u, trace_one);
    (void)open_cfw_touch_cat2_systick_set_callback(&state, 4u, trace_two);
    state.ctrl |= OPEN_CFW_TOUCH_SYSTICK_COUNTFLAG;
    open_cfw_touch_cat2_systick_service(&state);
    return trace_value | (state.load << 8);
}

int touch_host_syspm(int available)
{
    return open_cfw_touch_cat2_syspm_route(
        available ? syspm_capture : 0, 9u, (void *)(uintptr_t)1u);
}

int touch_host_flash_route(int available)
{
    const uint32_t data[] = {5u};
    return open_cfw_touch_cat2_flash_write_row_route(
        available ? flash_capture : 0, 11u, data, (void *)(uintptr_t)1u);
}

int touch_host_gpio_route(int available)
{
    return open_cfw_touch_cat2_gpio_pin_init_route(
        available ? gpio_capture : 0, (void *)(uintptr_t)1u, 6u,
        (const void *)(uintptr_t)2u, (void *)(uintptr_t)3u);
}

int touch_host_i2c_route(int available)
{
    trace_value = 0u;
    return open_cfw_touch_cat2_i2c_slave_interrupt_route(
        available ? i2c_capture : 0, (void *)(uintptr_t)1u,
        (void *)(uintptr_t)2u, (void *)(uintptr_t)3u);
}

uint32_t touch_host_scb_read_route(int available)
{
    uint8_t byte = 0u;
    uint32_t result = open_cfw_touch_cat2_scb_read_route(
        available ? scb_read_capture : 0, (const void *)(uintptr_t)1u,
        &byte, 1u, (void *)(uintptr_t)2u);
    return result | ((uint32_t)byte << 8);
}

uint32_t touch_host_scb_write_route(int available)
{
    const uint8_t byte = 3u;
    return open_cfw_touch_cat2_scb_write_route(
        available ? scb_write_capture : 0, (void *)(uintptr_t)1u,
        &byte, 7u, 2u, (void *)(uintptr_t)2u);
}

int touch_host_scb_level_route(int available)
{
    return open_cfw_touch_cat2_scb_set_rx_level_route(
        available ? scb_level_capture : 0, (void *)(uintptr_t)1u, 6u,
        (void *)(uintptr_t)2u);
}

int touch_host_gpio_value_route(int available)
{
    return open_cfw_touch_cat2_gpio_value_route(
        available ? gpio_value_capture : 0, (void *)(uintptr_t)1u, 3u, 9u,
        (void *)(uintptr_t)2u);
}

uint32_t touch_host_sysclk_route(int available)
{
    uint32_t result = 0xFFFFu;
    int status = open_cfw_touch_cat2_sysclk_route(
        available ? sysclk_capture : 0, 2u, 5u, 7u, &result,
        (void *)(uintptr_t)1u);
    return status == 0 ? result : (uint32_t)status;
}

int touch_host_msclp_route(int available)
{
    return open_cfw_touch_cat2_msclp_route(
        available ? msclp_capture : 0, (void *)(uintptr_t)1u,
        (const void *)(uintptr_t)2u, 5u, (void *)(uintptr_t)3u);
}

int touch_host_i2c_helper_route(int available)
{
    trace_value = 0u;
    return open_cfw_touch_cat2_i2c_helper_route(
        available ? i2c_helper_capture : 0, (void *)(uintptr_t)1u, 9u,
        (void *)(uintptr_t)2u, (void *)(uintptr_t)3u);
}

int touch_host_register_callback_route(int available)
{
    return open_cfw_touch_cat2_register_callback_route(
        available ? register_callback_capture : 0, (void *)(uintptr_t)1u,
        (void *)(uintptr_t)2u);
}

int touch_host_system_halt_route(int available)
{
    return open_cfw_touch_cat2_system_halt_route(
        available ? system_halt_capture : 0, (void *)(uintptr_t)1u);
}

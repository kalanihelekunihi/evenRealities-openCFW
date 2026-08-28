/* SPDX-License-Identifier: MIT */
#include <stdint.h>

static uint32_t fixture_state_words[4];
static void *fixture_handle;
static uint8_t fixture_default_config[24];
static uint32_t fixture_status[14];
static uintptr_t fixture_calls[64][4];
static uint32_t fixture_call_count;
static uint32_t fixture_logs[8][3];
static uint32_t fixture_log_count;

#define OPEN_CFW_MSPI_LOW_LEVEL_INIT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_low_level_init_420254.c"

open_cfw_low_init_state *open_cfw_low_init_host_state(void)
{
    return (open_cfw_low_init_state *)fixture_state_words;
}

void **open_cfw_low_init_host_handle_word(void) { return &fixture_handle; }
const uint8_t *open_cfw_low_init_host_default_config(void)
{
    return fixture_default_config;
}

uint32_t open_cfw_low_init_host_call(
    uint32_t operation, uintptr_t first, uintptr_t second, uintptr_t third)
{
    uint32_t index = fixture_call_count++;
    fixture_calls[index][0] = operation;
    fixture_calls[index][1] = first;
    fixture_calls[index][2] = second;
    fixture_calls[index][3] = third;
    if (operation == 0U && fixture_status[operation] == 0U) {
        *(void **)second = (void *)(uintptr_t)0x2468U;
    }
    if (operation == 6U && second != 0U) {
        *(uint32_t *)second = 0xA5A55A5AU;
    }
    return fixture_status[operation];
}

void open_cfw_low_init_host_log(uint32_t level, uint32_t line, uint32_t format)
{
    uint32_t index = fixture_log_count++;
    fixture_logs[index][0] = level;
    fixture_logs[index][1] = line;
    fixture_logs[index][2] = format;
}

void open_cfw_bootloader_mspi_xip_config_41ff34(uint32_t value)
{
    (void)open_cfw_low_init_host_call(10U, value, 0U, 0U);
}

void open_cfw_bootloader_pin_groups_41fadc(uint32_t instance, uint32_t device)
{
    (void)open_cfw_low_init_host_call(11U, instance, device, 0U);
}

void open_cfw_bootloader_nvic_set_priority_41fdde(uint32_t irq, uint32_t priority)
{
    (void)open_cfw_low_init_host_call(12U, irq, priority, 0U);
}

void open_cfw_bootloader_nvic_enable_irq_41fdc0(uint32_t irq)
{
    (void)open_cfw_low_init_host_call(13U, irq, 0U, 0U);
}

void open_cfw_low_init_fixture_reset(void)
{
    uint32_t i;
    uint32_t j;
    for (i = 0U; i < 4U; ++i) fixture_state_words[i] = 0U;
    for (i = 0U; i < 24U; ++i) fixture_default_config[i] = (uint8_t)i;
    fixture_default_config[8] = 16U;
    for (i = 0U; i < 14U; ++i) fixture_status[i] = 0U;
    for (i = 0U; i < 64U; ++i) for (j = 0U; j < 4U; ++j) fixture_calls[i][j] = 0U;
    for (i = 0U; i < 8U; ++i) for (j = 0U; j < 3U; ++j) fixture_logs[i][j] = 0U;
    fixture_handle = (void *)0;
    fixture_call_count = 0U;
    fixture_log_count = 0U;
}

void open_cfw_low_init_fixture_status(uint32_t operation, uint32_t status)
{
    fixture_status[operation] = status;
}
void open_cfw_low_init_fixture_active(uint32_t active)
{
    ((open_cfw_low_init_state *)fixture_state_words)->initialized = (uint8_t)active;
}
uint32_t open_cfw_low_init_fixture_call_count(void) { return fixture_call_count; }
uintptr_t open_cfw_low_init_fixture_call(uint32_t index, uint32_t field)
{
    return fixture_calls[index][field];
}
uint32_t open_cfw_low_init_fixture_log_count(void) { return fixture_log_count; }
uint32_t open_cfw_low_init_fixture_log(uint32_t index, uint32_t field)
{
    return fixture_logs[index][field];
}
uint32_t open_cfw_low_init_fixture_state(uint32_t index)
{
    return fixture_state_words[index];
}
uintptr_t open_cfw_low_init_fixture_state_address(void)
{
    return (uintptr_t)fixture_state_words;
}
const uint8_t *open_cfw_low_init_fixture_default(void) { return fixture_default_config; }

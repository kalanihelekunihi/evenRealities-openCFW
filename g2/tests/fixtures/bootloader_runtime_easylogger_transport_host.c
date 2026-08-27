#include <stdint.h>
#include <stddef.h>

#define OPEN_CFW_BOOTLOADER_EASYLOGGER_TRANSPORT_HOST 1
#include "../../components/bootloader/core_overlay/runtime_easylogger_transport_41b854.c"

static uint8_t initialized[4];
static uint8_t completion[4];
static uint32_t zero_calls;
static uint32_t zero_size;
static uint32_t start_calls;
static uint32_t start_result;
static uint32_t started_channel;
static const void *started_buffer;
static uint32_t started_length;
static uint8_t descriptor_snapshot[56];
static uint8_t completion_at_start;
static uint32_t wait_calls;
static uint32_t wait_duration_error;
static uint32_t complete_after_waits;

static void reset_state(void)
{
    uint32_t index;
    for (index = 0U; index < 4U; ++index) {
        initialized[index] = 0U;
        completion[index] = 0U;
    }
    zero_calls = 0U;
    zero_size = 0U;
    start_calls = 0U;
    start_result = 0U;
    started_channel = 0xFFFFFFFFU;
    started_buffer = (const void *)0;
    started_length = 0U;
    for (index = 0U; index < 56U; ++index) {
        descriptor_snapshot[index] = 0xA5U;
    }
    completion_at_start = 0xFFU;
    wait_calls = 0U;
    wait_duration_error = 0U;
    complete_after_waits = 0U;
}

void open_cfw_bootloader_easylogger_transport_host_zero(
    void *destination,
    uint32_t size)
{
    uint8_t *bytes = (uint8_t *)destination;
    uint32_t index;
    ++zero_calls;
    zero_size = size;
    for (index = 0U; index < size; ++index) {
        bytes[index] = 0U;
    }
}

uint8_t open_cfw_bootloader_easylogger_transport_host_initialized(
    uint8_t channel)
{
    return initialized[channel];
}

void open_cfw_bootloader_easylogger_transport_host_set_completion(
    uint8_t channel,
    uint8_t value)
{
    completion[channel] = value;
}

uint8_t open_cfw_bootloader_easylogger_transport_host_completion(
    uint8_t channel)
{
    return completion[channel];
}

uint32_t open_cfw_bootloader_easylogger_transport_host_start(
    uint8_t channel,
    const void *buffer,
    uint32_t length,
    void *descriptor)
{
    uint8_t *bytes = (uint8_t *)descriptor;
    uint32_t index;
    ++start_calls;
    started_channel = channel;
    started_buffer = buffer;
    started_length = length;
    completion_at_start = completion[channel];
    for (index = 0U; index < 56U; ++index) {
        descriptor_snapshot[index] = bytes[index];
    }
    if (complete_after_waits == 0U) {
        completion[channel] = 1U;
    }
    return start_result;
}

void open_cfw_bootloader_easylogger_transport_host_wait(uint32_t duration)
{
    ++wait_calls;
    if (duration != 10U) {
        wait_duration_error = 1U;
    }
    if (complete_after_waits != 0xFFFFFFFFU &&
        wait_calls >= complete_after_waits && started_channel < 4U) {
        completion[started_channel] = 1U;
    }
}

uint32_t open_cfw_test_easylogger_transport_rejects_invalid_channels(void)
{
    static const uint8_t payload[2] = {0x12U, 0x34U};
    uint32_t first;
    uint32_t second;
    reset_state();
    first = open_cfw_bootloader_easylogger_channel_write_41f918(
        4U, payload, 2U);
    initialized[1] = 2U;
    second = open_cfw_bootloader_easylogger_channel_write_41f918(
        1U, payload, 2U);
    return first == 1U && second == 1U && zero_calls == 2U &&
           zero_size == 56U && start_calls == 0U && wait_calls == 0U;
}

uint32_t open_cfw_test_easylogger_transport_driver_routes_channel_one(void)
{
    static const uint8_t payload[3] = {0x51U, 0x52U, 0x53U};
    uint32_t result;
    reset_state();
    initialized[1] = 1U;
    completion[1] = 1U;
    result = open_cfw_bootloader_easylogger_driver_output_41b854(
        payload, 3U, 0xDEADBEEFU);
    return result == 0U && start_calls == 1U && started_channel == 1U &&
           started_buffer == payload && started_length == 3U &&
           completion_at_start == 0U && wait_calls == 0U;
}

uint32_t open_cfw_test_easylogger_transport_descriptor_and_polling(void)
{
    static const uint8_t payload[5] = {1U, 2U, 3U, 4U, 5U};
    uint32_t index;
    uint32_t expected_pointer = (uint32_t)(uintptr_t)payload;
    uint32_t observed_pointer;
    uint32_t observed_length;
    uint32_t result;
    reset_state();
    initialized[2] = 1U;
    completion[2] = 1U;
    complete_after_waits = 3U;
    result = open_cfw_bootloader_easylogger_channel_write_41f918(
        2U, payload, 5U);
    observed_pointer = (uint32_t)descriptor_snapshot[0] |
        ((uint32_t)descriptor_snapshot[1] << 8) |
        ((uint32_t)descriptor_snapshot[2] << 16) |
        ((uint32_t)descriptor_snapshot[3] << 24);
    observed_length = (uint32_t)descriptor_snapshot[4] |
        ((uint32_t)descriptor_snapshot[5] << 8) |
        ((uint32_t)descriptor_snapshot[6] << 16) |
        ((uint32_t)descriptor_snapshot[7] << 24);
    if (result != 0U || observed_pointer != expected_pointer ||
        observed_length != 5U || descriptor_snapshot[52] != 0U ||
        completion_at_start != 0U || wait_calls != 3U ||
        wait_duration_error != 0U) {
        return 0U;
    }
    for (index = 8U; index < 56U; ++index) {
        if (descriptor_snapshot[index] != 0U) {
            return 0U;
        }
    }
    return 1U;
}

uint32_t open_cfw_test_easylogger_transport_start_failure_and_timeout(void)
{
    static const uint8_t payload[1] = {0xA5U};
    uint32_t failed;
    uint32_t timed_out;
    reset_state();
    initialized[0] = 1U;
    start_result = 7U;
    complete_after_waits = 2U;
    failed = open_cfw_bootloader_easylogger_channel_write_41f918(
        0U, payload, 1U);
    if (failed != 1U || wait_calls != 2U) {
        return 0U;
    }
    reset_state();
    initialized[3] = 1U;
    start_result = 0U;
    complete_after_waits = 0xFFFFFFFFU;
    timed_out = open_cfw_bootloader_easylogger_channel_write_41f918(
        3U, payload, 1U);
    return timed_out == 0U && wait_calls == 1000U &&
           wait_duration_error == 0U && completion[3] == 0U;
}

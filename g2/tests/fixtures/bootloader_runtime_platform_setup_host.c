#include <stdint.h>
#include <string.h>

#define OPEN_CFW_PLATFORM_SETUP_HOST 1

static uint8_t fixture_configuration[20];
static uint8_t fixture_submitted[20];
static uint32_t fixture_sequence[8];
static uint32_t fixture_sequence_length;
static uint32_t fixture_mode_first;
static uint32_t fixture_mode_second;
static uint32_t fixture_derive_bits;
static uint32_t fixture_copy_size;
static uint32_t fixture_channels[2];
static uint32_t fixture_channel_args[4];

static void record(uint32_t event)
{
    fixture_sequence[fixture_sequence_length++] = event;
}

const uint8_t *open_cfw_platform_setup_host_config(void)
{
    return fixture_configuration;
}

void open_cfw_platform_setup_host_guarded_teardown(void)
{
    record(1U);
}

void open_cfw_platform_setup_host_reset(void)
{
    record(2U);
}

void open_cfw_platform_setup_host_mode(uint32_t first, uint32_t second)
{
    fixture_mode_first = first;
    fixture_mode_second = second;
    record(3U);
}

void open_cfw_platform_setup_host_derive(uint32_t *output, float input)
{
    memcpy(&fixture_derive_bits, &input, sizeof(input));
    *output = 0x13579BDFU;
    record(4U);
}

void *open_cfw_platform_setup_host_copy(
    void *destination,
    const void *source,
    uint32_t size)
{
    fixture_copy_size = size;
    record(5U);
    return memcpy(destination, source, size);
}

void open_cfw_platform_setup_host_submit(void *configuration)
{
    memcpy(fixture_submitted, configuration, sizeof(fixture_submitted));
    record(6U);
}

void open_cfw_platform_setup_host_channel(
    uint32_t channel,
    uint32_t first,
    uint32_t second)
{
    const uint32_t index = fixture_sequence_length - 6U;
    fixture_channels[index] = channel;
    fixture_channel_args[index * 2U] = first;
    fixture_channel_args[index * 2U + 1U] = second;
    record(7U + index);
}

#include "../../components/bootloader/core_overlay/runtime_platform_setup_41fa50.c"

uint32_t open_cfw_test_platform_setup(void)
{
    uint32_t index;
    const uint32_t expected_sequence[8] = {1U, 2U, 3U, 4U, 5U, 6U, 7U, 8U};

    fixture_sequence_length = 0U;
    fixture_mode_first = 1U;
    fixture_mode_second = 1U;
    fixture_derive_bits = 0U;
    fixture_copy_size = 0U;
    memset(fixture_submitted, 0U, sizeof(fixture_submitted));
    for (index = 0U; index < sizeof(fixture_configuration); ++index) {
        fixture_configuration[index] = (uint8_t)(0xA0U + index);
    }

    open_cfw_bootloader_platform_setup_41fa50();
    return fixture_sequence_length == 8U &&
        memcmp(fixture_sequence, expected_sequence, sizeof(expected_sequence)) == 0 &&
        fixture_mode_first == 0U && fixture_mode_second == 0U &&
        fixture_derive_bits == 0x41C80000U && fixture_copy_size == 20U &&
        memcmp(fixture_submitted, fixture_configuration, 20U) == 0 &&
        fixture_channels[0] == 4U && fixture_channels[1] == 5U &&
        fixture_channel_args[0] == 0U && fixture_channel_args[1] == 0U &&
        fixture_channel_args[2] == 0U && fixture_channel_args[3] == 0U;
}

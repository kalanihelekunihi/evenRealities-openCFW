/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Native host oracle for the Apollo510 SPOT-manager initializer.
 */

#include <stdint.h>

#define OPEN_CFW_TEST_SPOTMGR_INIT_STATE_WORDS 15U
#define OPEN_CFW_TEST_SPOTMGR_INIT_MAX_EVENTS 96U

#define OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_STATE_WRITE 1U
#define OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_ACRG_READ 2U
#define OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_ACRG_WRITE 3U
#define OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_VRCTRL_READ 4U
#define OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_VRCTRL_WRITE 5U
#define OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_HANDLER_CALL 6U

uint32_t open_cfw_test_spotmgr_init_state[
    OPEN_CFW_TEST_SPOTMGR_INIT_STATE_WORDS
];
uint32_t open_cfw_test_spotmgr_init_handler_reads[
    OPEN_CFW_TEST_SPOTMGR_INIT_STATE_WORDS
];
uint32_t open_cfw_test_spotmgr_init_chip_revision;
uint32_t open_cfw_test_spotmgr_init_trim_version;
uint32_t open_cfw_test_spotmgr_init_patch_tracker0;
uint32_t open_cfw_test_spotmgr_init_acrg;
uint32_t open_cfw_test_spotmgr_init_vrctrl;
uint8_t open_cfw_test_spotmgr_init_flags[6];
uint32_t open_cfw_test_spotmgr_init_second_handler;
uint32_t open_cfw_test_spotmgr_init_override_second_handler;
uint32_t open_cfw_test_spotmgr_init_called_handler;
uint32_t open_cfw_test_spotmgr_init_call_count;
uint32_t open_cfw_test_spotmgr_init_event_count;
uint32_t open_cfw_test_spotmgr_init_event_kind[
    OPEN_CFW_TEST_SPOTMGR_INIT_MAX_EVENTS
];
uint32_t open_cfw_test_spotmgr_init_event_address[
    OPEN_CFW_TEST_SPOTMGR_INIT_MAX_EVENTS
];
uint32_t open_cfw_test_spotmgr_init_event_value[
    OPEN_CFW_TEST_SPOTMGR_INIT_MAX_EVENTS
];

static void open_cfw_test_spotmgr_init_record(
    uint32_t kind,
    uint32_t address,
    uint32_t value
)
{
    uint32_t index = open_cfw_test_spotmgr_init_event_count;

    if (index < OPEN_CFW_TEST_SPOTMGR_INIT_MAX_EVENTS) {
        open_cfw_test_spotmgr_init_event_kind[index] = kind;
        open_cfw_test_spotmgr_init_event_address[index] = address;
        open_cfw_test_spotmgr_init_event_value[index] = value;
    }
    ++open_cfw_test_spotmgr_init_event_count;
}

static uint32_t open_cfw_test_spotmgr_init_read32(uint32_t address)
{
    if (address == 0x4002000CU) {
        return open_cfw_test_spotmgr_init_chip_revision;
    }
    if (address == 0x200001E8U) {
        return open_cfw_test_spotmgr_init_trim_version;
    }
    if (address == 0x40020028U) {
        open_cfw_test_spotmgr_init_record(
            OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_ACRG_READ,
            address,
            open_cfw_test_spotmgr_init_acrg
        );
        return open_cfw_test_spotmgr_init_acrg;
    }
    if (address == 0x40020060U) {
        open_cfw_test_spotmgr_init_record(
            OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_VRCTRL_READ,
            address,
            open_cfw_test_spotmgr_init_vrctrl
        );
        return open_cfw_test_spotmgr_init_vrctrl;
    }
    return 0U;
}

static void open_cfw_test_spotmgr_init_write32(
    uint32_t address,
    uint32_t value
)
{
    if (address == 0x40020028U) {
        open_cfw_test_spotmgr_init_acrg = value;
        open_cfw_test_spotmgr_init_record(
            OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_ACRG_WRITE,
            address,
            value
        );
    }
    else if (address == 0x40020060U) {
        open_cfw_test_spotmgr_init_vrctrl = value;
        open_cfw_test_spotmgr_init_record(
            OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_VRCTRL_WRITE,
            address,
            value
        );
    }
}

static uint8_t open_cfw_test_spotmgr_init_read8(uint32_t address)
{
    if (address == 0x2007197CU) {
        return (uint8_t)open_cfw_test_spotmgr_init_patch_tracker0;
    }
    if (0x20074F64U <= address && address <= 0x20074F69U) {
        return open_cfw_test_spotmgr_init_flags[address - 0x20074F64U];
    }
    return 0U;
}

static void open_cfw_test_spotmgr_init_write8(
    uint32_t address,
    uint32_t value
)
{
    if (0x20074F64U <= address && address <= 0x20074F69U) {
        open_cfw_test_spotmgr_init_flags[address - 0x20074F64U] =
            (uint8_t)value;
    }
}

static uint32_t open_cfw_test_spotmgr_init_read_handler(uint32_t offset)
{
    uint32_t index = offset / 4U;
    uint32_t value;

    if (
        index >= OPEN_CFW_TEST_SPOTMGR_INIT_STATE_WORDS
        || (offset & 3U) != 0U
    ) {
        return 0U;
    }

    value = open_cfw_test_spotmgr_init_state[index];
    ++open_cfw_test_spotmgr_init_handler_reads[index];
    if (
        offset == 0U
        && open_cfw_test_spotmgr_init_override_second_handler != 0U
        && open_cfw_test_spotmgr_init_handler_reads[index] == 2U
    ) {
        value = open_cfw_test_spotmgr_init_second_handler;
    }
    return value;
}

static void open_cfw_test_spotmgr_init_write_handler(
    uint32_t offset,
    uint32_t value
)
{
    uint32_t index = offset / 4U;

    if (
        index >= OPEN_CFW_TEST_SPOTMGR_INIT_STATE_WORDS
        || (offset & 3U) != 0U
    ) {
        return;
    }
    open_cfw_test_spotmgr_init_state[index] = value;
    open_cfw_test_spotmgr_init_record(
        OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_STATE_WRITE,
        offset,
        value
    );
}

static uint32_t open_cfw_test_spotmgr_init_call_handler(uint32_t handler)
{
    ++open_cfw_test_spotmgr_init_call_count;
    open_cfw_test_spotmgr_init_called_handler = handler;
    open_cfw_test_spotmgr_init_record(
        OPEN_CFW_TEST_SPOTMGR_INIT_EVENT_HANDLER_CALL,
        0U,
        handler
    );
    return handler ^ 0xA5A55A5AU;
}

#define OPEN_CFW_SPOTMGR_INIT_READ32(address) \
    open_cfw_test_spotmgr_init_read32(address)
#define OPEN_CFW_SPOTMGR_INIT_WRITE32(address, value) \
    open_cfw_test_spotmgr_init_write32((address), (value))
#define OPEN_CFW_SPOTMGR_INIT_READ8(address) \
    open_cfw_test_spotmgr_init_read8(address)
#define OPEN_CFW_SPOTMGR_INIT_WRITE8(address, value) \
    open_cfw_test_spotmgr_init_write8((address), (value))
#define OPEN_CFW_SPOTMGR_INIT_READ_HANDLER(offset) \
    open_cfw_test_spotmgr_init_read_handler(offset)
#define OPEN_CFW_SPOTMGR_INIT_WRITE_HANDLER(offset, value) \
    open_cfw_test_spotmgr_init_write_handler((offset), (value))
#define OPEN_CFW_SPOTMGR_INIT_CALL_HANDLER(handler) \
    open_cfw_test_spotmgr_init_call_handler(handler)

#include "../../components/apollo_main/core_overlay/spotmgr_init.c"

void open_cfw_test_spotmgr_init_reset(void)
{
    uint32_t index;

    for (index = 0U; index < OPEN_CFW_TEST_SPOTMGR_INIT_STATE_WORDS; ++index) {
        open_cfw_test_spotmgr_init_state[index] = 0xDEADBEEFU;
        open_cfw_test_spotmgr_init_handler_reads[index] = 0U;
    }
    for (index = 0U; index < 6U; ++index) {
        open_cfw_test_spotmgr_init_flags[index] = 0xA5U;
    }
    for (index = 0U; index < OPEN_CFW_TEST_SPOTMGR_INIT_MAX_EVENTS; ++index) {
        open_cfw_test_spotmgr_init_event_kind[index] = 0U;
        open_cfw_test_spotmgr_init_event_address[index] = 0U;
        open_cfw_test_spotmgr_init_event_value[index] = 0U;
    }
    open_cfw_test_spotmgr_init_chip_revision = 0U;
    open_cfw_test_spotmgr_init_trim_version = 0U;
    open_cfw_test_spotmgr_init_patch_tracker0 = 1U;
    open_cfw_test_spotmgr_init_acrg = 0U;
    open_cfw_test_spotmgr_init_vrctrl = 0U;
    open_cfw_test_spotmgr_init_second_handler = 0U;
    open_cfw_test_spotmgr_init_override_second_handler = 0U;
    open_cfw_test_spotmgr_init_called_handler = 0U;
    open_cfw_test_spotmgr_init_call_count = 0U;
    open_cfw_test_spotmgr_init_event_count = 0U;
}


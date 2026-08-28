/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_emeeprom_clean_room.c"

typedef struct memory_backend {
    uint8_t bytes[512];
    uint32_t reads;
    uint32_t writes;
    uint32_t erases;
} memory_backend;

static uint32_t backend_read(
    void *raw, uint32_t address, uint8_t *destination, uint32_t size)
{
    memory_backend *backend = (memory_backend *)raw;
    uint32_t index;
    if (address > sizeof(backend->bytes) ||
            size > sizeof(backend->bytes) - address) return 1U;
    ++backend->reads;
    for (index = 0U; index < size; ++index) destination[index] = backend->bytes[address + index];
    return 0U;
}

static uint32_t backend_write(
    void *raw, uint32_t address, const uint8_t *source, uint32_t size)
{
    memory_backend *backend = (memory_backend *)raw;
    uint32_t index;
    if (address > sizeof(backend->bytes) ||
            size > sizeof(backend->bytes) - address) return 1U;
    ++backend->writes;
    for (index = 0U; index < size; ++index) backend->bytes[address + index] = source[index];
    return 0U;
}

static uint32_t backend_erase(
    void *raw, uint32_t address, uint32_t size)
{
    memory_backend *backend = (memory_backend *)raw;
    uint32_t index;
    if (address > sizeof(backend->bytes) ||
            size > sizeof(backend->bytes) - address) return 1U;
    ++backend->erases;
    for (index = 0U; index < size; ++index) backend->bytes[address + index] = 0xFFU;
    return 0U;
}

static open_cfw_touch_eeprom_backend provider_for(memory_backend *memory)
{
    open_cfw_touch_eeprom_backend backend = {
        backend_read, backend_write, backend_erase, memory,
    };
    return backend;
}

uint32_t open_cfw_test_touch_eeprom_simple(void)
{
    memory_backend memory = {{0U}, 0U, 0U, 0U};
    uint8_t row[64];
    open_cfw_touch_eeprom_context context = {0};
    open_cfw_touch_eeprom_backend backend = provider_for(&memory);
    open_cfw_touch_eeprom_config config = {32U, 16U, 64U, 64U, 1U, 0U};
    uint8_t input[4] = {1U, 2U, 3U, 4U};
    uint8_t output[4] = {0U};
    uint32_t descriptor = 0U;
    uint32_t result = 0U;

    context.config = config;
    context.backend = backend;
    context.row_buffer = row;
    context.row_buffer_size = sizeof(row);
    result |= open_cfw_touch_eeprom_5738_initialize_adapter(
                  &descriptor, &context) == 0U && context.initialized == 1U &&
                      open_cfw_touch_eeprom_4f00_physical_bytes(&config) == 32U
                  ? 1U : 0U;
    result |= open_cfw_touch_eeprom_write(4U, input, 4U, &context) == 0U &&
                      memory.writes == 1U ? 2U : 0U;
    result |= open_cfw_touch_eeprom_5778_read_adapter(
                  4U, output, 4U, &context) == 0U && output[0] == 1U &&
                      output[3] == 4U && memory.reads == 1U ? 4U : 0U;
    result |= open_cfw_touch_eeprom_5778_read_adapter(
                  30U, output, 4U, &context) ==
                      OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER ? 8U : 0U;
    result |= open_cfw_touch_eeprom_57e0_erase_adapter(&context) == 0U &&
                      memory.erases == 1U && memory.bytes[16] == 0xFFU
                  ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_eeprom_extended(void)
{
    memory_backend memory;
    uint8_t row[128];
    open_cfw_touch_eeprom_context context = {0};
    open_cfw_touch_eeprom_backend backend;
    open_cfw_touch_eeprom_config config = {64U, 0U, 384U, 128U, 0U, 1U};
    uint8_t first[4] = {9U, 8U, 7U, 6U};
    uint8_t second[3] = {5U, 4U, 3U};
    uint8_t output[16] = {0U};
    uint32_t index;
    uint32_t result = 0U;

    for (index = 0U; index < sizeof(memory.bytes); ++index) memory.bytes[index] = 0xFFU;
    memory.reads = 0U; memory.writes = 0U; memory.erases = 0U;
    backend = provider_for(&memory);
    context.row_buffer = row;
    context.row_buffer_size = sizeof(row);
    result |= open_cfw_touch_eeprom_568c_initialize(
                  &config, &context, &backend) == 0U &&
                      context.row_count == 3U && context.payload_per_row == 112U
                  ? 1U : 0U;
    result |= open_cfw_touch_eeprom_write(
                  8U, first, 4U, &context) == 0U &&
                      context.active_row == 1U && context.active_sequence == 1U
                  ? 2U : 0U;
    result |= open_cfw_touch_eeprom_write(
                  12U, second, 3U, &context) == 0U &&
                      context.active_row == 2U && context.active_sequence == 2U
                  ? 4U : 0U;
    result |= open_cfw_touch_eeprom_4fe0_read_extended(
                  8U, output, 7U, &context) == 0U &&
                      output[0] == 9U && output[3] == 6U &&
                      output[4] == 5U && output[6] == 3U ? 8U : 0U;

    memory.bytes[2U * 128U + 8U] ^= 1U;
    for (index = 0U; index < sizeof(output); ++index) output[index] = 0xAAU;
    result |= open_cfw_touch_eeprom_4fe0_read_extended(
                  8U, output, 7U, &context) == 0U &&
                      context.active_sequence == 1U && output[0] == 9U &&
                      output[3] == 6U && output[4] == 0xFFU ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_eeprom_primitives(void)
{
    static const uint8_t text[3] = {'a', 'b', 'c'};
    open_cfw_touch_eeprom_config config = {64U, 0U, 384U, 128U, 0U, 0U};
    open_cfw_touch_eeprom_context context = {0};
    uint8_t row[128];

    context.row_buffer = row;
    context.row_buffer_size = sizeof(row);
    return open_cfw_touch_eeprom_crc8(text, 3U) == UINT8_C(0xE2) &&
                   open_cfw_touch_eeprom_4f20_validate(&config, &context) == 0U &&
                   open_cfw_touch_eeprom_4f00_physical_bytes(&config) == 384U
               ? 1U : 0U;
}

uint32_t open_cfw_test_touch_eeprom_null_guards(void)
{
    return (open_cfw_touch_eeprom_4f20_validate(
                (const open_cfw_touch_eeprom_config *)0,
                (const open_cfw_touch_eeprom_context *)0) ==
                    OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER ? 0U : 1U) |
           (open_cfw_touch_eeprom_5778_read_adapter(
                0U, (uint8_t *)0, 0U, (void *)0) ==
                    OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER ? 0U : 1U) |
           (open_cfw_touch_eeprom_57e0_erase_adapter((void *)0) ==
                    OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER ? 0U : 1U);
}

/*
 * SPDX-License-Identifier: MIT
 *
 * Independent Emulated EEPROM implementation. This is a clean-room storage
 * contract and contains no Infineon EULA source or fixed-address flash access.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_emeeprom_clean_room.h"

enum {
    OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES = 16,
    OPEN_CFW_TOUCH_EEPROM_MAGIC = 0x4F434657,
};

static uint32_t load_le32(const uint8_t *source)
{
    return (uint32_t)source[0] | ((uint32_t)source[1] << 8U) |
           ((uint32_t)source[2] << 16U) | ((uint32_t)source[3] << 24U);
}

static void store_le32(uint8_t *destination, uint32_t value)
{
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8U);
    destination[2] = (uint8_t)(value >> 16U);
    destination[3] = (uint8_t)(value >> 24U);
}

static void copy_bytes(uint8_t *destination, const uint8_t *source,
                       uint32_t size)
{
    uint32_t index;

    for (index = 0U; index < size; ++index) {
        destination[index] = source[index];
    }
}

static void fill_bytes(uint8_t *destination, uint8_t value, uint32_t size)
{
    uint32_t index;

    for (index = 0U; index < size; ++index) {
        destination[index] = value;
    }
}

static uint32_t range_valid(uint32_t offset, uint32_t size, uint32_t limit)
{
    return offset <= limit && size <= limit - offset;
}

uint8_t open_cfw_touch_eeprom_crc8(const uint8_t *data, uint32_t size)
{
    uint8_t checksum = UINT8_C(0xFF);
    uint32_t index;
    uint32_t bit;

    if (data == NULL && size != 0U) {
        return 0U;
    }
    for (index = 0U; index < size; ++index) {
        checksum ^= data[index];
        for (bit = 0U; bit < 8U; ++bit) {
            checksum = (checksum & UINT8_C(0x80)) != 0U
                ? (uint8_t)((uint8_t)(checksum << 1U) ^ UINT8_C(0x31))
                : (uint8_t)(checksum << 1U);
        }
    }
    return checksum;
}

uint32_t open_cfw_touch_eeprom_4f00_physical_bytes(
    const open_cfw_touch_eeprom_config *config)
{
    if (config == NULL) {
        return 0U;
    }
    if (config->simple_mode != 0U) {
        return config->logical_size;
    }
    return config->physical_size;
}

uint32_t open_cfw_touch_eeprom_4f20_validate(
    const open_cfw_touch_eeprom_config *config,
    const open_cfw_touch_eeprom_context *context)
{
    if (config == NULL || context == NULL || config->logical_size == 0U ||
            config->physical_size == 0U || config->row_size < 32U ||
            config->row_size > context->row_buffer_size ||
            config->simple_mode > 1U || config->redundant_copy > 1U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    if (config->simple_mode != 0U) {
        return config->logical_size <= config->physical_size
            ? OPEN_CFW_TOUCH_EEPROM_SUCCESS
            : OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    if (config->physical_size % config->row_size != 0U ||
            config->row_size <= OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES ||
            config->logical_size >
                config->row_size - OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    return OPEN_CFW_TOUCH_EEPROM_SUCCESS;
}

uint32_t open_cfw_touch_eeprom_4f8c_geometry(
    open_cfw_touch_eeprom_context *context)
{
    if (context == NULL || context->config.row_size == 0U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    context->row_count = (uint16_t)(
        context->config.physical_size / context->config.row_size);
    context->payload_per_row = context->config.simple_mode != 0U
        ? context->config.row_size
        : (uint16_t)(context->config.row_size -
                     OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES);
    if (context->row_count == 0U || context->payload_per_row == 0U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    return OPEN_CFW_TOUCH_EEPROM_SUCCESS;
}

uint32_t open_cfw_touch_eeprom_4b44_read_simple(
    uint32_t offset, uint8_t *destination, uint32_t size,
    open_cfw_touch_eeprom_context *context)
{
    uint32_t status;

    if (context == NULL || destination == NULL || context->initialized == 0U ||
            context->backend.read == NULL ||
            range_valid(offset, size, context->config.logical_size) == 0U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    status = context->backend.read(
        context->backend.context, context->config.physical_base + offset,
        destination, size);
    return status == 0U ? OPEN_CFW_TOUCH_EEPROM_SUCCESS
                        : OPEN_CFW_TOUCH_EEPROM_WRITE_FAILED;
}

uint32_t open_cfw_touch_eeprom_4c08_write_range(
    uint32_t address, const uint8_t *source, uint32_t size,
    open_cfw_touch_eeprom_context *context)
{
    uint32_t status;

    if (context == NULL || source == NULL || context->backend.write == NULL ||
            address < context->config.physical_base ||
            range_valid(address - context->config.physical_base, size,
                        context->config.physical_size) == 0U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    status = context->backend.write(
        context->backend.context, address, source, size);
    return status == 0U ? OPEN_CFW_TOUCH_EEPROM_SUCCESS
                        : OPEN_CFW_TOUCH_EEPROM_WRITE_FAILED;
}

uint32_t open_cfw_touch_eeprom_560c_write_row(
    uint32_t row_index, uint32_t sequence, const uint8_t *payload,
    open_cfw_touch_eeprom_context *context)
{
    uint8_t *row;
    uint32_t address;
    uint32_t status;

    if (context == NULL || payload == NULL || row_index >= context->row_count ||
            context->row_buffer == NULL ||
            context->row_buffer_size < context->config.row_size) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    row = context->row_buffer;
    if (payload == row) {
        uint32_t index = context->config.logical_size;
        while (index != 0U) {
            --index;
            row[OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES + index] = row[index];
        }
        fill_bytes(row, UINT8_C(0xFF), OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES);
        fill_bytes(&row[OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES +
                        context->config.logical_size],
                   UINT8_C(0xFF), context->config.row_size -
                       OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES -
                       context->config.logical_size);
    } else {
        fill_bytes(row, UINT8_C(0xFF), context->config.row_size);
        copy_bytes(&row[OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES], payload,
                   context->config.logical_size);
    }
    store_le32(&row[0], OPEN_CFW_TOUCH_EEPROM_MAGIC);
    store_le32(&row[4], sequence);
    row[8] = open_cfw_touch_eeprom_crc8(
        &row[OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES], context->config.logical_size);
    address = context->config.physical_base +
              row_index * context->config.row_size;
    status = open_cfw_touch_eeprom_4c08_write_range(
        address, row, context->config.row_size, context);
    if (status == OPEN_CFW_TOUCH_EEPROM_SUCCESS) {
        context->active_row = row_index;
        context->active_sequence = sequence;
    }
    return status;
}

static uint32_t load_valid_row(
    uint32_t row_index, open_cfw_touch_eeprom_context *context,
    uint32_t *sequence)
{
    uint8_t *row = context->row_buffer;
    uint32_t status = context->backend.read(
        context->backend.context,
        context->config.physical_base + row_index * context->config.row_size,
        row, context->config.row_size);

    if (status != 0U || load_le32(&row[0]) != OPEN_CFW_TOUCH_EEPROM_MAGIC ||
            row[8] != open_cfw_touch_eeprom_crc8(
                &row[OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES],
                context->config.logical_size)) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_CHECKSUM;
    }
    *sequence = load_le32(&row[4]);
    return OPEN_CFW_TOUCH_EEPROM_SUCCESS;
}

uint32_t open_cfw_touch_eeprom_4fe0_read_extended(
    uint32_t offset, uint8_t *destination, uint32_t size,
    open_cfw_touch_eeprom_context *context)
{
    uint32_t row_index;
    uint32_t best_row = 0U;
    uint32_t best_sequence = 0U;
    uint32_t found = 0U;

    if (context == NULL || destination == NULL || context->initialized == 0U ||
            context->backend.read == NULL || context->row_buffer == NULL ||
            range_valid(offset, size, context->config.logical_size) == 0U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    for (row_index = 0U; row_index < context->row_count; ++row_index) {
        uint32_t sequence;
        if (load_valid_row(row_index, context, &sequence) == 0U &&
                (found == 0U || (int32_t)(sequence - best_sequence) > 0)) {
            found = 1U;
            best_row = row_index;
            best_sequence = sequence;
        }
    }
    if (found == 0U ||
            load_valid_row(best_row, context, &best_sequence) != 0U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_CHECKSUM;
    }
    copy_bytes(destination,
               &context->row_buffer[OPEN_CFW_TOUCH_EEPROM_HEADER_BYTES + offset],
               size);
    context->active_row = best_row;
    context->active_sequence = best_sequence;
    return OPEN_CFW_TOUCH_EEPROM_SUCCESS;
}

uint32_t open_cfw_touch_eeprom_568c_initialize(
    const open_cfw_touch_eeprom_config *config,
    open_cfw_touch_eeprom_context *context,
    const open_cfw_touch_eeprom_backend *backend)
{
    uint32_t status;

    if (config == NULL || context == NULL || backend == NULL ||
            backend->read == NULL || backend->write == NULL ||
            backend->erase == NULL || context->row_buffer == NULL) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    context->config = *config;
    context->backend = *backend;
    context->active_sequence = 0U;
    context->active_row = 0U;
    context->initialized = 0U;
    status = open_cfw_touch_eeprom_4f20_validate(config, context);
    if (status != 0U) {
        return status;
    }
    status = open_cfw_touch_eeprom_4f8c_geometry(context);
    if (status == 0U) {
        context->initialized = 1U;
    }
    return status;
}

uint32_t open_cfw_touch_eeprom_write(
    uint32_t offset, const uint8_t *source, uint32_t size,
    open_cfw_touch_eeprom_context *context)
{
    uint32_t status;

    if (context == NULL || source == NULL || context->initialized == 0U ||
            range_valid(offset, size, context->config.logical_size) == 0U) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    if (context->config.simple_mode != 0U) {
        return open_cfw_touch_eeprom_4c08_write_range(
            context->config.physical_base + offset, source, size, context);
    }
    fill_bytes(context->row_buffer, 0U, context->config.logical_size);
    status = open_cfw_touch_eeprom_4fe0_read_extended(
        0U, context->row_buffer, context->config.logical_size, context);
    if (status != 0U && status != OPEN_CFW_TOUCH_EEPROM_BAD_CHECKSUM) {
        return status;
    }
    copy_bytes(&context->row_buffer[offset], source, size);
    return open_cfw_touch_eeprom_560c_write_row(
        (context->active_row + 1U) % context->row_count,
        context->active_sequence + 1U, context->row_buffer, context);
}

uint32_t open_cfw_touch_eeprom_5738_initialize_adapter(
    uint32_t *descriptor, void *raw_context)
{
    open_cfw_touch_eeprom_context *context =
        (open_cfw_touch_eeprom_context *)raw_context;

    (void)descriptor;
    if (context == NULL) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    return open_cfw_touch_eeprom_568c_initialize(
        &context->config, context, &context->backend);
}

uint32_t open_cfw_touch_eeprom_5778_read_adapter(
    uint32_t offset, uint8_t *destination, uint32_t size, void *raw_context)
{
    open_cfw_touch_eeprom_context *context =
        (open_cfw_touch_eeprom_context *)raw_context;

    if (context == NULL) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    return context->config.simple_mode != 0U
        ? open_cfw_touch_eeprom_4b44_read_simple(
              offset, destination, size, context)
        : open_cfw_touch_eeprom_4fe0_read_extended(
              offset, destination, size, context);
}

uint32_t open_cfw_touch_eeprom_57e0_erase_adapter(void *raw_context)
{
    open_cfw_touch_eeprom_context *context =
        (open_cfw_touch_eeprom_context *)raw_context;
    uint32_t status;

    if (context == NULL || context->initialized == 0U ||
            context->backend.erase == NULL) {
        return OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER;
    }
    status = context->backend.erase(
        context->backend.context, context->config.physical_base,
        context->config.physical_size);
    if (status != 0U) {
        return OPEN_CFW_TOUCH_EEPROM_WRITE_FAILED;
    }
    context->active_row = 0U;
    context->active_sequence = 0U;
    return OPEN_CFW_TOUCH_EEPROM_SUCCESS;
}

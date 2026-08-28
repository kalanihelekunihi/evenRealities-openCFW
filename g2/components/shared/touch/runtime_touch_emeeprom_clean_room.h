/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_TOUCH_EMEEPROM_CLEAN_ROOM_H
#define OPEN_CFW_RUNTIME_TOUCH_EMEEPROM_CLEAN_ROOM_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TOUCH_EEPROM_SUCCESS UINT32_C(0)
#define OPEN_CFW_TOUCH_EEPROM_BAD_CHECKSUM UINT32_C(0x093E0001)
#define OPEN_CFW_TOUCH_EEPROM_WRITE_FAILED UINT32_C(0x093E0002)
#define OPEN_CFW_TOUCH_EEPROM_BAD_PARAMETER UINT32_C(0x093E0003)
#define OPEN_CFW_TOUCH_EEPROM_ACCEPTED UINT32_C(0x093E0004)

typedef struct open_cfw_touch_eeprom_backend {
    uint32_t (*read)(void *context, uint32_t address,
                     uint8_t *destination, uint32_t size);
    uint32_t (*write)(void *context, uint32_t address,
                      const uint8_t *source, uint32_t size);
    uint32_t (*erase)(void *context, uint32_t address, uint32_t size);
    void *context;
} open_cfw_touch_eeprom_backend;

typedef struct open_cfw_touch_eeprom_config {
    uint32_t logical_size;
    uint32_t physical_base;
    uint32_t physical_size;
    uint16_t row_size;
    uint8_t simple_mode;
    uint8_t redundant_copy;
} open_cfw_touch_eeprom_config;

typedef struct open_cfw_touch_eeprom_context {
    open_cfw_touch_eeprom_config config;
    open_cfw_touch_eeprom_backend backend;
    uint8_t *row_buffer;
    uint32_t row_buffer_size;
    uint32_t active_sequence;
    uint32_t active_row;
    uint16_t payload_per_row;
    uint16_t row_count;
    uint8_t initialized;
} open_cfw_touch_eeprom_context;

uint8_t open_cfw_touch_eeprom_crc8(const uint8_t *data, uint32_t size);
uint32_t open_cfw_touch_eeprom_4f00_physical_bytes(
    const open_cfw_touch_eeprom_config *config);
uint32_t open_cfw_touch_eeprom_4f20_validate(
    const open_cfw_touch_eeprom_config *config,
    const open_cfw_touch_eeprom_context *context);
uint32_t open_cfw_touch_eeprom_4f8c_geometry(
    open_cfw_touch_eeprom_context *context);
uint32_t open_cfw_touch_eeprom_4b44_read_simple(
    uint32_t offset, uint8_t *destination, uint32_t size,
    open_cfw_touch_eeprom_context *context);
uint32_t open_cfw_touch_eeprom_4c08_write_range(
    uint32_t address, const uint8_t *source, uint32_t size,
    open_cfw_touch_eeprom_context *context);
uint32_t open_cfw_touch_eeprom_560c_write_row(
    uint32_t row_index, uint32_t sequence, const uint8_t *payload,
    open_cfw_touch_eeprom_context *context);
uint32_t open_cfw_touch_eeprom_4fe0_read_extended(
    uint32_t offset, uint8_t *destination, uint32_t size,
    open_cfw_touch_eeprom_context *context);
uint32_t open_cfw_touch_eeprom_568c_initialize(
    const open_cfw_touch_eeprom_config *config,
    open_cfw_touch_eeprom_context *context,
    const open_cfw_touch_eeprom_backend *backend);
uint32_t open_cfw_touch_eeprom_write(
    uint32_t offset, const uint8_t *source, uint32_t size,
    open_cfw_touch_eeprom_context *context);
uint32_t open_cfw_touch_eeprom_5738_initialize_adapter(
    uint32_t *descriptor, void *context);
uint32_t open_cfw_touch_eeprom_5778_read_adapter(
    uint32_t offset, uint8_t *destination, uint32_t size, void *context);
uint32_t open_cfw_touch_eeprom_57e0_erase_adapter(void *context);

#endif

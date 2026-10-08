#ifndef OPENCFW_TOUCH_FLASH_PROVIDER_H
#define OPENCFW_TOUCH_FLASH_PROVIDER_H
#include <stdint.h>
typedef struct {
 uint16_t logical_rows, physical_row_bytes;
 uint32_t step_bytes, logical_capacity;
 uint8_t wear_factor, simple_mode, redundant_copy, program_mode;
 uint32_t physical_base;
 uint16_t historic_capacity, payload_capacity;
 uint32_t last_written_row, provider_address;
} touch_eeprom_context_layout;
_Static_assert(sizeof(touch_eeprom_context_layout)==32,"stock context size");
_Static_assert(__builtin_offsetof(touch_eeprom_context_layout,provider_address)==28,"provider offset");
uint32_t touch_flash_status(void);
uint32_t touch_flash_write_row(uint32_t address,const uint8_t *data);
uint32_t touch_storage_copy(uint32_t handle,uint32_t address,uint32_t size,uint8_t *data);
uint32_t touch_storage_zero(uint32_t handle,uint32_t address,uint32_t size);
uint32_t touch_storage_program(uint32_t handle,uint32_t address,uint32_t size,const uint8_t *data);
uint32_t touch_eeprom_program_gate(uint32_t address,const uint8_t *data,const uint8_t *context);
uint32_t touch_storage_no_erase(uint32_t handle,uint32_t address,uint32_t size);
/* Borrowed input RAM, synthetic SROM comparison only. Return0 from stock row
 * adapters does not prove programming: underlying errors are discarded. */
#endif

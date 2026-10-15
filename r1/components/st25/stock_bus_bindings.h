#ifndef R1_ST25_STOCK_BUS_BINDINGS_H
#define R1_ST25_STOCK_BUS_BINDINGS_H
#include <stdint.h>
/* Stock board/resource seams. Their implementations remain separate providers. */
void r1_i2c5_nfc_resource_acquire(void);
void r1_i2c5_nfc_resource_release(void);
void r1_st25_delay_ms(uint32_t milliseconds);
int32_t r1_i2c5_read_transfer(uint8_t address, uint16_t reg, uint8_t *data, uint16_t length);
int32_t r1_i2c5_write_transfer(uint8_t address, uint16_t reg, const uint8_t *data, uint16_t length);

int32_t r1_st25dvxxkc_bus_initialize(void);
int32_t r1_st25dvxxkc_bus_deinitialize(void);
int32_t r1_st25dvxxkc_bus_is_ready(uint16_t address, uint32_t trials);
int32_t r1_st25dvxxkc_bus_read(uint16_t address, uint16_t reg, uint8_t *data, uint16_t length);
int32_t r1_st25dvxxkc_bus_write(uint16_t address, uint16_t reg, const uint8_t *data, uint16_t length);
int32_t r1_st25dvxxkc_bus_tick_get(void);
int32_t r1_st25dvxxkc_register_provider(void);
#endif

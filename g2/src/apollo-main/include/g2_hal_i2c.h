/* Product I2C HAL (stock driver/hal/src/hal_i2c.c, native 0x50412c..0x50475b).
 *
 * Eight logical buses map one-to-one onto Apollo510 IOM modules. Every call
 * takes the per-bus mutex, wakes the IOM, runs one or two blocking AmbiqSuite
 * transactions and puts the IOM back to deep sleep. All transfer entry points
 * return 0 on success and 1 on any failure (bad bus, IOM error, sleep error). */
#ifndef G2_HAL_I2C_H
#define G2_HAL_I2C_H

#include <stdint.h>

#define G2_HAL_I2C_BUS_COUNT 8u
#define G2_HAL_I2C_JOINED_MAX 32u

void hal_i2c_irq_enable(int16_t irq);
uint32_t hal_i2c_power_down(uint8_t bus);
uint32_t hal_i2c_power_up(uint8_t bus);
uint32_t HAL_I2CInit(void);
uint32_t hal_i2c_transfer_full(uint8_t bus, uint8_t addr,
                               const void *tx, uint32_t tx_len,
                               void *rx, uint32_t rx_len);
void hal_i2c_irq_handler(void);
uint32_t hal_i2c_transfer_joined(uint8_t bus, uint8_t addr,
                                 const void *head, uint32_t head_len,
                                 const void *body, uint32_t body_len);
uint32_t hal_i2c_transfer_read(uint8_t bus, uint8_t addr, void *rx, uint32_t len);
uint32_t hal_i2c_transfer_write(uint8_t bus, uint8_t addr, const void *tx, uint32_t len);

#endif

/* Native static mailbox-mode update, stock 0x5d1f4.
 * Successful register reads supply one byte. Initialize the private byte so a
 * malformed success-without-data provider cannot expose uninitialized C data. */
#include <stdint.h>
#include "stock_bus_bindings.h"

uint32_t r1_st25_mailbox_mode_enable_native(uint32_t enabled)
{
    uint8_t value = 0;
    uint32_t status = (uint32_t)r1_i2c5_read_transfer(0xae, 0x0d, &value, 1);
    if (status != 0)
        return status;
    value = (uint8_t)((value & 0xfeu) | (enabled & 1u));
    r1_st25_delay_ms(5);
    return (uint32_t)r1_i2c5_write_transfer(0xae, 0x0d, &value, 1);
}

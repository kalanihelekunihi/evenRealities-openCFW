#ifndef OPENCFW_TOUCH_I2C_BOUNDED_ABI_H
#define OPENCFW_TOUCH_I2C_BOUNDED_ABI_H
#include <stdint.h>
#include <stddef.h>
/* Independent explicit layout for the tested locked touch init interface.
 * Public PDL small-enum config matches this24-byte layout; the context is84.
 * No physical controller operations or production address binding here. */
typedef struct {
 uint8_t mode;                 /*1 slave,2 master,3 combined*/
 uint8_t use_rx_fifo, use_tx_fifo, slave_address, slave_address_mask;
 uint8_t accept_address_in_fifo, ack_general_address, hs_enable;
 uint8_t wake_from_sleep, digital_filter, reserved10[2];
 uint32_t low_phase_count, high_phase_count;
 uint16_t address_fifo_delay; uint8_t reserved22[2];
} OpenCfwTouchI2cConfig;
typedef struct { uint8_t opaque[84]; } OpenCfwTouchI2cContext;
_Static_assert(sizeof(OpenCfwTouchI2cConfig)==24,"touch config ABI");
_Static_assert(offsetof(OpenCfwTouchI2cConfig,low_phase_count)==12,"phase ABI");
_Static_assert(offsetof(OpenCfwTouchI2cConfig,address_fifo_delay)==20,"delay ABI");
/* Context offsets recovered and compared for init only. Preserve the whole
 * context across driver calls; no callback/IRQ ownership safety inferred. */
enum { OPENCFW_TOUCH_I2C_STATE=4, OPENCFW_TOUCH_I2C_MASTER_STATUS=8,
 OPENCFW_TOUCH_I2C_SLAVE_STATUS=32, OPENCFW_TOUCH_I2C_EVENT_CALLBACK=68,
 OPENCFW_TOUCH_I2C_ADDRESS_CALLBACK=72, OPENCFW_TOUCH_I2C_HS_CALLBACK=76,
 OPENCFW_TOUCH_I2C_ADDRESS_DELAY=80 };
#endif

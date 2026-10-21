#ifndef R1_I2C5_STOCK_TRANSPORT_H
#define R1_I2C5_STOCK_TRANSPORT_H
#include "generic_device_registry/generic_device_registry.h"
#include "../st25/stock_bus_bindings.h"
/* Fixed target layout: GPO device 0x20006838, bus device 0x2000683C,
 * shared request 0x20006840. Board discovery still owns initial binding. */
typedef struct {
    generic_device_registry_device *gpo;
    generic_device_registry_device *bus;
    generic_device_registry_request_block request;
} r1_i2c5_stock_state;
extern r1_i2c5_stock_state r1_i2c5_state;
extern generic_device_registry_device *r1_vnfc_rect_adc_device;
void r1_vnfc_rect_adc_handle_cache(void);
void r1_i2c5_nfc_resource_registration(void);
#endif

#ifndef R1_STOCK_TWI_RECORDS_H
#define R1_STOCK_TWI_RECORDS_H
#include "software_twi/software_twi.h"
#include "../registry/stock_registry.h"
typedef uint32_t (*r1_twi_lifecycle_op)(generic_device_registry_device *device);
typedef struct {
    uintptr_t reserved_00, reserved_04;
    r1_twi_lifecycle_op open, close;
    generic_device_registry_operation read, write;
    uintptr_t reserved_18, reserved_1c, reserved_20;
} r1_twi_native_ops;
typedef struct {
    const char *name;
    uint8_t opened;
    uint8_t reserved[3];
    software_twi_engine engine;
    software_twi_pin_op_fn pin_release;
    generic_device_registry_device device;
    r1_twi_native_ops ops;
} r1_stock_twi_record;
extern r1_stock_twi_record r1_stock_twi_records[4];
uint32_t r1_stock_i2c2_register(void);
uint32_t r1_stock_i2c3_register(void);
uint32_t r1_stock_i2c4_register(void);
uint32_t r1_stock_i2c5_register(void);
uint32_t r1_stock_i2c2_open(generic_device_registry_device *device);
uint32_t r1_stock_i2c2_close(generic_device_registry_device *device);
uint32_t r1_stock_i2c3_open(generic_device_registry_device *device);
uint32_t r1_stock_i2c3_close(generic_device_registry_device *device);
uint32_t r1_stock_i2c4_open(generic_device_registry_device *device);
uint32_t r1_stock_i2c4_close(generic_device_registry_device *device);
uint32_t r1_stock_i2c5_open(generic_device_registry_device *device);
uint32_t r1_stock_i2c5_close(generic_device_registry_device *device);
uint32_t r1_stock_i2c2_read(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
uint32_t r1_stock_i2c2_write(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
uint32_t r1_stock_i2c3_read(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
uint32_t r1_stock_i2c3_write(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
uint32_t r1_stock_i2c4_read(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
uint32_t r1_stock_i2c4_write(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
uint32_t r1_stock_i2c5_read(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
uint32_t r1_stock_i2c5_write(generic_device_registry_device *device,uintptr_t operation,uintptr_t request,uintptr_t extra);
#endif

#ifndef R1_NATIVE_HW_TWI_H
#define R1_NATIVE_HW_TWI_H

#include <stddef.h>
#include <stdint.h>
#include "../registry/stock_registry.h"

/* Operation slots bind the existing register-sensitive bridges. Their C
 * declarations describe those definitions, not a generic callable packet ABI. */
typedef void (*r1_hw_twi_irq_metadata_fn)(void);
typedef struct {
    uintptr_t reserved_00, reserved_04;
    uint32_t (*open)(void), (*close)(void);
    uint32_t (*read)(uint32_t device, uint32_t operation, const void *request);
    uint32_t (*write)(uint32_t device, uint32_t operation, const void *request);
    uintptr_t reserved_18, reserved_1c, reserved_20;
} r1_hw_twi_operations;

typedef struct {
    uint8_t state_00, state_01, state_02, padding;
    void *semaphore;
    uint32_t reserved_08;
} r1_hw_twi_control;

typedef struct {
    const char *name;
    uint8_t opened, padding[3];
    uint32_t pin_08, pin_0c, instance_id;
    uintptr_t peripheral;
    uint32_t driver_index, use_dma;
    /* Native helper and Nordic callback signatures differ. This is an opaque
     * binding, not a declaration that either signature is interchangeable. */
    r1_hw_twi_irq_metadata_fn irq;
    generic_device_registry_device device;
    r1_hw_twi_operations ops;
} r1_hw_twi_record;

typedef struct {
    r1_hw_twi_control control;
    r1_hw_twi_record record;
} r1_hw_twi_cluster;

_Static_assert(sizeof(r1_hw_twi_control) == 12, "native TWI control extent");
_Static_assert(sizeof(r1_hw_twi_operations) == 36, "native operation extent");
_Static_assert(offsetof(r1_hw_twi_operations, open) == 8, "native open slot");
_Static_assert(offsetof(r1_hw_twi_operations, read) == 16, "native read slot");
_Static_assert(offsetof(r1_hw_twi_operations, write) == 20, "native write slot");
_Static_assert(offsetof(r1_hw_twi_control, semaphore) == 4, "native semaphore");
_Static_assert(offsetof(r1_hw_twi_control, reserved_08) == 8, "native result");
_Static_assert(sizeof(r1_hw_twi_record) == 96, "native TWI record extent");
_Static_assert(offsetof(r1_hw_twi_record, irq) == 32, "native IRQ slot");
_Static_assert(offsetof(r1_hw_twi_record, device) == 36, "native device slot");
_Static_assert(offsetof(r1_hw_twi_record, ops) == 60, "native operations");
_Static_assert(offsetof(r1_hw_twi_cluster, record) == 12, "native record offset");
_Static_assert(sizeof(r1_hw_twi_cluster) == 108, "native cluster extent");

extern r1_hw_twi_cluster r1_hw_twi0, r1_hw_twi1;
uint32_t r1_hw_twi0_open(void), r1_hw_twi0_close(void);
uint32_t r1_hw_twi1_open(void), r1_hw_twi1_close(void);
uint32_t r1_hw_twi0_read(uint32_t device, uint32_t operation, const void *request);
uint32_t r1_hw_twi0_write(uint32_t device, uint32_t operation, const void *request);
uint32_t r1_hw_twi1_read(uint32_t device, uint32_t operation, const void *request);
uint32_t r1_hw_twi1_write(uint32_t device, uint32_t operation, const void *request);
uint32_t r1_hw_twi0_irq(const volatile uint8_t *event);
uint32_t r1_hw_twi1_irq(const volatile uint8_t *event);
uint32_t r1_twi_primary_device_binding_configuration(void);
uint32_t r1_twi_secondary_device_binding_configuration(void);

#endif

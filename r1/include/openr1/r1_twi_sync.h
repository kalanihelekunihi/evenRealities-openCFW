#ifndef OPENR1_R1_TWI_SYNC_H
#define OPENR1_R1_TWI_SYNC_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_TWI_SYNC_DELAY_US 64u
#define R1_TWI_SYNC_STATUS_OK 0u
#define R1_TWI_SYNC_STATUS_ARGUMENT 1u
#define R1_TWI_SYNC_STATUS_ADDRESS_NACK 5u
#define R1_TWI_SYNC_STATUS_DATA_NACK 7u
#define R1_TWI_SYNC_STATUS_DATA_SIZE 9u
#define R1_TWI_SYNC_STATUS_TIMEOUT 13u
#define R1_TWI_SYNC_STATUS_BUSY 17u
#define R1_TWI_WRITE_DATA_MAX 80u

typedef enum {
    R1_TWI_SYNC_EVENT_DONE = 0,
    R1_TWI_SYNC_EVENT_ADDRESS_NACK = 1,
    R1_TWI_SYNC_EVENT_DATA_NACK = 2
} r1_twi_sync_event;

typedef struct {
    bool completed;
    bool failed;
    bool semaphore_enabled;
    void *semaphore;
    uint32_t status;
} r1_twi_sync_state;

typedef uint32_t (*r1_twi_sync_kernel_state_fn)(void *context);
typedef uint32_t (*r1_twi_sync_tick_frequency_fn)(void *context);
typedef int32_t (*r1_twi_sync_semaphore_acquire_fn)(
    void *context, void *semaphore, uint32_t ticks);
typedef void (*r1_twi_sync_semaphore_release_fn)(
    void *context, void *semaphore);
typedef void (*r1_twi_sync_delay_us_fn)(void *context, uint32_t microseconds);

typedef struct {
    void *context;
    r1_twi_sync_kernel_state_fn kernel_state;
    r1_twi_sync_tick_frequency_fn tick_frequency;
    r1_twi_sync_semaphore_acquire_fn semaphore_acquire;
    r1_twi_sync_semaphore_release_fn semaphore_release;
    r1_twi_sync_delay_us_fn delay_us;
} r1_twi_sync_ops;

typedef uint32_t (*r1_twi_transfer_transmit_fn)(
    void *context, void *bus, uint8_t address, const uint8_t *data,
    uint32_t length, bool no_stop);
typedef uint32_t (*r1_twi_transfer_receive_fn)(
    void *context, void *bus, uint8_t address, uint8_t *data,
    uint32_t length);
typedef void (*r1_twi_transfer_fatal_error_fn)(void *context, uint32_t status);

typedef struct {
    void *context;
    r1_twi_transfer_transmit_fn transmit;
    r1_twi_transfer_receive_fn receive;
    r1_twi_transfer_fatal_error_fn fatal_error;
    const r1_twi_sync_ops *sync;
} r1_twi_transfer_ops;

typedef struct {
    uint32_t scl_pin;
    uint32_t sda_pin;
    uint32_t frequency;
    uint8_t interrupt_priority;
    bool clear_bus_init;
    bool hold_bus_uninit;
    bool preconfigure_pins;
} r1_twi_lifecycle_config;

typedef struct {
    bool initialized;
    r1_twi_sync_state *transfer_state;
} r1_twi_lifecycle_state;

typedef void (*r1_twi_lifecycle_configure_pin_fn)(
    void *context, uint32_t pin);
typedef uint32_t (*r1_twi_lifecycle_initialize_fn)(
    void *context, void *bus, const r1_twi_lifecycle_config *config,
    r1_twi_sync_state *transfer_state);
typedef void (*r1_twi_lifecycle_bus_fn)(void *context, void *bus);

typedef struct {
    void *context;
    r1_twi_lifecycle_configure_pin_fn configure_pin;
    r1_twi_lifecycle_initialize_fn initialize;
    r1_twi_lifecycle_bus_fn enable;
    r1_twi_lifecycle_bus_fn disable;
    r1_twi_lifecycle_bus_fn uninitialize;
    r1_twi_lifecycle_bus_fn power_cycle;
} r1_twi_lifecycle_ops;

typedef struct {
    bool initialized;
    uint32_t scl_pin;
    uint32_t sda_pin;
} r1_twi_software_lifecycle_state;

typedef void (*r1_twi_software_release_pin_fn)(
    void *context, uint32_t pin);

typedef struct {
    void *context;
    r1_twi_software_release_pin_fn release_pin;
} r1_twi_software_lifecycle_ops;

r1_error r1_twi_sync_complete(
    r1_twi_sync_state *state, uint8_t event_type,
    const r1_twi_sync_ops *ops);

uint32_t r1_twi_sync_wait(
    r1_twi_sync_state *state, uint32_t timeout_ms,
    const r1_twi_sync_ops *ops);

uint32_t r1_twi_primary_register_read(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops);
uint32_t r1_twi_primary_register_write(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    const uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops);
uint32_t r1_twi_secondary_register_read(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops);
uint32_t r1_twi_secondary_register_write(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    const uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops);
uint32_t r1_twi_lifecycle_initialize(
    r1_twi_lifecycle_state *state, void *bus,
    const r1_twi_lifecycle_config *config,
    const r1_twi_lifecycle_ops *ops);
uint32_t r1_twi_primary_lifecycle_initialize(
    r1_twi_lifecycle_state *state, void *bus,
    uint32_t scl_pin, uint32_t sda_pin,
    const r1_twi_lifecycle_ops *ops);
uint32_t r1_twi_secondary_lifecycle_initialize(
    r1_twi_lifecycle_state *state, void *bus,
    uint32_t scl_pin, uint32_t sda_pin,
    const r1_twi_lifecycle_ops *ops);
uint32_t r1_twi_lifecycle_shutdown(
    r1_twi_lifecycle_state *state, void *bus,
    const r1_twi_lifecycle_ops *ops);
uint32_t r1_twi_software_lifecycle_shutdown(
    r1_twi_software_lifecycle_state *state,
    const r1_twi_software_lifecycle_ops *ops);
void r1_twi_i2c5_delay_noop(uint32_t delay_units);

#endif

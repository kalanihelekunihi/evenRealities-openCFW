/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPENCFW_TOUCH_CAT2_ADAPTERS_H
#define OPENCFW_TOUCH_CAT2_ADAPTERS_H

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_TOUCH_SYSTICK_CALLBACKS 5u
#define OPEN_CFW_TOUCH_SYSTICK_COUNTFLAG (1u << 16)
#define OPEN_CFW_TOUCH_SYSTICK_CLKSOURCE (1u << 2)
#define OPEN_CFW_TOUCH_SYSTICK_TICKINT (1u << 1)
#define OPEN_CFW_TOUCH_SYSTICK_ENABLE (1u << 0)

typedef void (*open_cfw_touch_cat2_void_fn)(void);
typedef int (*open_cfw_touch_cat2_syspm_fn)(uint32_t type, void *context);
typedef int (*open_cfw_touch_cat2_flash_write_fn)(
    uint32_t row_address, const uint32_t *data, void *context);
typedef int (*open_cfw_touch_cat2_gpio_pin_init_fn)(
    void *base, uint32_t pin, const void *config, void *context);
typedef void (*open_cfw_touch_cat2_i2c_irq_fn)(
    void *base, void *i2c_context, void *provider_context);
typedef uint32_t (*open_cfw_touch_cat2_scb_read_fn)(
    const void *base, void *buffer, uint32_t size, void *context);
typedef uint32_t (*open_cfw_touch_cat2_scb_write_fn)(
    void *base, const void *buffer, uint32_t data, uint32_t size,
    void *context);
typedef int (*open_cfw_touch_cat2_scb_level_fn)(
    void *base, uint32_t level, void *context);
typedef int (*open_cfw_touch_cat2_gpio_value_fn)(
    void *base, uint32_t pin, uint32_t value, void *context);
typedef int (*open_cfw_touch_cat2_sysclk_fn)(
    uint32_t operation, uint32_t argument0, uint32_t argument1,
    uint32_t *result, void *context);
typedef int (*open_cfw_touch_cat2_msclp_fn)(
    void *base, const void *config, uint32_t key, void *context);
typedef void (*open_cfw_touch_cat2_i2c_helper_fn)(
    void *base, uint32_t flag, void *i2c_context, void *provider_context);
typedef int (*open_cfw_touch_cat2_register_callback_fn)(
    void *callback_record, void *context);
typedef int (*open_cfw_touch_cat2_system_halt_fn)(void *context);

typedef struct {
    uint32_t ctrl;
    uint32_t load;
    uint32_t val;
    open_cfw_touch_cat2_void_fn callbacks[OPEN_CFW_TOUCH_SYSTICK_CALLBACKS];
    open_cfw_touch_cat2_void_fn vector;
} open_cfw_touch_cat2_systick;

int open_cfw_touch_cat2_delay_us(
    uint16_t microseconds, uint32_t frequency_mhz,
    void (*delay_cycles)(uint32_t cycles));
void open_cfw_touch_cat2_systick_service(open_cfw_touch_cat2_systick *state);
void open_cfw_touch_cat2_systick_enable(open_cfw_touch_cat2_systick *state);
void open_cfw_touch_cat2_systick_set_clock(
    open_cfw_touch_cat2_systick *state, uint32_t source);
int open_cfw_touch_cat2_systick_init(
    open_cfw_touch_cat2_systick *state, uint32_t source, uint32_t interval);
open_cfw_touch_cat2_void_fn open_cfw_touch_cat2_systick_set_callback(
    open_cfw_touch_cat2_systick *state, uint32_t number,
    open_cfw_touch_cat2_void_fn callback);
int open_cfw_touch_cat2_syspm_route(
    open_cfw_touch_cat2_syspm_fn provider, uint32_t type, void *context);
int open_cfw_touch_cat2_flash_write_row_route(
    open_cfw_touch_cat2_flash_write_fn provider, uint32_t row_address,
    const uint32_t *data, void *context);
int open_cfw_touch_cat2_gpio_pin_init_route(
    open_cfw_touch_cat2_gpio_pin_init_fn provider, void *base, uint32_t pin,
    const void *config, void *context);
int open_cfw_touch_cat2_i2c_slave_interrupt_route(
    open_cfw_touch_cat2_i2c_irq_fn provider, void *base, void *i2c_context,
    void *provider_context);
uint32_t open_cfw_touch_cat2_scb_read_route(
    open_cfw_touch_cat2_scb_read_fn provider, const void *base, void *buffer,
    uint32_t size, void *context);
uint32_t open_cfw_touch_cat2_scb_write_route(
    open_cfw_touch_cat2_scb_write_fn provider, void *base, const void *buffer,
    uint32_t data, uint32_t size, void *context);
int open_cfw_touch_cat2_scb_set_rx_level_route(
    open_cfw_touch_cat2_scb_level_fn provider, void *base, uint32_t level,
    void *context);
int open_cfw_touch_cat2_gpio_value_route(
    open_cfw_touch_cat2_gpio_value_fn provider, void *base, uint32_t pin,
    uint32_t value, void *context);
int open_cfw_touch_cat2_sysclk_route(
    open_cfw_touch_cat2_sysclk_fn provider, uint32_t operation,
    uint32_t argument0, uint32_t argument1, uint32_t *result, void *context);
int open_cfw_touch_cat2_msclp_route(
    open_cfw_touch_cat2_msclp_fn provider, void *base, const void *config,
    uint32_t key, void *context);
int open_cfw_touch_cat2_i2c_helper_route(
    open_cfw_touch_cat2_i2c_helper_fn provider, void *base, uint32_t flag,
    void *i2c_context, void *provider_context);
int open_cfw_touch_cat2_register_callback_route(
    open_cfw_touch_cat2_register_callback_fn provider, void *callback_record,
    void *context);
int open_cfw_touch_cat2_system_halt_route(
    open_cfw_touch_cat2_system_halt_fn provider, void *context);

#endif
